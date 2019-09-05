import json
import os
import re
import tempfile
import typing
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.base import View

from lib.converter_facade import fetch_remote_file, ConverterFacade, ConverterIo, ConverterIoType, ConversionFormat, \
    conversion_format_from_path
from .forms import UrlForm, FileForm
from .models import Conversion

CONVERSION_STORAGE_SUBDIR = 'conversions'
POST_CONVERT_FLAG = 'post_convert'


class ConversionFileStorage:
    root: str

    def __init__(self, root: str):
        self.root = root

    def generate_save_directory(self, public_id: str) -> str:
        if not re.match(r'^([a-z0-9_\-]{7,14})', public_id, re.I):
            raise ValueError('ID should not contain any bad characters.')

        return os.path.join(self.root, CONVERSION_STORAGE_SUBDIR, *list(public_id[:2]))

    def create_save_directory(self, public_id: str) -> None:
        os.makedirs(self.generate_save_directory(public_id), exist_ok=True)

    def generate_save_path(self, public_id, filename: typing.Optional[str] = None) -> str:
        filename = filename or public_id
        return os.path.join(self.generate_save_directory(public_id), filename)

    def move_file_to_public_id(self, source: str, public_id: str, filename: typing.Optional[str] = None) -> str:
        """
        Move a file to its permanent conversion results location.

        Encoda does the file writing itself to a temp file. After that is complete, this should be called to do the
        move. This is why the file has an `open` (read) but no `write` method.
        """
        self.create_save_directory(public_id)
        save_path = self.generate_save_path(public_id, filename)
        os.rename(source, save_path)
        return save_path


class OpenView(View):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        url_form = UrlForm()
        file_form = FileForm()

        if request.method == 'POST':
            mode = request.POST.get('mode')
            if mode in ('url', 'file'):
                source_io = None
                source_file = None
                target_file = None
                uploaded_filename = None

                conversion_kwargs = {}

                if mode == 'url':
                    url_form = UrlForm(request.POST)
                    if url_form.is_valid():
                        conversion_kwargs['input_url'] = url_form.cleaned_data['url']
                        source_io = fetch_remote_file(conversion_kwargs['input_url'],
                                                      settings.STENCILA_CLIENT_USER_AGENT)

                elif mode == 'file':
                    file_form = FileForm(request.POST, request.FILES)
                    if file_form.is_valid():
                        with tempfile.NamedTemporaryFile(delete=False) as source_file:
                            uploaded_file = request.FILES['file']
                            for chunk in uploaded_file.chunks():
                                source_file.write(chunk)

                        uploaded_filename = uploaded_file.name
                        source_io = ConverterIo(ConverterIoType.PATH, source_file.name,
                                                conversion_format_from_path(uploaded_filename))

                if source_io:
                    try:
                        with tempfile.NamedTemporaryFile(delete=False) as target_file:
                            target_io = ConverterIo(ConverterIoType.PATH, target_file.name, ConversionFormat.html)
                            converter = ConverterFacade(settings.STENCILA_BINARY)

                            conversion_result = converter.convert(source_io, target_io)

                        conversion = Conversion(**conversion_kwargs)

                        public_id = conversion.generate_or_get_public_id()

                        cfs = ConversionFileStorage(settings.STENCILA_PROJECT_STORAGE_DIRECTORY)

                        if conversion_result.returncode == 0:
                            conversion.output_file = cfs.move_file_to_public_id(target_file.name, public_id)
                        else:
                            # We can later find failed Conversions by those with null output_file
                            conversion.output_file = None

                        conversion.stderr = conversion_result.stderr.decode('utf8')
                        conversion.stdout = conversion_result.stdout.decode('utf8')

                        # It may have warnings even if the conversion went OK
                        conversion.has_warnings = conversion.stderr is not None and len(conversion.stderr) != 0

                        if (conversion.has_warnings or conversion_result.returncode != 0) and uploaded_filename:
                            # retain the uploaded file for later
                            conversion.input_file = cfs.move_file_to_public_id(source_io.data, public_id,
                                                                               uploaded_filename)

                        conversion.meta = json.dumps({
                            'user_agent': request.META.get('HTTP_USER_AGENT')
                        })
                        conversion.save()

                        return redirect(reverse('open_result', args=(public_id,)) + '?{}'.format(POST_CONVERT_FLAG))
                    finally:
                        if source_io:
                            try:
                                os.unlink(source_io.data)
                            except OSError:
                                pass

                        if source_file:
                            try:
                                os.unlink(source_file.name)
                            except OSError:
                                pass

                        if target_file:
                            try:
                                os.unlink(target_file.name)
                            except OSError:
                                pass

        return render(request, 'open/main.html', {'url_form': url_form, 'file_form': file_form})


class OpenResultView(View):
    def get(self, request: HttpRequest, conversion_id: str) -> HttpResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id)
        return render(request, 'open/output.html', {
            'raw_source': reverse('open_result_raw', args=(conversion.public_id,)),
            'is_post_convert': POST_CONVERT_FLAG in request.GET,
            'public_id': conversion.public_id
        })


class OpenResultRawView(View):
    """Fetches and displays just the raw HTML content with no Hub UI around the outside."""

    def get(self, request: HttpRequest, conversion_id: str) -> HttpResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id)
        with open(conversion.output_file, 'rb') as f:
            return HttpResponse(FileWrapper(f), content_type='text/html')

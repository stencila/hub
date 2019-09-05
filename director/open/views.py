import json
import os
import subprocess
import tempfile
import typing
from wsgiref.util import FileWrapper

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.base import View

from lib.converter_facade import fetch_remote_file, ConverterFacade, ConverterIo, ConverterIoType, ConversionFormat, \
    conversion_format_from_path, ConversionFormatError
from open.lib import ConversionFileStorage
from .forms import UrlForm, FileForm
from .models import Conversion

POST_CONVERT_FLAG = 'post_convert'


class ConversionRequest:
    source_io: typing.Optional[ConverterIo] = None
    invalid_source_format: bool = False
    input_url: typing.Optional[str] = None
    uploaded_filename: typing.Optional[str] = None
    source_file: typing.Optional[typing.Any] = None

    def source_format_valid(self) -> bool:
        if self.source_io is None:
            return False
        return self.source_io.conversion_format in (ConversionFormat.html, ConversionFormat.md)


class OpenView(View):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        url_form = UrlForm()
        file_form = FileForm()

        if request.method == 'POST':
            mode = request.POST.get('mode')
            if mode not in ('url', 'file'):
                raise ValueError('Unknown mode "{}"'.format(mode))

            if mode == 'url':
                url_form = UrlForm(request.POST)
                cr = self.get_url_conversion_request(url_form)
            else:
                file_form = FileForm(request.POST, request.FILES)
                cr = self.get_file_conversion_request(request, file_form)

            if cr.source_format_valid():
                target_file = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as target_file:
                        target_io = ConverterIo(ConverterIoType.PATH, target_file.name, ConversionFormat.html)
                        converter = ConverterFacade(settings.STENCILA_BINARY)

                        conversion_result = converter.convert(cr.source_io, target_io)

                    public_id = self.create_conversion(request, conversion_result, cr.input_url, cr.source_io,
                                                       target_file, cr.uploaded_filename)

                    return redirect(reverse('open_result', args=(public_id,)) + '?{}'.format(POST_CONVERT_FLAG))
                finally:
                    self.temp_file_cleanup(cr.source_io, cr.source_file, target_file)

            if not cr.source_format_valid():
                messages.error(request, 'Only conversion from HTML or Markdown is currently supported.')

        return render(request, 'open/main.html', {'url_form': url_form, 'file_form': file_form})

    @staticmethod
    def get_file_conversion_request(request: HttpRequest, file_form: FileForm) -> ConversionRequest:
        cr = ConversionRequest()
        if file_form.is_valid():
            uploaded_file = request.FILES['file']
            cr.uploaded_filename = uploaded_file.name
            try:
                input_format = conversion_format_from_path(cr.uploaded_filename)
            except ConversionFormatError:
                cr.invalid_source_format = True
            else:
                if cr.source_file:
                    with tempfile.NamedTemporaryFile(delete=False) as source_file:
                        for chunk in uploaded_file.chunks():
                            cr.source_file.write(chunk)

                    cr.source_io = ConverterIo(ConverterIoType.PATH, source_file.name, input_format)
        return cr

    @staticmethod
    def get_url_conversion_request(url_form: UrlForm) -> ConversionRequest:
        cr = ConversionRequest()
        if url_form.is_valid():
            cr.input_url = url_form.cleaned_data['url']
            try:
                cr.source_io = fetch_remote_file(cr.input_url, settings.STENCILA_CLIENT_USER_AGENT)
            except ConversionFormatError:
                cr.invalid_source_format = True
        return cr

    @staticmethod
    def create_conversion(request: HttpRequest, conversion_result: subprocess.CompletedProcess,
                          input_url: typing.Optional[str], source_io: ConverterIo,
                          target_file: typing.Optional[typing.Any],
                          uploaded_filename: typing.Optional[str]) -> str:
        conversion = Conversion(input_url=input_url)
        public_id = conversion.generate_or_get_public_id()
        conversion.stderr = conversion_result.stderr.decode('utf8')
        conversion.stdout = conversion_result.stdout.decode('utf8')
        # It may have warnings even if the conversion went OK
        conversion.has_warnings = conversion.stderr is not None and len(conversion.stderr) != 0
        cfs = ConversionFileStorage(settings.STENCILA_PROJECT_STORAGE_DIRECTORY)
        if conversion_result.returncode == 0 and target_file is not None:
            conversion.output_file = cfs.move_file_to_public_id(target_file.name, public_id)
        else:
            # We can later find failed Conversions by those with null output_file
            conversion.output_file = None
        if (conversion.has_warnings or conversion_result.returncode != 0) and uploaded_filename:
            # retain the uploaded file for later
            conversion.input_file = cfs.move_file_to_public_id(source_io.data, public_id,
                                                               uploaded_filename)
        conversion.meta = json.dumps({
            'user_agent': request.META.get('HTTP_USER_AGENT')
        })
        conversion.save()
        return public_id

    @staticmethod
    def temp_file_cleanup(source_io: typing.Optional[ConverterIo],
                          source_file: typing.Optional[typing.Any],
                          target_file: typing.Optional[typing.Any]) -> None:
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

import json
import logging
import os
import subprocess
import tempfile
import typing
from os.path import splitext, basename
from wsgiref.util import FileWrapper

import requests
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.base import View
from requests import HTTPError

from lib.converter_facade import fetch_remote_file, ConverterFacade, ConverterIo, ConverterIoType, ConversionFormatId, \
    conversion_format_from_path, ConversionFormatError
from open.lib import ConversionFileStorage
from .forms import UrlForm, FileForm, FeedbackForm
from .models import Conversion, ConversionFeedback

OWNED_CONVERSIONS_KEY = 'owned_conversions'

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class ConversionRequest:
    source_io: typing.Optional[ConverterIo] = None
    invalid_source_format: bool = False
    input_url: typing.Optional[str] = None
    source_file: typing.Optional[typing.Any] = None
    original_filename: typing.Optional[str] = None

    def source_format_valid(self) -> bool:
        if self.source_io is None:
            return False
        return self.source_io.conversion_format in (ConversionFormatId.html, ConversionFormatId.md)


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
                        target_io = ConverterIo(ConverterIoType.PATH, target_file.name, ConversionFormatId.html)
                        converter = ConverterFacade(settings.STENCILA_BINARY)

                        conversion_result = converter.convert(cr.source_io, target_io, True)

                    public_id = self.create_conversion(request, conversion_result, cr.input_url, cr.source_io,
                                                       target_io, target_file, cr.original_filename)

                    # Add the ownership of this conversion to the session
                    if OWNED_CONVERSIONS_KEY not in request.session:
                        request.session[OWNED_CONVERSIONS_KEY] = []
                    request.session[OWNED_CONVERSIONS_KEY].append(public_id)
                    # modified flag needs to be set manually since an object inside session is being manipulated
                    request.session.modified = True

                    return redirect('open_result', public_id)
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
            cr.original_filename = uploaded_file.name
            try:
                input_format = conversion_format_from_path(cr.original_filename)
            except ConversionFormatError:
                cr.invalid_source_format = True
            else:
                with tempfile.NamedTemporaryFile(delete=False) as source_file:
                    for chunk in uploaded_file.chunks():
                        source_file.write(chunk)
                cr.source_file = source_file
                cr.source_io = ConverterIo(ConverterIoType.PATH, source_file.name, input_format)
        return cr

    @staticmethod
    def get_url_conversion_request(url_form: UrlForm) -> ConversionRequest:
        cr = ConversionRequest()
        if url_form.is_valid():
            cr.input_url = url_form.cleaned_data['url']
            try:
                file_name, source_io = fetch_remote_file(cr.input_url, settings.STENCILA_CLIENT_USER_AGENT)
                cr.source_io = source_io
                cr.original_filename = file_name
            except ConversionFormatError:
                cr.invalid_source_format = True
        return cr

    @staticmethod
    def create_conversion(request: HttpRequest, conversion_result: subprocess.CompletedProcess,
                          input_url: typing.Optional[str], source_io: ConverterIo, target_io: ConverterIo,
                          target_file: typing.Optional[typing.Any],
                          original_filename: typing.Optional[str]) -> str:
        conversion = Conversion(input_url=input_url)
        public_id = conversion.generate_or_get_public_id()

        conversion.source_format = source_io.conversion_format.value.format_id
        conversion.target_format = target_io.conversion_format.value.format_id

        conversion.stderr = conversion_result.stderr.decode('utf8')
        conversion.stdout = conversion_result.stdout.decode('utf8')

        conversion.original_filename = original_filename
        # It may have warnings even if the conversion went OK
        conversion.has_warnings = conversion.stderr is not None and len(conversion.stderr) != 0
        cfs = ConversionFileStorage(settings.STENCILA_PROJECT_STORAGE_DIRECTORY)
        if conversion_result.returncode == 0 and target_file is not None:
            conversion.output_file = cfs.move_file_to_public_id(target_file.name, public_id)

            intermediary_input_path = target_file.name + '.json'
            intermediary_output_path = basename(conversion.output_file) + '.json'

            cfs.move_file_to_public_id(intermediary_input_path, public_id, basename(intermediary_output_path))
        else:
            # We can later find failed Conversions by those with null output_file
            conversion.output_file = None
        if (conversion.has_warnings or conversion_result.returncode != 0) and original_filename:
            # retain the uploaded file for later
            conversion.input_file = cfs.move_file_to_public_id(source_io.data, public_id,
                                                               original_filename)
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


class LogMessage:
    message: dict

    def __init__(self, message: dict) -> None:
        self.message = message

    def level_to_name(self) -> str:
        return ['ERROR', 'WARN', 'INFO', 'DEBUG'][self.message['level']]

    def __getitem__(self, item: typing.Any) -> typing.Any:
        return self.message[item]


def user_owns_conversion(request: HttpRequest, conversion_id: str) -> bool:
    if OWNED_CONVERSIONS_KEY not in request.session:
        return False

    return conversion_id in request.session[OWNED_CONVERSIONS_KEY]


class ConversionDownloadOption(typing.NamedTuple):
    name: str
    format_id: str
    icon_class: str


CONVERSION_DOWNLOAD_OPTIONS = [
    ConversionDownloadOption('Word (.docx)', 'docx', 'far fa-file-word'),
    None,
    ConversionDownloadOption('JATS (.xml)', 'jats', 'far fa-file-code'),
    # ConversionDownloadOption('PDF', 'pdf', 'far fa-file-pdf'),
    ConversionDownloadOption('Web page', 'html', 'far fa-file-code'),
    # None,
    # ConversionDownloadOption('RMarkdown (.rmd)', 'rmd', 'far fa-file-code'),
    # ConversionDownloadOption('Jupyter Notebook (.ipynb)', 'ipynb', 'far fa-book'),
]


class OpenResultView(View):
    def get(self, request: HttpRequest, conversion_id: str) -> HttpResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id, is_deleted=False)

        conversion_owned = user_owns_conversion(request, conversion_id)
        context = {
            'user_owns_conversion': conversion_owned,
            'public_id': conversion.public_id
        }

        if conversion_owned and conversion.stderr:
            # log messages are line separated JSON directories
            raw_log_messages = json.loads('[' + ','.join(conversion.stderr.strip().split('\n')) + ']')
            log_messages: typing.Optional[typing.List[LogMessage]] = list(map(LogMessage, raw_log_messages))
        else:
            log_messages = None

        context['log_messages'] = log_messages
        context['display_warings_button'] = conversion_owned and log_messages is not None

        if conversion.output_file is None:
            template = 'open/error.html'
            context['conversion_success'] = False
        else:
            template = 'open/output.html'
            context['conversion_success'] = True
            context['download_options'] = CONVERSION_DOWNLOAD_OPTIONS
            context['share_url'] = request.build_absolute_uri()
            context['raw_source'] = reverse('open_result_raw', args=(conversion.public_id,))

        return render(request, template, context)


class OpenResultRawView(View):
    """Fetches and displays just the raw HTML content with no Hub UI around the outside."""

    def get(self, request: HttpRequest, conversion_id: str) -> HttpResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id, is_deleted=False)
        if conversion.output_file is None:
            return render(request, 'open/error.html', {})

        if 'download' in request.GET:
            return self.send_download(request.GET['download'], conversion)

        with open(conversion.output_file, 'rb') as f:
            return HttpResponse(FileWrapper(f), content_type='text/html')

    @staticmethod
    def send_download(format_name: str, conversion: Conversion) -> HttpResponse:
        json_representation_path = conversion.output_file + '.json'

        source_io = ConverterIo(ConverterIoType.PATH, json_representation_path, ConversionFormatId.json)

        with tempfile.NamedTemporaryFile() as target_file:
            target_io = ConverterIo(ConverterIoType.PATH, target_file.name, ConversionFormatId.from_id(format_name))

            converter = ConverterFacade(settings.STENCILA_BINARY)
            converter.convert(source_io, target_io)

            resp = HttpResponse(FileWrapper(target_file), content_type=target_io.conversion_format.value.mimetypes[0])
            if conversion.original_filename:
                original_filename, _ = splitext(conversion.original_filename)
                output_filename = '{}.{}'.format(original_filename, target_io.conversion_format.value.format_id)
            else:
                output_filename = 'stencila-open-download.{}'.format(target_io.conversion_format.value.format_id)

            resp['Content-Disposition'] = 'attachment; filename="{}"'.format(output_filename)
            return resp


def upsert_intercom_user(email_address: str) -> None:
    """Create or update an Intercom user with a flag that they have added Conversion feedback."""
    if settings.DEBUG:
        LOGGER.debug('In debug mode so not sending %s to intercom', email_address)
        return

    resp = requests.post('https://api.intercom.io/users', json={
        'email': email_address,
        'custom_attributes': {
            'open_feedback': True
        }
    }, headers={
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(settings.INTERCOM_ACCESS_TOKEN)
    })

    try:
        resp.raise_for_status()
    except HTTPError:
        LOGGER.exception('Adding conversion feedback user to Intercom')


class OpenFeedbackView(View):
    def post(self, request: HttpRequest, conversion_id: str) -> HttpResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id, is_deleted=False)

        if not user_owns_conversion(request, conversion_id):
            raise PermissionDenied('You do not own this conversion.')

        feedback_form = FeedbackForm(request.POST)

        resp: typing.Dict[typing.Any, typing.Any] = {}

        if feedback_form.is_valid():
            ConversionFeedback.objects.create(conversion=conversion, **feedback_form.cleaned_data)

            if feedback_form.cleaned_data['email_address']:
                upsert_intercom_user(feedback_form.cleaned_data['email_address'])

            resp['success'] = True
        else:
            resp['success'] = False
            resp['errors'] = dict(feedback_form.errors.items())

        return JsonResponse(resp)

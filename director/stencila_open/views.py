import json
import logging
import os
import shutil
import subprocess
import tempfile
import typing
import uuid
from os.path import splitext, basename, dirname

import requests
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from requests import HTTPError

from lib.conversion_types import ConversionFormatId, conversion_format_from_path, ConversionFormatError
from lib.converter_facade import fetch_url, ConverterFacade, ConverterIo, ConverterIoType, \
    ConverterContext, GoogleDocs403Exception, download_for_conversion
from lib.sparkla import generate_manifest
from projects.source_operations import path_is_in_directory
from stencila_open.lib import ConversionFileStorage
from .forms import UrlForm, FileForm, FeedbackForm
from .models import Conversion, ConversionFeedback

OWNED_CONVERSIONS_KEY = 'owned_conversions'
SAVE_EXAMPLE_KEY = 'stencila_example'

OUTPUT_FORMAT = ConversionFormatId.html
OUTPUT_FILENAME = 'output.html'

INTERMEDIARY_FILENAME = 'output.json'

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
        return self.source_io.conversion_format in (
            ConversionFormatId.html,
            ConversionFormatId.md,
            ConversionFormatId.ipynb,
            ConversionFormatId.docx,
            ConversionFormatId.gdoc,
            ConversionFormatId.rmd,
            ConversionFormatId.rnb
        )


class ConversionExample(typing.NamedTuple):
    tagline: str
    url: str
    icon_class: str


class OpenView(View):
    def dispatch(self, request: HttpRequest, url: typing.Optional[str] = None) -> HttpResponse:
        if request.META.get('HTTP_USER_AGENT') == settings.STENCILA_CLIENT_USER_AGENT:
            return HttpResponse('<h1>Generic Hub Conversion Output 🗿🥚</h1>', content_type='text/html;charset=utf-8')

        url_form = UrlForm()
        file_form = FileForm()
        save_example = False

        if request.method == 'POST' or url:
            if request.method == 'POST':
                mode = request.POST.get('mode')
            elif url:
                mode = 'url'

                # If passing a URL with a query string, it won't be part of `url`, Django will parse it into request.GET
                # This will re-add it to the URL after removing our SAVE flag
                if SAVE_EXAMPLE_KEY in request.GET:
                    get_params = request.GET.copy()
                    del get_params[SAVE_EXAMPLE_KEY]
                    save_example = (not request.user.is_anonymous) and request.user.is_staff
                else:
                    get_params = request.GET

                if get_params:
                    # this should be safe as and ? will be consumed already
                    url += '?' + get_params.urlencode()

                if not save_example:
                    # check for an example conversion for this to use already
                    example_conversion = self.get_example_conversion(url)  # type: ignore # url != None is checked above
                    if example_conversion:
                        return redirect('open_result', example_conversion.public_id)
            else:
                mode = ''

            if mode not in ('url', 'file'):
                raise ValueError('Unknown mode "{}"'.format(mode))

            cr: typing.Optional[ConversionRequest] = None

            if mode == 'url':
                if request.method == 'POST':
                    form_data = request.POST
                else:
                    form_data = {'url': url}
                url_form = UrlForm(form_data)
                try:
                    cr = self.get_url_conversion_request(url_form)
                except GoogleDocs403Exception:
                    messages.error(request, 'Could not retrieve the Google Doc because it isn\'t publicly viewable.'
                                            'Please make sure link sharing is set to "Public on the web" or '
                                            '"Anyone with the link" for the Google Doc.<br>For more information, see: '
                                            '<a href="https://support.google.com/drive/answer/2494822#link_sharing">'
                                            'https://support.google.com/drive/answer/2494822#link_sharing</a>',
                                   extra_tags='safe')
                except HTTPError as e:
                    if e.response.status_code == 404:
                        messages.error(request, 'Unable to fetch from {} as the file doesn\'t exist.'.format(
                            url_form.cleaned_data['url']))
                    else:
                        messages.error(request, 'Unable to fetch from {} (response status: {}).'.format(
                            url_form.cleaned_data['url'], e.response.status_code))
                except OSError:
                    messages.error(request, 'Unable to fetch from {}, please check the URL is valid.'.format(
                        url_form.cleaned_data['url']))
                except Exception:
                    messages.error(request, 'Unable to fetch from {}, an unknown error occurred.'.format(
                        url_form.cleaned_data['url']))

            else:
                file_form = FileForm(request.POST, request.FILES)
                cr = self.get_file_conversion_request(request, file_form)

            if cr and cr.source_format_valid():
                assert cr.source_io is not None
                # mostly to keep mypy happy, the None check is done in source_format_valid call above

                target_file = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as target_file:
                        target_io = ConverterIo(ConverterIoType.PATH, target_file.name, OUTPUT_FORMAT)
                        converter = ConverterFacade(settings.STENCILA_BINARY)

                        conversion_result = converter.convert(cr.source_io, target_io, ConverterContext(True, False))

                    public_id = self.create_conversion(request, conversion_result, cr.input_url, cr.source_io,
                                                       target_io, target_file, cr.original_filename, save_example)

                    # Add the ownership of this conversion to the session
                    if OWNED_CONVERSIONS_KEY not in request.session:
                        request.session[OWNED_CONVERSIONS_KEY] = []
                    request.session[OWNED_CONVERSIONS_KEY].append(public_id)
                    # modified flag needs to be set manually since an object inside session is being manipulated
                    request.session.modified = True

                    return redirect('open_preview', public_id)
                finally:
                    self.temp_file_cleanup(cr.source_io, cr.source_file, target_file)

            if cr and not cr.source_format_valid():
                messages.error(request, 'Only conversion from HTML, Markdown, Word (.docx), Jupyter Notebook, Google '
                                        'Docs, R Markdown or Rstudio is currently supported.')

        conversion_examples = [
            ConversionExample('Jupyter Notebook <br> hosted on Github',
                              'https://github.com/stencila/examples/tree/master/jupyter/jupyter.ipynb',
                              'fab fa-github'),

            ConversionExample('Markdown file <br> on Hackmd.io',
                              'https://hackmd.io/RaFYCFoyTlODFxz5hPevLw',
                              'fas fa-file-code'),

            ConversionExample('R Notebook <br> hosted on Github',
                              'https://github.com/stencila/examples/tree/master/rmarkdown/rmarkdown.nb.html',
                              'fab fa-github'),

            ConversionExample('Article written in <br> Google Docs',
                              'https://docs.google.com/document/d/1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA',
                              'fab fa-google'),
        ]

        return render(request, 'open/main.html',
                      {'url_form': url_form, 'file_form': file_form, 'conversion_examples': conversion_examples})

    @staticmethod
    def get_example_conversion(url: str) -> typing.Optional[Conversion]:
        """Attempt to find an example Conversion for a url request."""
        try:
            return Conversion.objects.get(input_url=url, is_example=True)
        except Conversion.DoesNotExist:
            return None

    @staticmethod
    def get_file_conversion_request(request: HttpRequest, file_form: FileForm) -> ConversionRequest:
        cr = ConversionRequest()
        if file_form.is_valid():
            uploaded_file = request.FILES['file']
            cr.original_filename = uploaded_file.name

            if cr.original_filename is None:
                raise ValueError('Invalid file: uploaded without a name.')

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
            cr.input_url = typing.cast(str, url_form.cleaned_data['url'])  # safe to do because the form is valid
            try:
                file_name, source_io = fetch_url(cr.input_url, download_for_conversion,
                                                 settings.STENCILA_CLIENT_USER_AGENT)
                cr.source_io = source_io
                cr.original_filename = file_name
            except ConversionFormatError:
                cr.invalid_source_format = True
        return cr

    def create_conversion(self, request: HttpRequest, conversion_result: subprocess.CompletedProcess,
                          input_url: typing.Optional[str], source_io: ConverterIo, target_io: ConverterIo,
                          target_file: typing.Optional[typing.Any],
                          original_filename: typing.Optional[str], save_example: bool) -> str:

        conversion = None
        if save_example and input_url:
            conversion = self.get_example_conversion(input_url)

        if not conversion:
            conversion = Conversion(input_url=input_url, is_example=save_example)

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
            conversion.output_file = cfs.copy_file_to_public_id(target_file.name, public_id, OUTPUT_FILENAME)

            # copy the media directory if it exists
            media_path = target_file.name + '.media'
            if os.path.exists(media_path):
                cfs.copy_file_to_public_id(media_path, public_id, basename(media_path))

            intermediary_input_path = target_file.name + '.json'

            cfs.copy_file_to_public_id(intermediary_input_path, public_id, INTERMEDIARY_FILENAME)
        else:
            # We can later find failed Conversions by those with null output_file
            conversion.output_file = None
        if (conversion.has_warnings or conversion_result.returncode != 0) and original_filename:
            # retain the uploaded file for later
            if not isinstance(source_io.data, str):
                raise TypeError('Source Data does not appear to be a path')
            conversion.input_file = cfs.copy_file_to_public_id(source_io.data, public_id,
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
                if isinstance(source_io.data, str):
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
    ConversionDownloadOption('Reproducible Word (.docx)', ConversionFormatId.docx.value.format_id, 'far fa-file-word'),
    None,
    ConversionDownloadOption('Jupyter Notebook (.ipynb)', ConversionFormatId.ipynb.value.format_id, 'fas fa-book'),
    ConversionDownloadOption('R Markdown (.Rmd)', ConversionFormatId.rmd.value.format_id, 'far fa-file-code'),
    None,
    ConversionDownloadOption('JATS (.xml)', ConversionFormatId.jats.value.format_id, 'far fa-file-code'),
    ConversionDownloadOption('JSON-Linked Data (.jsonld)', ConversionFormatId.jsonld.value.format_id,
                             'far fa-file-code'),
    ConversionDownloadOption('Semantic HTML', ConversionFormatId.html.value.format_id, 'far fa-file-code'),
    # ConversionDownloadOption('PDF', 'pdf', 'far fa-file-pdf'),
]


class ConversionTheme(typing.NamedTuple):
    theme_id: str
    name: str


THEMES = [
    ConversionTheme('stencila', 'Stencila'),
    ConversionTheme('eLife', 'eLife'),
    ConversionTheme('nature', 'Nature'),
    ConversionTheme('plos', 'PLOS')
]


class FileDownloadCleanup:
    path: str

    def __init__(self, path: str) -> None:
        self.path = path

    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            os.remove(self.path)
        except OSError:
            pass


class OpenConversionView(View):
    @staticmethod
    def get_log_messages(conversion: Conversion, conversion_owned: bool) -> \
            typing.Optional[typing.List[LogMessage]]:
        if conversion_owned and conversion.stderr:
            # log messages are line separated JSON directories
            raw_log_messages = json.loads('[' + ','.join(conversion.stderr.strip().split('\n')) + ']')
            return list(map(LogMessage, raw_log_messages))
        else:
            return None

    def get_error_response(self, request, context, conversion, conversion_owned):
        context['conversion_success'] = False
        context['log_messages'] = self.get_log_messages(conversion, conversion_owned)
        context['display_warnings_button'] = conversion_owned and context['log_messages'] is not None
        context['filename'] = conversion.original_filename
        return render(request, 'open/error.html', context)


class OpenPreviewView(OpenConversionView):
    def get(self, request: HttpRequest, conversion_id: str) -> HttpResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id, is_deleted=False)

        conversion_owned = user_owns_conversion(request, conversion_id)
        context = {
            'user_owns_conversion': conversion_owned,
            'public_id': conversion.public_id
        }

        if conversion.output_file is None:
            return self.get_error_response(request, context, conversion, conversion_owned)

        context['conversion_success'] = True
        context['download_options'] = CONVERSION_DOWNLOAD_OPTIONS
        context['share_url'] = request.build_absolute_uri()
        context['raw_source'] = reverse('open_result_raw', args=(conversion.public_id,))
        context['absolute_raw_url'] = request.build_absolute_uri(context['raw_source'])

        return render(request, 'open/output_intermediary.html', context)


class OpenDisplayView(OpenConversionView):
    def get(self, request: HttpRequest, conversion_id: str) -> HttpResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id, is_deleted=False)
        conversion_owned = user_owns_conversion(request, conversion_id)
        context = {
            'user_owns_conversion': conversion_owned,
            'public_id': conversion.public_id
        }

        if conversion.output_file is None:
            return self.get_error_response(request, context, conversion, conversion_owned)

        context['conversion_success'] = True
        context['log_messages'] = self.get_log_messages(conversion, conversion_owned)
        context['download_options'] = CONVERSION_DOWNLOAD_OPTIONS
        context['share_url'] = request.build_absolute_uri()
        context['raw_source'] = reverse('open_result_raw', args=(conversion.public_id,))
        context['absolute_raw_url'] = request.build_absolute_uri(context['raw_source'])
        context['themes'] = THEMES
        context['current_theme'] = request.GET.get('theme')

        return render(request, 'open/output.html', context)


class OpenMediaView(View):
    def get(self, request: HttpRequest, conversion_id: str, media_dir_id: str, filename: str) -> FileResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id, is_deleted=False)

        conversion_dir = dirname(conversion.output_file)
        media_dir = os.path.join(conversion_dir, '{}.media'.format(media_dir_id))
        file_path = os.path.join(media_dir, filename)

        if not path_is_in_directory(file_path, conversion_dir):
            raise PermissionDenied('Media file is not inside conversion directory.')

        if not os.path.exists(file_path):
            raise Http404

        return FileResponse(open(file_path, 'rb'))


class OpenResultRawView(View):
    """Fetches and displays just the raw HTML content with no Hub UI around the outside."""

    def get(self, request: HttpRequest, conversion_id: str) -> FileResponse:
        conversion = get_object_or_404(Conversion, public_id=conversion_id, is_deleted=False)
        if conversion.output_file is None:
            return render(request, 'open/error.html', {
                'filename': conversion.original_filename
            })

        if 'download' in request.GET:
            return self.send_download(request.GET['download'], conversion)

        resp = FileResponse(open(conversion.output_file, 'rb'))
        # this needs to be set here instead of content_type kwarg as it gets overwritten since it matches the default
        # content type from settings
        resp['Content-Type'] = 'text/html'
        return resp

    @staticmethod
    def send_download(format_name: str, conversion: Conversion) -> FileResponse:
        for format_option in CONVERSION_DOWNLOAD_OPTIONS:
            if format_option is None:
                continue
            if format_option.format_id == format_name:
                break
        else:
            raise TypeError('{} is not a valid format'.format(format_name))

        conversion_dir = dirname(conversion.output_file)

        # Should be output to its own directory to prevent conflicts with the original HTML file
        output_directory = os.path.join(conversion_dir, 'downloads')
        os.makedirs(output_directory, exist_ok=True)

        json_representation_path = os.path.join(conversion_dir, INTERMEDIARY_FILENAME)

        source_io = ConverterIo(ConverterIoType.PATH, json_representation_path, ConversionFormatId.json)

        output_format = ConversionFormatId.from_id(format_name)

        # Use specified extension (e.g. for jats.xml) or fall back to format_id)
        extension = output_format.value.output_extension or output_format.value.format_id

        if conversion.original_filename:
            original_filename, _ = splitext(conversion.original_filename)
            output_filename = '{}.{}'.format(original_filename, extension)
        else:
            output_filename = 'stencila-open-conversion.{}'.format(extension)

        output_path = os.path.join(output_directory, output_filename)

        target_io = ConverterIo(ConverterIoType.PATH, output_path, output_format)

        converter = ConverterFacade(settings.STENCILA_BINARY)
        conversion_result = converter.convert(source_io, target_io, ConverterContext(False, True))

        if conversion_result.returncode != 0:
            raise RuntimeError('Conversion was not successful: {}'.format(str(conversion_result.stderr)))

        media_path = output_path + '.media'
        if os.path.exists(media_path):
            shutil.rmtree(media_path)

        output_zip_path = os.path.splitext(output_path)[0] + '.zip'

        if os.path.exists(output_zip_path):
            output_path = output_zip_path
            output_filename = basename(output_zip_path)
            output_mimetype = 'application/zip'
        else:
            output_mimetype = output_format.value.mimetypes[0]

        resp = FileResponse(open(output_path, 'rb'), as_attachment=True, filename=output_filename)

        # set here instead of as kwarg above because it can get overwritten if it's text/html
        resp['Content-Type'] = output_mimetype
        with FileDownloadCleanup(output_path):
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


def get_request_user_id(request: HttpRequest) -> str:
    if request.user.is_anonymous:
        if 'OPEN_USER' not in request.session:
            request.session['OPEN_USER'] = str(uuid.uuid4())
        return request.session['OPEN_USER']

    return '{}'.format(request.user.id)


@method_decorator(csrf_exempt, name='dispatch')
class OpenManifestView(View):
    def post(self, request: HttpRequest, conversion_id: str) -> HttpResponse:
        if request.user.is_anonymous or not request.user.is_staff:
            raise PermissionDenied

        conversion = get_object_or_404(Conversion, public_id=conversion_id, is_deleted=False)

        manifest = generate_manifest(get_request_user_id(request), project_id_override=conversion.pk)

        return JsonResponse(manifest)

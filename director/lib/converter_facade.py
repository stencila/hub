import datetime
import enum
import ipaddress
import mimetypes
import os
import subprocess
import tempfile
import typing
from os.path import splitext, basename
from socket import gethostbyname
from urllib.parse import urlparse, urljoin

import requests
from django.http.multipartparser import parse_header

MAX_REMOTE_CONVERT_SIZE = 5 * 1024 * 1024
STREAM_CHUNK_SIZE = 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 30
MAX_DOWNLOAD_TIME_SECONDS = 60
MAX_HTTP_REDIRECTS = 10

DOCX_MIMETYPES = ('application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
                  'application/vnd.ms-word.document.macroEnabled.12',
                  'application/vnd.ms-word.template.macroEnabled.12')


class ConverterIoType(enum.Enum):
    PIPE = enum.auto()
    PATH = enum.auto()


class ConversionFormat(typing.NamedTuple):
    format_id: str
    mimetypes: typing.Iterable[str]


class ConversionFormatId(enum.Enum):
    """
    List of formats we know how to work with.

    To add support for a conversion format:
    - Add it to the list below
    - Add a conversion for its mimetype to the `conversion_format_from_mimetype` function below
    - Check that its mimetype can be retrieved from its path using the `mimetype_from_path` function below (add support
      manually if necessary).
    """

    docx = ConversionFormat('docx', DOCX_MIMETYPES)
    gdoc = ConversionFormat('gdoc', ['application/vnd.google-apps.document'])
    html = ConversionFormat('html', ['text/html'])
    ipynb = ConversionFormat('ipynb', ['application/x-ipynb+jso'])
    jats = ConversionFormat('jats', ['text/xml+jats'])
    json = ConversionFormat('json', ['application/json'])
    md = ConversionFormat('md', ['text/markdown'])
    rmd = ConversionFormat('rmd', ['text/rmarkdown'])
    xml = ConversionFormat('xml', ['application/xml'])

    @classmethod
    def from_id(cls, format_id: str) -> 'ConversionFormatId':
        for f in cls:
            if f.value.format_id == format_id:
                return f

        raise ValueError('No such member with id {}'.format(format_id))

    @classmethod
    def from_mimetype(cls, mimetype: str) -> 'ConversionFormatId':
        for f in cls:
            if mimetype in f.value.mimetypes:
                return f

        raise ValueError('No such member with mimetype {}'.format(mimetype))


def mimetype_from_path(path: str) -> typing.Optional[str]:
    """
    Get the mimetype of a file from its path.

    Takes the path instead of extension because some formats (e.g. JATS) have two extensions.
    """
    if path.lower().endswith('.jats.xml'):
        return 'text/xml+jats'

    mimetype, encoding = mimetypes.guess_type(path, False)

    if not mimetype:
        name, ext = splitext(path)
        ext = ext.lower()

        if ext == '.md':
            return 'text/markdown'

        if ext == '.rmd':
            return 'text/rmarkdown'

        if ext == '.ipynb':
            return 'application/x-ipynb+json'

        if ext == '.docx':
            return DOCX_MIMETYPES[0]

    return mimetype


def conversion_format_from_mimetype(mimetype: str) -> ConversionFormatId:
    try:
        return ConversionFormatId.from_mimetype(mimetype)
    except ValueError:
        raise ConversionFormatError('Unable to create ConversionFormatId from {}'.format(mimetype))


def conversion_format_from_path(path: str) -> ConversionFormatId:
    mimetype = mimetype_from_path(path)

    if not mimetype:
        raise ValueError('MIME type could not be determined for path: {}'.format(mimetype))
    return conversion_format_from_mimetype(mimetype)


class ConverterIo(typing.NamedTuple):
    io_type: ConverterIoType
    # data is either data to be converted (io_type == PIPE) or the path to the file to be converted (io_type == PATH)
    data: typing.Union[None, str, bytes]
    conversion_format: ConversionFormatId

    @property
    def as_path_shell_arg(self) -> str:
        if self.io_type == ConverterIoType.PIPE:
            return '-'  # placeholder for STDIN/STDOUT

        return str(self.data)


class RemoteFileException(Exception):
    pass


class ConversionFormatError(Exception):
    pass


def is_malicious_host(hostname: str) -> bool:
    """Detect if user is trying to do things like connect to localhost or a local IP address of some kind."""
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        return True  # Trying to access a site by IP

    address = gethostbyname(hostname)
    ip = ipaddress.ip_address(address)
    return ip.is_loopback or ip.is_private


def fetch_remote_file(url: str, user_agent: typing.Optional[str] = None,
                      seen_urls: typing.Optional[typing.List[str]] = None) -> typing.Tuple[str, ConverterIo]:
    """
    Download a remote file to a tmp location, then generate a `ConverterIO`.

    The conversion_format wil try to be determined from the response mimetype then a fallback to file extensions.
    """
    headers = {'User-Agent': user_agent} if user_agent else None

    url_obj = urlparse(url)

    if is_malicious_host(url_obj.hostname):
        raise RemoteFileException('{} is not a valid host name.'.format(url_obj.hostname))

    _, file_ext = splitext(url_obj.path)

    if seen_urls is None:
        seen_urls = []

    with requests.get(url,
                      headers=headers,
                      stream=True,
                      timeout=DOWNLOAD_TIMEOUT_SECONDS,
                      allow_redirects=False) as resp:
        if 'Location' in resp.headers:
            # Manually follow redirects to determine if it is a redirect to a malicious URL
            if url in seen_urls:
                raise RemoteFileException('Looping redirect found at {}'.format(url))
            seen_urls.append(url)

            if len(seen_urls) > MAX_HTTP_REDIRECTS:
                raise RemoteFileException('Too many HTTP redirects from original URL: {}'.format(seen_urls[0]))

            new_url = urljoin(url, resp.headers['location'])
            return fetch_remote_file(new_url, user_agent, seen_urls)

        download_start_time = datetime.datetime.now()
        resp.raise_for_status()
        downloaded_bytes = 0
        if 'Content-Length' in resp.headers:
            try:
                content_length = int(resp.headers['Content-Length'])
                if content_length > MAX_REMOTE_CONVERT_SIZE:
                    raise RemoteFileException('Not fetching remote file as it exceeds the maximum size for conversion.')
            except ValueError:
                pass

        mimetype = resp.headers.get('Content-Type')
        if mimetype:
            mimetype = mimetype.split(';')[0]

        source_format = None

        if mimetype:
            try:
                source_format = conversion_format_from_mimetype(mimetype)
            except ConversionFormatError:
                pass  # Fall back to extension, in cases where HTTP server send back 'text/plain' for MD, for example

        file_name = basename(url_obj.path)

        if 'Content-Disposition' in resp.headers:
            _, metadata = parse_header(resp.headers['Content-Disposition'])
            file_name = metadata.get('filename')

        if not source_format:
            try:
                source_format = conversion_format_from_path(file_name)
            except ValueError:
                raise ConversionFormatError(
                    'Unable to determine conversion format from mimetype "{}" or path "".'.format(mimetype,
                                                                                                  url_obj.path))

        with tempfile.NamedTemporaryFile(delete=False) as download_to:
            try:
                for chunk in resp.iter_content(chunk_size=STREAM_CHUNK_SIZE):
                    download_seconds = datetime.datetime.now() - download_start_time
                    if download_seconds.total_seconds() > MAX_DOWNLOAD_TIME_SECONDS:
                        raise RemoteFileException(
                            'Time for download took more than {} seconds ({})'.format(MAX_DOWNLOAD_TIME_SECONDS,
                                                                                      download_seconds))

                    if not chunk:
                        continue

                    downloaded_bytes += len(chunk)

                    if downloaded_bytes > MAX_REMOTE_CONVERT_SIZE:
                        raise RemoteFileException('Remote file exceeded size limit while streaming.')

                    download_to.write(chunk)
            except Exception:
                os.unlink(download_to.name)
                raise

        return file_name, ConverterIo(ConverterIoType.PATH, download_to.name, source_format)


class ConverterFacade(object):
    converter_binary: typing.List[str]

    def __init__(self, converter_binary: typing.List[str]) -> None:
        self.converter_binary = converter_binary

    def convert(self, input_data: ConverterIo, output_data: ConverterIo,
                output_intermediary: bool = False) -> subprocess.CompletedProcess:
        convert_args: typing.List[str] = [
            'convert',
            '--from', input_data.conversion_format.value.format_id,
            '--to', output_data.conversion_format.value.format_id,
            input_data.as_path_shell_arg, output_data.as_path_shell_arg]

        if output_intermediary:
            if output_data.as_path_shell_arg == '-':
                raise RuntimeError('Can\'t output the intermediary when sending output to STDOUT')

            convert_args.append(output_data.as_path_shell_arg + '.json')

        input_pipe_data = input_data.data if input_data.io_type == ConverterIoType.PIPE else None

        return subprocess.run(self.converter_binary + convert_args, input=input_pipe_data, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

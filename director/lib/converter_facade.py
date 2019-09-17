import datetime
import enum
import ipaddress
import json
import os
import re
import subprocess
import tempfile
import typing
from os.path import splitext, basename
from socket import gethostbyname
from urllib.parse import urlparse, urljoin, unquote

import requests
from allauth.socialaccount.models import SocialApp
from django.http.multipartparser import parse_header

from lib.conversion_types import ConversionFormatId, conversion_format_from_mimetype, conversion_format_from_path, \
    ConversionFormatError
from lib.google_docs_facade import extract_google_document_id_from_url, GoogleDocsFacade

MAX_REMOTE_CONVERT_SIZE = 5 * 1024 * 1024
STREAM_CHUNK_SIZE = 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 30
MAX_DOWNLOAD_TIME_SECONDS = 60
MAX_HTTP_REDIRECTS = 10


class ConverterIoType(enum.Enum):
    PIPE = enum.auto()
    PATH = enum.auto()


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


def convert_raw_content_url(url: str) -> str:
    """
    Get URL to raw content from one that has website chrome around it.

    For providers like Github that have a URL you would navigate to that is not the raw content, convert the URL to be
    that of the raw content.
    """
    github_match = re.search(r'^https://github.com/([a-z0-9\-]+)/([a-z0-9\-_]+)/blob/(.*)', url, re.I)

    if github_match:
        return 'https://raw.githubusercontent.com/{}/{}/{}'.format(github_match.group(1),
                                                                   github_match.group(2),
                                                                   github_match.group(3))

    return url


class ServiceId(enum.Enum):
    google_docs = enum.auto()


class ServiceItem(typing.NamedTuple):
    service_id: ServiceId
    item_id: str


def fetch_google_docs_content(service_item: ServiceItem) -> typing.Tuple[str, ConverterIo]:
    google_app = SocialApp.objects.filter(provider='google').first()

    gdf = GoogleDocsFacade(google_app.client_id, google_app.secret)
    document = gdf.get_document(service_item.item_id)
    with tempfile.NamedTemporaryFile(delete=False) as download_to:
        download_to.write(json.dumps(document).encode('utf-8'))

    return document['title'], ConverterIo(ConverterIoType.PATH, download_to.name, ConversionFormatId.gdoc)


def fetch_service_item(service_item: ServiceItem) -> typing.Tuple[str, ConverterIo]:
    if service_item.service_id == ServiceId.google_docs:
        return fetch_google_docs_content(service_item)

    raise TypeError('Unsupported service item type {}'.format(service_item.service_id))


def parse_service_url(url: str) -> typing.Optional[ServiceItem]:
    try:
        google_docs_id = extract_google_document_id_from_url(url)
        return ServiceItem(ServiceId.google_docs, google_docs_id)
    except ValueError:
        pass

    return None


def fetch_url(url: str, user_agent: typing.Optional[str] = None,
              seen_urls: typing.Optional[typing.List[str]] = None) -> typing.Tuple[str, ConverterIo]:
    """
    Download a remote file to a tmp location, then generate a `ConverterIO`.

    The conversion_format wil try to be determined from the response mimetype then a fallback to file extensions.

    Returns the filename of the source and a ConversionIo for the source.
    """
    # delegate fetching of 3rpd party service items that have custom URLs, e.g. Google Docs
    service_item = parse_service_url(url)
    if service_item:
        return fetch_service_item(service_item)

    headers = {'User-Agent': user_agent} if user_agent else None

    url = convert_raw_content_url(url)

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
            return fetch_url(new_url, user_agent, seen_urls)

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
            content_disposition: typing.Union[str, bytes] = resp.headers['Content-Disposition']

            if not isinstance(content_disposition, bytes):
                content_disposition = content_disposition.encode('ascii')

            _, metadata = parse_header(content_disposition)
            file_name = metadata.get('filename')
            if isinstance(file_name, bytes):
                file_name = file_name.decode('ascii')
            file_name = unquote(file_name)

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


class ConverterContext(typing.NamedTuple):
    output_intermediary: bool = False
    maybe_zip: bool = False


class ConverterFacade(object):
    converter_binary: typing.List[str]

    def __init__(self, converter_binary: typing.List[str]) -> None:
        self.converter_binary = converter_binary

    def convert(self, input_data: ConverterIo, output_data: ConverterIo,
                context: typing.Optional[ConverterContext]) -> subprocess.CompletedProcess:
        convert_args: typing.List[str] = [
            'convert',
            '--from', input_data.conversion_format.value.format_id,
            '--to', output_data.conversion_format.value.format_id,
            input_data.as_path_shell_arg, output_data.as_path_shell_arg]

        if context:
            if context.output_intermediary:
                if output_data.as_path_shell_arg == '-':
                    raise RuntimeError('Can\'t output the intermediary when sending output to STDOUT')

            convert_args.append(output_data.as_path_shell_arg + '.json')

            if context.maybe_zip:
                # If output contains media it will be zipped up
                convert_args.append('--zip=maybe')

        input_pipe_data = input_data.data if input_data.io_type == ConverterIoType.PIPE else None

        return subprocess.run(self.converter_binary + convert_args, input=input_pipe_data, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

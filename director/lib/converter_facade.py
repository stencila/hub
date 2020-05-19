import datetime
import enum
import ipaddress
import json
import os
import re
import subprocess
import tempfile
import typing
from io import BytesIO
from os.path import splitext, basename
from socket import gethostbyname
from urllib.parse import urlparse, urljoin, unquote

import requests
from django.core.exceptions import ValidationError
from django.http.multipartparser import parse_header
from googleapiclient.errors import HttpError
from requests import Response

from lib.conversion_types import (
    ConversionFormatId,
    conversion_format_from_mimetype,
    conversion_format_from_path,
    UnknownFormatError,
)
from lib.google_docs_facade import GoogleDocsFacade
from projects.source_models import GoogleDocsSource, SourceAddress

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
    # data can be bytes to be converted (io_type == PIPE) or the path/url to the file to be converted (io_type == PATH)
    data: typing.Union[None, str, bytes]
    conversion_format: typing.Optional[ConversionFormatId] = None

    @property
    def as_path_shell_arg(self) -> str:
        if self.io_type == ConverterIoType.PIPE:
            return "-"  # placeholder for STDIN/STDOUT

        return str(self.data)


class RemoteFileException(Exception):
    pass


class GoogleDocs403Exception(RemoteFileException):
    pass


def is_malicious_host(hostname: typing.Optional[str]) -> bool:
    """Detect if user is trying to do things like connect to localhost or a local IP address of some kind."""
    if not hostname:
        return True

    if hostname.lower() in ["hub-test.stenci.la", "hub.stenci.la"]:
        return True

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
    github_match = re.search(
        r"^https?://github\.com/([a-z0-9\-]+)/([a-z0-9\-_]+)/blob/([^?]+)", url, re.I
    )

    if github_match:
        return "https://raw.githubusercontent.com/{}/{}/{}".format(
            github_match.group(1), github_match.group(2), github_match.group(3)
        )

    hackmd_match = re.search(r"^https?://hackmd\.io/([^/?]+)", url, re.I)

    if hackmd_match:
        return "https://hackmd.io/{}/download".format(hackmd_match.group(1))

    return url


def is_encoda_delegate_url(url: typing.Optional[str]) -> bool:
    """Check if the URL can be passed straight to Encoda for it to fetch."""
    url_obj = urlparse(url)

    hostname = url_obj.hostname

    if not hostname:
        return False

    return hostname.lower() in ["journals.plos.org", "elifesciences.org"]


class ServiceId(enum.Enum):
    google_docs = enum.auto()


class ServiceItem(typing.NamedTuple):
    service_id: ServiceId
    item_id: str


def fetch_google_docs_content(
    service_item: ServiceItem,
) -> typing.Tuple[str, ConverterIo]:

    gdf = GoogleDocsFacade()
    document = gdf.get_document(service_item.item_id)
    with tempfile.NamedTemporaryFile(delete=False) as download_to:
        download_to.write(json.dumps(document).encode("utf-8"))

    return (
        document["title"],
        ConverterIo(ConverterIoType.PATH, download_to.name, ConversionFormatId.gdoc),
    )


def fetch_service_item(service_item: ServiceItem) -> typing.Tuple[str, ConverterIo]:
    if service_item.service_id == ServiceId.google_docs:
        try:
            return fetch_google_docs_content(service_item)
        except HttpError as e:
            if e.resp["status"] == "403":  # it is a string
                raise GoogleDocs403Exception()
            raise

    raise TypeError("Unsupported service item type {}".format(service_item.service_id))


def parse_service_url(url: str) -> typing.Optional[ServiceItem]:
    try:
        google_docs_id = typing.cast(
            SourceAddress, GoogleDocsSource.parse_address(url, strict=True)
        ).docs_id
        return ServiceItem(ServiceId.google_docs, google_docs_id)
    except ValidationError:
        pass

    return None


def fetch_url(
    url: str,
    response_delegate: typing.Optional[
        typing.Callable[[str, Response], typing.Any]
    ] = None,
    user_agent: typing.Optional[str] = None,
    seen_urls: typing.Optional[typing.List[str]] = None,
) -> typing.Any:
    """
    Fetch a URL, following redirects and denying access to dangerous URLs.

    If response_delegate is provided, call out to that function to generate the response and return it. Otherwise, just
    return the file name.
    """
    # delegate fetching of 3rd party service items that have custom URLs, e.g. Google Docs
    service_item = parse_service_url(url)
    if service_item:
        return fetch_service_item(service_item)

    headers = {"User-Agent": user_agent} if user_agent else None

    url = convert_raw_content_url(url)

    url_obj = urlparse(url)

    if url_obj.hostname is None:
        raise TypeError('Url "{}" appears to have no hostname.'.format(url))

    if is_malicious_host(url_obj.hostname):
        raise RemoteFileException(
            "{} is not a valid hostname.".format(url_obj.hostname)
        )

    _, file_ext = splitext(url_obj.path)

    if seen_urls is None:
        seen_urls = []

    with requests.request(
        "GET",
        url,
        headers=headers,
        stream=True,
        timeout=DOWNLOAD_TIMEOUT_SECONDS,
        allow_redirects=False,
    ) as resp:
        if "Location" in resp.headers:
            # Manually follow redirects to determine if it is a redirect to a malicious URL
            if url in seen_urls:
                raise RemoteFileException("Looping redirect found at {}".format(url))
            seen_urls.append(url)

            if len(seen_urls) > MAX_HTTP_REDIRECTS:
                raise RemoteFileException(
                    "Too many HTTP redirects from original URL: {}".format(seen_urls[0])
                )

            new_url = urljoin(url, resp.headers["location"])
            return fetch_url(new_url, response_delegate, user_agent, seen_urls)

        resp.raise_for_status()

        file_name = basename(url_obj.path)

        if "Content-Disposition" in resp.headers:
            content_disposition: typing.Union[str, bytes] = resp.headers[
                "Content-Disposition"
            ]

            if not isinstance(content_disposition, bytes):
                content_disposition = content_disposition.encode("ascii")

            _, metadata = parse_header(content_disposition)
            file_name = metadata.get("filename")
            if isinstance(file_name, bytes):
                file_name = file_name.decode("ascii")
            file_name = unquote(file_name)

        if response_delegate:
            return response_delegate(file_name, resp)
        return file_name


def download_from_response(
    file_name: str,
    resp: Response,
    download: typing.Union[str, bool] = False,
    return_content: bool = False,
) -> typing.Union[bytes, typing.Tuple[str, ConversionFormatId]]:
    """
    Download data from the `response`.

    The `download` and `return_content` arguments are mutually exclusive (only one can be truthy at a time and they
    can't both be false).

    If `download` is True, then the file will be downloaded to a temporary file. The temporary file will not be deleted
    at the end of this function. The calling function should clean it up. If `download` is a string the the file will
    be downloaded to that path.

    If `return_content` is true, then the content is downloaded and returned (as bytes).
    """
    if bool(download) == bool(return_content):
        raise ValueError(
            "One of download or return_content must be set, not both or neither."
        )

    if "Content-Length" in resp.headers:
        try:
            content_length = int(resp.headers["Content-Length"])
            if content_length > MAX_REMOTE_CONVERT_SIZE:
                raise RemoteFileException(
                    "Not fetching remote file as it exceeds the maximum size for conversion."
                )
        except ValueError:
            pass

    if download:
        source_format = None
        mimetype = resp.headers.get("Content-Type")
        if mimetype:
            mimetype = mimetype.split(";")[0]
        if mimetype:
            try:
                source_format = conversion_format_from_mimetype(mimetype)
            except UnknownFormatError:
                pass  # Fall back to extension, in cases where HTTP server send back 'text/plain' for MD, for example

        if not source_format:
            try:
                source_format = conversion_format_from_path(file_name)
            except ValueError:
                raise UnknownFormatError(
                    'Unable to determine conversion format from mimetype "{}" or file name "{}".'.format(
                        mimetype, file_name
                    )
                )
        if isinstance(download, str):
            output_path = download
            with open(download, "wb") as download_to:
                stream_download(resp, download_to)
        else:
            # it's just a boolean so create a temp file for download
            with tempfile.NamedTemporaryFile(delete=False) as temp_download_to:
                try:
                    stream_download(resp, temp_download_to)
                except Exception:
                    os.unlink(temp_download_to.name)
                    raise
                output_path = temp_download_to.name
        return output_path, source_format
    else:
        # Don't download, read the file and return its contents
        download_to = BytesIO()
        stream_download(resp, download_to)
        download_to.seek(0)
        return download_to.read()


def stream_download(resp: Response, download_to: typing.IO) -> None:
    """Stream the `resp` content as bytes, to the download_to file-like object."""
    downloaded_bytes = 0
    download_start_time = datetime.datetime.now()
    for chunk in resp.iter_content(chunk_size=STREAM_CHUNK_SIZE):
        download_seconds = datetime.datetime.now() - download_start_time
        if download_seconds.total_seconds() > MAX_DOWNLOAD_TIME_SECONDS:
            raise RemoteFileException(
                "Time for download took more than {} seconds ({})".format(
                    MAX_DOWNLOAD_TIME_SECONDS, download_seconds
                )
            )

        if not chunk:
            continue

        downloaded_bytes += len(chunk)

        if downloaded_bytes > MAX_REMOTE_CONVERT_SIZE:
            raise RemoteFileException(
                "Remote file exceeded size limit while streaming."
            )

        download_to.write(chunk)


def download_for_conversion(
    file_name: str, resp: Response
) -> typing.Tuple[str, ConverterIo]:
    """
    Download a remote file to a tmp location, then generate a `ConverterIO`.

    The conversion_format wil try to be determined from the response mimetype then a fallback to file extensions.

    Returns the filename of the source and a ConversionIo for the source.
    """
    # This cast is because we know the return value has this type based on the arguments to `download_from_response`
    download_path, source_format = typing.cast(
        typing.Tuple[str, ConversionFormatId],
        download_from_response(file_name, resp, True),
    )
    return file_name, ConverterIo(ConverterIoType.PATH, download_path, source_format)


def get_response_content(file_name: str, resp: Response) -> bytes:
    """Download the content in `resp` and return its content as bytes."""
    # with these options, the return value from `download_from_response` will be bytes
    return typing.cast(bytes, download_from_response(file_name, resp, False, True))


class ConverterContext(typing.NamedTuple):
    output_intermediary: bool = False
    maybe_zip: bool = False
    standalone: bool = True
    theme: typing.Optional[str] = None


class ConverterFacade(object):
    converter_binary: str

    def __init__(self, converter_binary: str) -> None:
        self.converter_binary = converter_binary

    def convert(
        self,
        input_data: ConverterIo,
        output_data: ConverterIo,
        context: typing.Optional[ConverterContext] = None,
    ) -> subprocess.CompletedProcess:
        convert_args: typing.List[str] = [
            "convert",
            input_data.as_path_shell_arg,
            output_data.as_path_shell_arg,
        ]

        if input_data.conversion_format:
            convert_args.extend(
                ["--from", input_data.conversion_format.value.format_id]
            )

        if output_data.conversion_format:
            convert_args.extend(["--to", output_data.conversion_format.value.format_id])

        if context:
            if context.output_intermediary:
                if output_data.as_path_shell_arg == "-":
                    raise RuntimeError(
                        "Can't output the intermediary when sending output to STDOUT"
                    )

                convert_args.append(output_data.as_path_shell_arg + ".json")

            if context.maybe_zip:
                # If output contains media it will be zipped up
                convert_args.append("--zip=maybe")

            if context.standalone is False:
                convert_args.append("--standalone=false")

            if context.theme:
                convert_args.extend(["--theme", context.theme])

        input_pipe_data = (
            input_data.data if input_data.io_type == ConverterIoType.PIPE else None
        )

        return subprocess.run(
            [self.converter_binary] + convert_args,
            input=input_pipe_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

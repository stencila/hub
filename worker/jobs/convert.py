import json
import os
import tempfile
from typing import Dict, List, Optional, Union, cast

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import GoogleCredentials

from config import get_content_root, get_node_modules_bin
from jobs.base.subprocess_job import SubprocessJob
from util.files import Files, list_files, move_files, temp_dir
from util.gapis import gdrive_service


class Convert(SubprocessJob):
    """
    A job that converts files from one format to another.

    Delegates convertion the Encoda CLI https://github.com/stencila/encoda
    which should be installed globally within the worker's Docker container.
    """

    name = "convert"

    def do(  # type: ignore
        self,
        input: Union[str, bytes],
        output: Union[str, List[str]],
        options: Dict[str, Union[str, bool]] = {},
        src: str = ".",
        dest: str = ".",
        secrets: Dict = {},
        **kwargs,
    ) -> Files:
        """
        Do the conversion.

        The signature of this method is similar to that of Encoda's
        `convert` function but with a flatter structure for the options
        aligned to the Encoda CLI.

        Allows for multiple outputs and alternative source and desination
        directories (with dictionary of files relative to destination).

        input: The path to the input file, or bytes to be sent to stdin.
        output: The path to the output file, a list of outputs files, or
                "-" for output stream bytes (mostly when used by other jobs).
        options:
            from: The format to convert from (defaults to ext name of input)
            to: The format to convert to (defaults to ext name of output)
            theme: Name of the theme to use for outputs
        src: The source storage directory e.g. `snapshots/42/T5kdbaJ8ZmNTXuuv4XJnsi/`
             defaulting to the current working directory
        dest: The destination storage directory e.g. `content/3212/`
              defaulting to the current working directory
        """
        assert (isinstance(input, str) or isinstance(input, bytes)) and len(
            input
        ) > 0, "input must be a non-empty string or bytes"
        assert isinstance(output, str) or isinstance(
            output, list
        ), "output must be a string or list of strings"
        assert isinstance(options, dict), "options must be a dictionary"

        # Rewrite output path(s) to a temporary directory
        temp = None
        outputs = output if isinstance(output, list) else [output]
        for index, output in enumerate(outputs):
            if output != "-":
                if temp is None:
                    temp = temp_dir()
                outputs[index] = os.path.join(temp, output)

        # Generate arguments to Encoda and call it
        args = encoda_args(input, outputs, options)
        result = super().do(args, input=input if isinstance(input, bytes) else None)

        # If the output is a stream then just return the bytes
        if len(outputs) == 1 and outputs[0] == "-":
            return result

        # Get list of created files
        assert isinstance(temp, str)
        files = list_files(temp)

        # Move all files to destination.
        dest_parts = os.path.normpath(dest).split("/")
        if dest_parts[0] == "content":
            dest_root = get_content_root()
        else:
            dest_root = "."
        move_files(temp, dest=os.path.join(dest_root, *dest_parts[1:]))

        # For some conversion targets it is necessary to also create a source.
        if isinstance(output, str) and output.endswith(".gdoc"):
            files[output]["source"] = create_gdoc(
                input_=input, output=output, secrets=secrets
            )

        return files


def encoda_args(  # type: ignore
    input: Union[str, bytes], outputs: List[str], options: Dict[str, Union[str, bool]],
) -> List[str]:
    """
    Create an array of Encoda arguments based on job inputs, outputs and options.
    """
    args = [
        get_node_modules_bin("encoda"),
        "convert",
        "-" if isinstance(input, bytes) else input,
    ] + outputs
    for name, value in options.items():
        # Determine --from option
        # Encoda currently does not allow for mimetypes in the `from` option.
        # This replaces some mimetypes with codec names for formats that are
        # not easily identifiable from their extension. This means that for other
        # files, the file extension will be used to determine the format (which
        # works in most cases).
        if name == "from" and isinstance(value, str):
            value = {
                "application/jats+xml": "jats",
                "application/vnd.google-apps.document": "gdoc",
            }.get(value, value)
            # If the value has a slash in it, assume it's still a mimetype
            # and skip
            if isinstance(value, str) and "/" in value:
                continue

        # Transform boolean values
        if value is False:
            value = "false"
        if value is True:
            value = "true"

        args.append("--{}={}".format(name, value))
    return args


def create_gdoc(
    input_: Union[str, bytes], output: str, secrets: Dict
) -> Dict[str, str]:
    """
    Create a GoogleDoc from input and return its id.

    When encoding to `gdoc`, Encoda actually creates a `docx` file which
    this function then uploads to Google Drive and has it converted
    to a Google Doc there (because it is not possible to upload the
    Google Doc JSON content directly).
    """
    gdoc = (
        gdrive_service(secrets)
        .files()
        .create(
            body={
                "name": input_ if type(input_) is str else "Untitled",
                "mimeType": "application/vnd.google-apps.document",
            },
            media_body=MediaFileUpload(output),
            media_mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        .execute()
    )
    return dict(type_name="GoogleDocs", doc_id=gdoc["id"])

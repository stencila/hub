import json
from typing import Any, Dict, Union

from .convert import Convert


class Encode(Convert):
    """
    A job that encodes Stencila Schema JSON as another format.

    An example of usage of this job would be to encode a document as
    a PDF file after it has been through the `execute` job.
    """

    name = "encode"

    def do(self, input: Any, output: str, options: Dict[str, Union[str, bool]] = {}, **kwargs):  # type: ignore
        """
        Do the encoding.

        Simply does a conversion job, with input read from `stdin` as JSON
        and output to a file.
        """
        input_json = json.dumps(input)
        return super().do(
            input_json.encode(), output, dict(**options, **{"from": "json"})
        )

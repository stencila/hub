import json
from typing import cast, List, Union, Dict

from .convert import Convert


class Decode(Convert):
    """
    A job that decodes content to Stencila Schema JSON.

    An example of usage of this job would be to decode a document into
    JSON so it can be passed to the `execute` job.
    """

    name = "decode"

    def do(self, input: Union[str, bytes], options: Dict[str, Union[str, bool]] = {}, **kwargs):  # type: ignore
        """
        Do the decoding.

        Simply does a conversion job, outputting JSON to `stdout`
        and then parsing that JSON.
        """
        result = super().do(input, "-", dict(**options, to="json"))
        return json.loads(cast(str, result))

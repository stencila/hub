from typing import List, Union, Dict

from jobs.base.subprocess_job import SubprocessJob


class Convert(SubprocessJob):
    """
    A job that converts files from one format to another.

    Delegates convertion the Encoda CLI https://github.com/stencila/encoda
    which should be installed globally within the worker's Docker container.
    """

    name = "convert"

    def do(self, input: str, output: Union[str, List[str]], options: Dict[str, Union[str, bool]] = {}):  # type: ignore
        """
        Do the conversion.

        The signature of this method is similar to that of Encoda's
        `convert` function but with a flatter structure for the options
        aligned to the Encoda CLI.

        input: The path to the input file
        output: The path to the output file, or a list of outputs files
        options:
            from: The format to convert from (defaults to ext name of input)
            to: The format to convert to (defaults to ext name of output)
            theme: Name of the theme to use for outputs
        """
        assert (
            isinstance(input, str) and len(input) > 0
        ), "input must be a non-empty string"
        assert isinstance(output, str) or isinstance(
            output, list
        ), "output must be a string or list of strings"
        assert isinstance(options, dict), "options must be a dictionary"

        args = ["npx", "encoda", "convert", input]
        args += output if isinstance(output, list) else [output]
        for name, value in options.items():
            if value is False:
                value = "false"
            if value is True:
                value = "true"
            args.append("--{}={}".format(name, value))

        return super().do(args)

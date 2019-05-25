import enum
import subprocess
import typing


class ConverterIoType(enum.Enum):
    PIPE = enum.auto()
    PATH = enum.auto()


class ConverterIo(typing.NamedTuple):
    io_type: ConverterIoType
    # data is either data to be converted (io_type == PIPE) or the path to the file to be converted (io_type == PATH)
    data: typing.Union[None, str, bytes]
    conversion_format: str

    @property
    def as_path_shell_arg(self) -> str:
        if self.io_type == ConverterIoType.PIPE:
            return '-'  # placeholder for STDIN/STDOUT

        return str(self.data)


class ConverterFacade(object):
    converter_binary: typing.List[str]

    def __init__(self, converter_binary: typing.List[str]) -> None:
        self.converter_binary = converter_binary

    def convert(self, input_data: ConverterIo, output_data: ConverterIo) -> typing.Optional[bytes]:
        convert_args = [
            '--from', input_data.conversion_format,
            '--to', output_data.conversion_format,
            input_data.as_path_shell_arg, output_data.as_path_shell_arg]

        input_pipe_data = input_data.data if input_data.io_type == ConverterIoType.PIPE else None

        convert_result = subprocess.run(self.converter_binary + convert_args, input=input_pipe_data,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if convert_result.returncode != 0:
            raise RuntimeError('Convert process failed. Stderr is: {}'.format(convert_result.stderr.decode('ascii')))

        if output_data.io_type == ConverterIoType.PIPE:
            return convert_result.stdout

        return None

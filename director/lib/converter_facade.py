import subprocess
import typing


class ConverterFacade(object):
    converter_binary: typing.List[str]

    def __init__(self, converter_binary: typing.List[str]) -> None:
        self.converter_binary = converter_binary

    def convert(self, from_format: str, to_format: str, input_data: bytes) -> bytes:
        convert_args = ['--from', from_format, '--to', to_format]
        convert_result = subprocess.run(self.converter_binary + convert_args, input=input_data, stdout=subprocess.PIPE)
        return convert_result.stdout

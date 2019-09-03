import os
import tempfile
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

from lib.converter_facade import fetch_remote_file, ConverterFacade, ConverterIo, ConverterIoType, ConversionFormat
from open.forms import UrlForm


class OpenView(View):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.method != 'POST':
            url_form = UrlForm()
        else:
            url_form = UrlForm(request.POST)

        if url_form.is_valid():
            source_io = None
            try:
                source_io = fetch_remote_file(url_form.cleaned_data['url'], settings.STENCILA_CLIENT_USER_AGENT)
                with tempfile.NamedTemporaryFile() as target_file:

                    target_io = ConverterIo(ConverterIoType.PATH, target_file.name, ConversionFormat.html)
                    converter = ConverterFacade(settings.STENCILA_BINARY)

                    converter.convert(source_io, target_io)

                    return HttpResponse(
                        FileWrapper(target_file), content_type='text/html'
                    )
            finally:
                if source_io:
                    try:
                        os.unlink(source_io.data)
                    except OSError:
                        pass

        return render(request, 'open/main.html', {'url_form': url_form})

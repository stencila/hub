#!/usr/bin/python3

import os
from zipfile import ZipFile

with ZipFile(
    os.path.join(os.path.dirname(__file__), "1000-maniacs.zip"), "w"
) as zip_file:
    for index in range(1000):
        zip_file.writestr(f"{index}.txt", b"maniac")

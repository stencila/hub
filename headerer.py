# Adds the following header to source files (currently only .py)

import re

header = '''
This file is part of Stencila Hub.

Copyright (C) 2015-2016 Stencila Ltd.

Stencila Hub is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Stencila Hub is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Stencila Hub.  If not, see <http://www.gnu.org/licenses/>.

'''
header_lines = header.strip().split('\n')

# Commented for Python (other file types may be added)
header_lines_py = ['#  '+line+'\n' for line in header_lines]

dir_excludes = [
    re.compile(r'^\.$'),  # Exclude files in top level

    re.compile(r'.*/migrations$'),  # Exclude migrations

    re.compile(r'^\./curator/env/?.*'),

    re.compile(r'^\./director/dynamic/?.*'),
    re.compile(r'^\./director/env/?.*'),
    re.compile(r'^\./director/general/node_modules/?.*'),
    re.compile(r'^\./director/general/semantic/?.*'),
    re.compile(r'^\./director/static/?.*'),
    re.compile(r'^\./director/uploads/?.*'),

    re.compile(r'^\./worker/env/?.*'),

    re.compile(r'^\./\.git.*'),
]

file_excludes = [
    re.compile(r'.*\.conf$'),
    re.compile(r'.*\.html$'),
    re.compile(r'.*\.gitignore$'),
    re.compile(r'.*\.go$'),
    re.compile(r'.*\.log$'),
    re.compile(r'.*\.pyc$'),
    re.compile(r'.*\.sqlite3$'),
    re.compile(r'.*\.sh$'),
    re.compile(r'.*\.txt$'),

    re.compile(r'^\./director/manage.py$'),
    re.compile(r'.*/__init__.py$'),
]

file_includes = [
    re.compile(r'.*\.py$')  # Currently just marking Python files
]


def dir_excluded(path):
    for exclude in dir_excludes:
        if exclude.match(path):
            return True
    return False


def file_excluded(path):
    for exclude in file_excludes:
        if exclude.match(path):
            return True
    return False


def file_included(path):
    for include in file_includes:
        if include.match(path):
            return True
    return False

import os
for root, dirs, files in os.walk('.'):
    if dir_excluded(root):
        continue
    print root
    for filename in files:
        path = os.path.join(root, filename)
        if not file_excluded(path) and file_included(path):
            print '  ', path
            # Read existing lines
            file = open(path)
            lines = file.readlines()
            file.close()
            # If first line is not same as first line of header
            if lines[0] != header_lines[0]:
                # Prepend header to front
                lines[:0] = header_lines_py + ['\n']
                # Write out
                file = open(path, 'w')
                file.writelines(lines)
                file.close()

#!/usr/bin/env python3

import os
import simplecrypt
import sys


def secret(*args):
    """
    Create a secret encrypted file. You need to set the STENCILA_DEV_PASSWORD environment variable
    e.g.
       STENCILA_DEVPASS=notasecret ./make.py secret secrets/director-allauth.json secrets/director-allauth.json.enc
    """
    inp = args[0]
    out = args[1]
    password = os.environ['STENCILA_DEVPASS']
    with open(inp) as inp_file:
        plaintext = inp_file.read()
        with open(out, 'wb') as out_file:
            ciphertext = simplecrypt.encrypt(password, plaintext)
            out_file.write(ciphertext)

if __name__ == '__main__':
    task = sys.argv[1]
    args = sys.argv[2:]
    if task == 'secret':
        secret(*args)
    else:
        print('Unknown task: ' + task)

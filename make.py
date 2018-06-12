#!/usr/bin/env python3

import os
import simplecrypt
import sys


def encrypt_secret(*args):
    """
    Create a secret encrypted file.
    You need to set the STENCILA_DEVPASS environment variable
    e.g.
       STENCILA_DEVPASS=notasecret ./make.py encrypt_secret secrets/director-allauth.json
    """
    inp = args[0]
    out = inp + '.enc'
    password = os.environ['STENCILA_DEVPASS']
    with open(inp) as inp_file:
        plaintext = inp_file.read()
        with open(out, 'wb') as out_file:
            ciphertext = simplecrypt.encrypt(password, plaintext)
            out_file.write(ciphertext)


def decrypt_secret(*args):
    """
    Create a secret encrypted file.
    You need to set the STENCILA_DEVPASS environment variable
    e.g.
       STENCILA_DEVPASS=notasecret ./make.py decrypt_secret secrets/director-allauth.json.enc
    """
    inp = args[0]
    out = inp[:-4]
    password = os.environ['STENCILA_DEVPASS']
    with open(inp, 'rb') as inp_file:
        ciphertext = inp_file.read()
        plaintext = simplecrypt.decrypt(password, ciphertext)
        if not os.path.exists(out):
            with open(out, 'w') as out_file:
                out_file.write(plaintext.decode('utf8'))
        else:
            print('File already exists: ' + out)


if __name__ == '__main__':
    task = sys.argv[1]
    args = sys.argv[2:]
    if task == 'encrypt_secret':
        encrypt_secret(*args)
    elif task == 'decrypt_secret':
        decrypt_secret(*args)
    else:
        print('Unknown task: ' + task)

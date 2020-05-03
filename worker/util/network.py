"""A module for networking related utilities."""

import random
import socket


def get_local_ip():
    """
    Get the local IP address.

    Equivalent to https://github.com/stencila/executa/blob/753207cb31298578497d978265c718e20b583a05/src/tcp/util.ts#L15
    Thanks to https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_random_port():
    """
    Get a random port from the local port range.

    Get OS to pick a port, and if that fails for some reason, fallback to 
    random choice.
    Thanks to https://unix.stackexchange.com/questions/55913/whats-the-easiest-way-to-find-an-unused-local-port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("", 0))
        port = s.getsockname()[1]
    except:
        port = ransom.randint(1024, 65535)
    finally:
        s.close()
    return port

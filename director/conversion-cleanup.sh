#!/bin/bash

until
    python3 -c "import socket; s = socket.create_connection(('127.0.0.1', 5432)); s.close()" > /dev/null  2>&1;
    do echo waiting for postgres;
    sleep 2;
done;

sleep 5

python3 ./manage.py conversioncleanup

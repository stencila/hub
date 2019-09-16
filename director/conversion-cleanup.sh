#!/bin/bash

until
    python3 -c "import socket; socket.create_connection(('127.0.0.1', 5432))" > /dev/null  2>&1;
    do echo waiting for postgres;
    sleep 2;
done;

python3 ./manage.py conversioncleanup

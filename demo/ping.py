#!/usr/bin/env python
# coding: utf-8
import time
import logging
import sys
from stpclient import Client


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    if len(sys.argv) > 3:
        count = int(sys.argv[3])
    else:
        count = 1
    client = Client(host, port, timeout=1)
    for i in range(count):
        try:
            print client.call('ping').argv
        except:
            logging.exception('')
            client.close()
        time.sleep(0.5)


if __name__ == '__main__':
    main()

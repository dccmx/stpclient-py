#!/usr/bin/env python
# coding: utf-8
import time
from stpclient import Client


def main():
    client = Client('localhost', 9999, timeout=1)
    try:
        print client.call('long')
    except Exception as e:
        print e
        time.sleep(1)
    print client.call('ping').argv


if __name__ == '__main__':
    main()

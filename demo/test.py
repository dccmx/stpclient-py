#!/usr/bin/env python
# coding: utf-8
import time
from tornado.ioloop import IOLoop
from stpclient.exceptions import STPTimeoutError
from stpclient import Client
from stpclient import AsyncClient


def test_async():
    io_loop = IOLoop.instance()
    client = AsyncClient('localhost', 9999, timeout=1)
    assert client.closed
    _response = ['']

    def callback(response):
        _response[0] = response
        io_loop.stop()
    print 'call long'
    client.call('long', callback)
    io_loop.start()
    response = _response[0]
    _response = ['']
    try:
        response.rethrow()
    except STPTimeoutError as e:
        print e
        time.sleep(2)
    print 'call ping'
    client.call('ping', callback)
    io_loop.start()
    response = _response[0]
    _response = ['']
    response.rethrow()


def test_sync():
    client = Client('localhost', 9999, timeout=1)
    try:
        print client.call('long')
    except Exception as e:
        print e
        time.sleep(1)
    print client.call('ping').argv
    print 'sleep 10s'
    time.sleep(10)
    print 'ping again'
    try:
        print client.call('ping').argv
    except Exception as e:
        print e
    time.sleep(10)
    print 'ping again'
    print client.call('ping').argv


def main():
    test_sync()
    test_async()


if __name__ == '__main__':
    main()

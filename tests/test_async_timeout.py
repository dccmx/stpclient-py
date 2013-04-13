#!/usr/bin/python
# coding: utf-8
import unittest
from nose.tools import raises, timed
from stpclient.exceptions import STPTimeoutError


class TestAsyncTimeout(unittest.TestCase):
    def setUp(self):
        from tornado.ioloop import IOLoop
        self.io_loop = IOLoop.instance()
        self._response = None

    @raises(STPTimeoutError)
    @timed(1.1)
    def test_timeout(self):
        from stpclient import AsyncClient
        client = AsyncClient('localhost', 9999, timeout=1)
        assert client.closed

        def callback(response):
            self._response = response
            self.io_loop.stop()
        client.call('long', callback)
        self.io_loop.start()
        response = self._response
        self._response = None
        response.rethrow()

    @timed(0.1)
    def test_not_timeout(self):
        from stpclient import AsyncClient
        client = AsyncClient('localhost', 9999, timeout=1)
        assert client.closed

        def callback(response):
            self._response = response
            self.io_loop.stop()
        client.call('ping', callback)
        self.io_loop.start()
        response = self._response
        self._response = None
        response.rethrow()

    @timed(3.2)
    def test_timeout_state(self):
        import time
        from stpclient import AsyncClient
        client = AsyncClient('localhost', 9999, timeout=1)
        assert client.closed

        def callback(response):
            self._response = response
            self.io_loop.stop()
        client.call('long', callback)
        self.io_loop.start()
        response = self._response
        self._response = None
        try:
            response.rethrow()
        except STPTimeoutError:
            time.sleep(2)
        client.call('ping', callback)
        self.io_loop.start()
        response = self._response
        self._response = None
        response.rethrow()

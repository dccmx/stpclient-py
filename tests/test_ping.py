#!/usr/bin/python
# coding: utf-8
import unittest
from nose.tools import eq_
from nose.tools import timed


class TestPing(unittest.TestCase):
    @timed(0.1)
    def test_connect(self):
        from stpclient import Client
        client = Client('localhost', 9999, timeout=1)
        assert not client.closed
        client.close()
        assert client.closed

    @timed(0.1)
    def test_error_state(self):
        from stpclient import Client
        from stpclient.exceptions import STPNetworkError
        client = Client('localhost', 0, timeout=1)
        assert not client.closed
        try:
            client.call('ping')
        except STPNetworkError:
            pass
        assert client.closed

    @timed(0.1)
    def test_ping(self):
        from stpclient import Client
        client = Client('localhost', 9999, timeout=1)
        resp = client.call('ping')
        eq_(resp[0], 'OK')
        eq_(resp[1], 'PONG')

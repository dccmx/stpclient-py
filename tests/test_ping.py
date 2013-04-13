#!/usr/bin/python
# coding: utf-8
import unittest
from nose.tools import eq_


class TestPing(unittest.TestCase):
    def test_connect(self):
        from stpclient import Client
        client = Client('localhost', 9999)
        assert not client.closed
        client.close()
        assert client.closed

    def test_error_state(self):
        from stpclient import Client
        from stpclient.exceptions import STPNetworkError
        client = Client('localhost', 0)
        assert not client.closed
        try:
            client.call('ping')
        except STPNetworkError:
            pass
        assert client.closed

    def test_ping(self):
        from stpclient import Client
        client = Client('localhost', 9999)
        resp = client.call('ping')
        eq_(resp[0], 'OK')
        eq_(resp[1], 'PONG')

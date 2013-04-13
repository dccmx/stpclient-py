#!/usr/bin/python
# coding: utf-8
import unittest
from nose.tools import raises
from stpclient.exceptions import STPTimeoutError


class TestTimeout(unittest.TestCase):
    @raises(STPTimeoutError)
    def test_timeout(self):
        from stpclient import Client
        client = Client('localhost', 9999, timeout=1)
        assert not client.closed
        client.call('long')

    def test_timeout_state(self):
        from stpclient import Client
        from stpclient.exceptions import STPTimeoutError
        client = Client('localhost', 9999, timeout=1)
        assert not client.closed
        try:
            client.call('long')
        except STPTimeoutError as e:
            print e
            pass
        assert client.closed

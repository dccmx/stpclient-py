#!/usr/bin/python
# coding: utf-8
from threading import local
from stpclient import Client


class MagicClient(local):
    def __init__(self, *args, **kwargs):
        self.client = Client(*args, **kwargs)

    def __getattr__(self, name):
        def stpcall(*args):
            resp = self.client.call((name,) + args).argv
            if resp[0] == 'ERR':
                raise Exception(resp[1])
            else:
                return resp[1:]
        return stpcall

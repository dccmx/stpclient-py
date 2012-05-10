#!/usr/bin/env python
# coding: utf-8
from stpclient import AsyncClient
from stpclient import ioloop


i = 0
def test_callback():
    clients = []
    def callback(resp):
        global i
        print resp.error if resp.error is not None else resp.argv
        i += 1
        if i == 4:
            ioloop.IOLoop.instance().stop()
    for i in range(2):
        clients.append(AsyncClient('localhost', 3370 + i, connect_timeout=2))
    for client in clients:
        client.call('ping', callback)
        client.call('ping', callback)
    ioloop.IOLoop.instance().start()


def test_lazy_call():
    clients = []
    async_response = []
    for i in range(10):
        clients.append(AsyncClient('localhost', 3370 + i, connect_timeout=2))
    for client in clients:
        async_response.append(client.lazy_call('ping'))
    for resp in async_response:
        try:
            response = resp.response
        except Exception as e:
            print str(e)
        print response.argv


def main():
    test_callback()
    test_lazy_call()


if __name__ == '__main__':
    main()

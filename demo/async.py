#!/usr/bin/env python
# coding: utf-8
from stpclient import AsyncClient
from stpclient import ioloop


i = 0


def main():
    clients = []
    def callback(resp):
        global i
        if resp.error is not None:
            print resp.error
        else:
            print resp.argv
        i += 1
        if i == 10:
            ioloop.IOLoop.instance().stop()
    for i in range(10):
        clients.append(AsyncClient('localhost', 3370 + i, connect_timeout=2))
    for client in clients:
        client.add_call('ping', callback)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()

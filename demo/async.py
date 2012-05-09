#!/usr/bin/env python
# coding: utf-8
from stpclient import AsyncClient


def main():
    clients = []
    def callback(resp):
        print resp
    for i in range(10):
        clients.append(AsyncClient('localhost', 3370 + i))
    for client in clients:
        client.async_call('PING', callback)


if __name__ == '__main__':
    main()

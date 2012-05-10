#!/usr/bin/env python
# coding: utf-8
import argparse
import os
import readline
from stpclient import Client


argparser = argparse.ArgumentParser(description='telnet of stp', conflict_handler='resolve')
argparser.add_argument('-h', metavar='host', dest='host', type=str, default='localhost', help='host')
argparser.add_argument('-p', metavar='port', dest='port', type=int, default=3399, help='port')
argparser.add_argument('-s', metavar='socket', dest='socket', type=str, default=None, help='unix socket of sink')
args = argparser.parse_args()

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')
histfile = os.path.join(os.path.expanduser("~"), ".telstp_history")
try:
    readline.read_history_file(histfile)
except IOError:
    pass
import atexit
atexit.register(readline.write_history_file, histfile)
del os, histfile


def main():
    client = Client(args.host, args.port, unix_socket=args.socket)
    while True:
        line = raw_input('telstp %s>: ' % str(client))
        if line == 'quit':
            break
        try:
            resp = client.call(line.split())
            for r in resp.argv:
                print r
        except Exception, e:
            print str(e)
            client = Client(args.host, args.port, unix_socket=args.socket)


if __name__ == '__main__':
    main()

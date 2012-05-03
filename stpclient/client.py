#!/usr/bin/python
# coding: utf-8
import socket
import time
from threading import local


__author__ = "dccmx <dccmx@dccmx.com>"
__version__ = "0.1"
__copyright__ = "Copyright (C) 2012 dccmx"
__license__ = "MIT"


# exceptions for Client
class STPError(Exception):
    pass


class STPTimeoutError(Exception):
    pass


class STPNetworkError(Exception):
    pass


class Connection(local):
    def __init__(self, host='localhost', port=3399, timeout=1, unix_socket=None):
        self.host = host
        self.port = port
        self.unix_socket = unix_socket
        self.timeout = timeout
        self.socket = None
        self.address = None
        self.family = None
        self.recvbuf = ''
        self.sendbuf = ''
        self.connect()

    def connect(self):
        if self.socket is not None:
            return
        if self.unix_socket is not None:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.family = socket.AF_UNIX
            self.address = self.unix_socket
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.family = socket.AF_INET
            self.address = (self.host, self.port)
        if self.timeout > 0:
            self.socket.settimeout(self.timeout)
        try:
            self.socket.connect(self.address)
        except socket.timeout, e:
            self.close()
            raise STPTimeoutError(str(e))
        except Exception, e:
            self.close()
            raise e

    def close(self):
        self.sendbuf = ''
        if self.socket:
            self.socket.close()
            self.socket = None

    def _encode(self, value):
        "Return a bytestring representation of the value"
        if isinstance(value, unicode):
            return value.encode('utf-8', 'strict')
        return str(value)

    def addarg(self, arg):
        arg = self._encode(arg)
        self.sendbuf += '%d\r\n%s\r\n' % (len(arg), arg)

    def call(self):
        self.connect()
        try:
            self.sendbuf += '\r\n'
            self.socket.sendall(self.sendbuf)
            self.sendbuf = ''
        except socket.timeout, e:
            self.close()
            raise STPTimeoutError(str(e))
        except Exception, e:
            self.close()
            raise e

    def readlen(self, length):
        now = time.time()
        while len(self.recvbuf) < length + 2:
            if self.timeout > 0 and time.time() - now >= self.timeout:
                raise STPTimeoutError("Timeout")
            self.recvbuf += self.socket.recv(4096)
        ret = self.recvbuf[:length]
        self.recvbuf = self.recvbuf[length + 2:]
        return ret

    def readline(self):
        now = time.time()
        while True:
            if self.timeout > 0 and time.time() - now >= self.timeout:
                raise STPTimeoutError("Timeout")
            index = self.recvbuf.find('\r\n')
            if index >= 0:
                break
            data = self.socket.recv(4096)
            if not data:
                raise STPNetworkError('Connection closed while reading from %s' % str(self))
                self.recvbuf = ''
                return ''
            self.recvbuf += data
        ret = self.recvbuf[:index]
        self.recvbuf = self.recvbuf[index + 2:]
        return ret

    def recv_response(self):
        if self.socket is None:
            raise STPNetworkError("Lost connection from %s", str(self))
        ret = []
        try:
            now = time.time()
            while True:
                if self.timeout > 0 and time.time() - now >= self.timeout:
                    raise STPTimeoutError("Timeout")
                line = self.readline()
                if line == '':
                    break
                length = int(line)
                ret.append(self.readlen(length))
            return ret
        except socket.timeout, e:
            self.close()
            raise STPTimeoutError(str(e))
        except Exception, e:
            self.close()
            raise e

    def __str__(self):
        if self.family == socket.AF_INET:
            return "%s:%d" % (self.address[0], self.address[1])
        else:
            return "%s" % (self.address)


class Client(local):
    def __init__(self, host, port, timeout=None, unix_socket=None):
        self.connection = Connection(host, port, timeout, unix_socket)

    def call(self, args):
        for arg in args:
            self.connection.addarg(arg)
        self.connection.call()
        return self.connection.recv_response()

#!/usr/bin/python
# coding: utf-8
import sys
import socket
import time
import collections
import functools
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
import exceptions


def encode(value):
    "Return a bytestring representation of the value"
    if isinstance(value, unicode):
        return value.encode('utf-8', 'strict')
    return str(value)


class STPRequest(object):
    def __init__(self, args=None, connect_timeout=None, request_timeout=None):
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        if args is None:
            self._argv = []
        elif isinstance(args, tuple):
            self._argv = list(args)
        elif isinstance(args, list):
            self._argv = args
        else:
            self._argv = [encode(args)]

    def __getitem__(self, key):
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            return [self._argv[i] for i in xrange(*key.indices(len(self._argv)))]
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += len(self._argv)
            if key >= len(self._argv):
                raise IndexError('The index (%d) is out of range.' % key)
            return self._argv[key]  # Get the data from elsewhere
        else:
            raise TypeError('Invalid argument type.')

    def __len__(self):
        return len(self._argv)

    def serialize(self):
        buf = ''
        for arg in self._argv:
            earg = encode(arg)
            buf += '%d\r\n%s\r\n' % (len(earg), earg)
        buf += '\r\n'
        return buf

    def appendbulk(self, arg):
        self._argv.append(arg)


class STPResponse(object):
    def __init__(self, request_time=None, error=None):
        self.request_time = request_time
        self.error = error
        self._argv = []

    @property
    def argv(self):
        return self._argv

    def __len__(self):
        return len(self._argv)

    def __getitem__(self, key):
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            return [self._argv[i] for i in xrange(*key.indices(len(self._argv)))]
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += len(self._argv)
            if key >= len(self._argv):
                raise IndexError('The index (%d) is out of range' % key)
            return self._argv[key]  # Get the data from elsewhere
        else:
            raise TypeError('Invalid argument type')

    def rethrow(self):
        '''If there was an error on the request, raise an `STPError`.'''
        if self.error:
            raise self.error


class LazySTPResponse(object):
    def __init__(self, io_loop):
        self._io_loop = io_loop
        self._response = None

    def __call__(self, resp):
        self._response = resp
        self._io_loop.stop()

    @property
    def response(self):
        while self._response is None:
            self._io_loop.start()
        self._response.rethrow()
        return self._response


class Connection(object):
    '''
    timeout
      -1: no timeout
      None: per-request setting
      other: overide per-request setting
    '''
    def __init__(self, host, port, io_loop, unix_socket=None, timeout=-1, connect_timeout=-1, max_buffer_size=104857600):
        self.host = host
        self.port = port
        self.unix_socket = unix_socket
        self.io_loop = io_loop
        self.connect_timeout = connect_timeout
        self.request_timeout = timeout
        self.max_buffer_size = max_buffer_size
        self.start_time = time.time()
        self.stream = None
        self._timeout = None
        self._callback = None
        self._request_queue = collections.deque()
        self._request = None
        self._response = STPResponse()
        self._connecting = False

    @property
    def closed(self):
        return self.stream is None

    def close(self):
        self._clear_close_callback()
        self._close_stream()
        self._clear_timeout()

    def _close_stream(self):
        if self.stream is not None:
            self.stream.error = None
            if not self.stream.closed():
                self.stream.close()
        self.stream = None

    def _clear_timeout(self):
        if self._timeout is not None:
            self.io_loop.remove_timeout(self._timeout)
        self._timeout = None

    def _clear_close_callback(self):
        if self.stream:
            self.stream.set_close_callback(None)

    def _connect(self):
        # fix tornado stream bug, see tornado.iostream.close()
        sys.exc_clear()
        self.close()
        self._connecting = True
        af = socket.AF_INET if self.unix_socket is None else socket.AF_UNIX
        self.stream = IOStream(socket.socket(af, socket.SOCK_STREAM),
                               io_loop=self.io_loop,
                               max_buffer_size=self.max_buffer_size)
        if self.connect_timeout is not None and self.connect_timeout > 0:
            self._timeout = self.io_loop.add_timeout(time.time() + self.connect_timeout, self._on_timeout)
        self.stream.set_close_callback(self._on_close)
        addr = self.unix_socket if self.unix_socket is not None else (self.host, self.port)
        self.stream.connect(addr, self._on_connect)

    def _on_close(self):
        if self.stream and not self.stream.error:
            self.io_loop.add_callback(functools.partial(self._on_error, exceptions.STPNetworkError('Unkown socket error (this should not happen!)')))
        else:
            self.io_loop.add_callback(self._on_error)

    def _on_connect(self):
        self._connecting = False
        self._clear_timeout()
        self._write_request()

    def _on_timeout(self):
        self._clear_timeout()
        msg = 'Connect timeout' if self._connecting else 'Request timeout'
        msg += ' %s' % str(self)
        self._on_error(exceptions.STPTimeoutError(msg))

    def _on_error(self, e=None):
        if isinstance(e, exceptions.STPError):
            err = e
        else:
            msg = str(self.stream.error) if self.stream is not None and self.stream.error is not None else str(e)
            err = exceptions.STPNetworkError('%s %s' % (msg, str(self)))
        self.close()
        self._request = None
        self._run_callback(STPResponse(request_time=time.time() - self.start_time, error=err))
        # reconnect and send remaining requests
        if len(self._request_queue) > 0:
            self._connect_and_write_request()

    def send_request(self, request, callback):
        self._request_queue.append((request, callback))
        self._connect_and_write_request()

    def _connect_and_write_request(self):
        if len(self._request_queue) > 0 and self._request is None:
            self._request, self._callback = self._request_queue.popleft()
            if self.closed:
                self._connect()
            elif not self._connecting:
                self._write_request()

    def _write_request(self):
        def write_callback():
            '''tornado needs it'''
            pass
        if self._request is None:
            return
        timeout = self.request_timeout
        if self._request.request_timeout is not None:
            timeout = self._request.request_timeout
        if timeout is not None and timeout > 0:
            self._timeout = self.io_loop.add_timeout(time.time() + timeout, self._on_timeout)
        self.start_time = time.time()
        try:
            self.stream.write(self._request.serialize(), write_callback)
            self._read_arg()
        except Exception as e:
            self._on_error(e)

    def _run_callback(self, response):
        if self._callback is not None:
            callback = self._callback
            self._callback = None
            callback(response)

    def _read_until(self, delimiter, callback):
        self.stream.read_until(delimiter, callback)

    def _read_bytes(self, size, callback):
        self.stream.read_bytes(size, callback)

    def _read_arg(self):
        try:
            self.io_loop.add_callback(functools.partial(self._read_until, b'\r\n', self._on_arglen))
        except Exception as e:
            self._on_error(e)

    def _on_arglen(self, data):
        if data == b'\r\n':
            response = self._response
            self._response = STPResponse()
            response.request_time = time.time() - self.start_time
            self._clear_timeout()
            self._run_callback(response)
            self._request = None
            self._connect_and_write_request()
        else:
            try:
                arglen = int(data[:-2])
                self.io_loop.add_callback(functools.partial(self._read_bytes, arglen, self._on_arg))
            except Exception as e:
                self._on_error(exceptions.STPProtocolError(str(e)))

    def _on_arg(self, data):
        self._response._argv.append(data)
        try:
            self.io_loop.add_callback(functools.partial(self._read_until, b'\r\n', self._on_strip_arg_eol))
        except Exception as e:
            self._on_error(e)

    def _on_strip_arg_eol(self, data):
        self._read_arg()

    def __str__(self):
        return '%s:%d' % (self.host, self.port) if self.unix_socket is None else self.unix_socket


def prepare_request(request):
    if not isinstance(request, STPRequest):
        if isinstance(request, list) or isinstance(request, tuple):
            request = STPRequest(list(request))
        else:
            request = STPRequest([request])
    return request


class AsyncClient(object):
    def __init__(self, host, port, timeout=-1, connect_timeout=-1, unix_socket=None, io_loop=None, max_buffer_size=104857600):
        self.host = host
        self.port = port
        self.unix_socket = unix_socket
        self.io_loop = io_loop or IOLoop.instance()
        self.max_buffer_size = max_buffer_size
        self.connection = Connection(self.host, self.port, self.io_loop, self.unix_socket, timeout, connect_timeout, self.max_buffer_size)

    @property
    def closed(self):
        return self.connection.closed

    def close(self):
        self.connection.close()

    def lazy_call(self, request):
        request = prepare_request(request)
        lresp = LazySTPResponse(self.io_loop)
        self.connection.send_request(request, lresp)
        return lresp

    def call(self, request, callback):
        request = prepare_request(request)
        self.connection.send_request(request, callback)

    def __str__(self):
        return 'Async STPClient to %s' % str(self.connection)


class Client(object):
    def __init__(self, host, port, timeout=None, connect_timeout=-1, unix_socket=None, max_buffer_size=104857600):
        def connect():
            self._io_loop = IOLoop()
            self._async_client = AsyncClient(host, port, timeout, connect_timeout, unix_socket, self._io_loop, max_buffer_size)
            self._response = None
        self._connect = connect
        self._response = None
        self._connect()

    @property
    def closed(self):
        return self._async_client is None

    def close(self):
        if self._async_client:
            self._async_client.close()
        self._io_loop.close()
        self._async_client = None
        self._io_loop = None
        self._response = None

    def call(self, request):
        if self.closed:
            self._connect()

        def callback(response):
            self._response = response
            self._io_loop.stop()
        self._async_client.call(request, callback)
        self._io_loop.start()
        response = self._response
        self._response = None
        try:
            response.rethrow()
        except:
            self.close()
            raise
        return response

    def __del__(self):
        self.close()

    def __str__(self):
        return 'STPClient to %s' % str(self._async_client.connection)

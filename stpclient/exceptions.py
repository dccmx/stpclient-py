#!/usr/bin/python
# coding: utf-8


class STPError(Exception):
    pass


class STPTimeoutError(STPError):
    pass


class STPNetworkError(STPError):
    pass


class STPProtocolError(STPError):
    pass

from stpclient.client import (
        AsyncClient,
        Client,
        STPReqeust,
        STPResponse,
        STPError,
        STPTimeoutError,
        STPNetworkError)

from stpclient.magicclient import MagicClient


__author__ = "dccmx <dccmx@dccmx.com>"
__version__ = "0.2"
__copyright__ = "Copyright (C) 2012 dccmx"
__license__ = "MIT"
__all__ = [
        'AsyncClient',
        'Client',
        'STPReqeust', 'STPResponse',
        'STPError', 'STPTimeoutError', 'STPNetworkError',
        'MagicClient'
        ]

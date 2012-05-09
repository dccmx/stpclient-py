#!/usr/bin/env python
import distutils.core

kwargs = {}

version = "0.1.0"

distutils.core.setup(
    name="stpclient",
    version=version,
    packages=["stpclient"],
    package_data={
        "stpclient": ["README.md"],
        },
    author="dccmx",
    author_email="dccmx@dccmx.com",
    url="http://simpletp.org",
    download_url="https://github.com/dccmx/stpclient/tarball/%s" % version,
    license="MIT",
    description="stpclient is an client lib that communicate with simpletp server",
    **kwargs
)

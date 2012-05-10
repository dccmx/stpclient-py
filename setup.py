#!/usr/bin/env python
import distutils.core


distutils.core.setup(
    name='stpclient',
    version='0.2.0',
    packages=['stpclient'],
    package_data={
        'stpclient': ['README.md'],
        },
    author='dccmx',
    author_email='dccmx@dccmx.com',
    url='http://simpletp.org',
    license='MIT',
    description='stpclient is an client lib that communicate with simpletp server'
)

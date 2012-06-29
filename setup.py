#!/usr/bin/env python
from setuptools import setup


setup(
    name='stpclient',
    version='0.3.1',
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

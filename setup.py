#!/usr/bin/env python
from setuptools import setup


setup(
    name='stpclient',
    version='0.5.8',
    packages=['stpclient'],
    package_data={
        'stpclient': ['README.md'],
    },
    install_requires=['tornado'],
    author='dccmx',
    author_email='dccmx@dccmx.com',
    url='http://simpletp.org',
    license='MIT',
    description='stpclient is an client lib that communicate with simpletp server'
)

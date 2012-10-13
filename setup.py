#/usr/bin/env python
import codecs
import os
import sys

from setuptools import setup, find_packages

version = '0.1'

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

setup(
    name='flixpy',
    version=version,
    description="A python API wrapper specificly designed to work with netflix's streaming API",
    long_description=read(os.path.join(os.path.dirname(__file__), 'README.markdown')),
    author='Chris Drackett',
    author_email='chris@shelfworthy.com',
    url='http://github.com/shelfworthy/flixpy',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests==0.14.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='api,netflix,streaming',
)

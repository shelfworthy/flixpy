import os
import sys

from setuptools import setup, find_packages

version = '0.1'

setup(
    name='python-netflix-streaming',
    version=version,
    description="A python API wrapper specificly designed to work with netflix's streaming API",
    long_description=read(os.path.join(os.path.dirname(__file__), 'README.markdown')),
    author='Chris Drackett',
    author_email='chris@shelfworthy.com',
    url='http://github.com/shelfworthy/python-netflix-streaming',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
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
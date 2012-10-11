from setuptools import setup, find_packages

version = '0.1'

setup(
    name='python-netflix-streaming',
    version=version,
    description="A python API wrapper specificly designed to work with netflix's streaming API",
    author='Chris Drackett',
    author_email='chris@shelfworthy.com',
    url='http://github.com/shelfworthy/python-textile',
    packages=find_packages(),
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
    include_package_data=True,
    zip_safe=False,
)

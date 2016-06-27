"""
Usage
``````
.. code:: python


    usage: freeproxy [-h] [-l] [-t] URL

    Get http proxies from some free proxy sites

    positional arguments:
      URL         The url for testing proxies. Like "https://www.google.com"

    optional arguments:
      -h, --help  show this help message and exit
      -l          Logging debug messages to a file
      -t          Test availability of proxies stored in db

Links
`````````
* `website <https://github.com/YieldNull/freeproxy>`_
"""

from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='freeproxy',

    # See https://packaging.python.org/en/latest/distributing/#choosing-a-versioning-scheme
    version='1.0.1',

    description='Get http proxies from some free proxy sites',
    long_description=__doc__,

    url='https://github.com/yieldnull/freeproxy',
    author='YieldNull',
    author_email='yieldnull@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='proxy spider',
    packages=['freeproxy'],
    platforms='any',
    install_requires=[
        'requests',
        'peewee',
        'gevent',
        'beautifulsoup4'
    ],

    entry_points={
        'console_scripts': [
            'freeproxy=freeproxy.client:main',
        ],
    },
)

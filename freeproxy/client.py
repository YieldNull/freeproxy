#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command line tool.

Created By YieldNull at 6/23/16
"""
from gevent import monkey

monkey.patch_socket()

import gevent
import os
import requests
import datetime
import random
import time
from gevent.pool import Pool
from peewee import SqliteDatabase, CharField, DateTimeField, Model, \
    FloatField, IntegrityError, IntegerField
from freeproxy import _headers, _user_agents, _home_dir, _log, fetch_proxies, enable_logging

# database
db = SqliteDatabase(os.path.join(_home_dir, 'proxy.db'))


class Proxy(Model):
    """
    Database Model
    """
    proxy = CharField(primary_key=True)  # "ip:port"
    check_time = DateTimeField(null=True)  # time of testing
    response_time = FloatField(null=True)  # response time
    status_code = IntegerField(null=True)  # status code

    class Meta:
        database = db


def init_db():
    db.create_table(Proxy, safe=True)


def store_in_db(proxy, escaped=None, status_code=None):
    """
    Store tested proxies in database
    :param proxy:  "ip:port"
    :param escaped:  response time
    :param status_code: status code. None if the testing URL is unreachable.
    """
    proxy = proxy.strip()
    try:
        try:
            Proxy.create(proxy=proxy, check_time=datetime.datetime.now(), response_time=escaped,
                         status_code=status_code)
        except IntegrityError:
            Proxy.update(check_time=datetime.datetime.now(), response_time=escaped,
                         status_code=status_code).where(Proxy.proxy == proxy).execute()
    except Exception as e:
        _log(e.args)


def test_proxies(proxies, timeout=10, single_url=None, many_urls=None, call_back=None):
    """
    Test proxies, or process html source using callback in the meantime.

    :type proxies: list
    :param proxies:  proxies
    :param timeout: response timeout
    :param single_url: The URL for testing
    :param many_urls: The list of URLs for testing. Pick one of them when perform request.
    :param call_back: Process the html source if status code is 200. callback(url, source)
    :return:
    """

    proxies = set(proxies)
    errors = set()
    pool = Pool(100)

    def test(proxy):
        code = None
        url = random.choice(many_urls) if many_urls is not None else single_url

        start_time = time.time()
        try:
            with gevent.Timeout(seconds=timeout, exception=Exception('[Connection Timeout]')):
                _headers['User-Agent'] = random.choice(_user_agents)

                res = requests.get(url,
                                   proxies={'http': 'http://{}'.format(proxy.strip()),
                                            'https': 'https://{}'.format(proxy.strip())},
                                   headers=_headers
                                   )
                code = res.status_code
                source = res.text

            _log('[Proxy: {:d} {:s}]'.format(code, proxy))

            # 回调
            if source is not None and call_back is not None and code == 200:
                call_back(url, source)

            if code != 200:
                errors.add(proxy)

        except Exception as e:
            # log(e.args)
            errors.add(proxy)

        end_time = time.time()
        escaped = end_time - start_time if code else None

        store_in_db(proxy, escaped=escaped, status_code=code)  # store in db

    for proxy in proxies:
        pool.spawn(test, proxy)
    pool.join()

    proxies = proxies - errors
    _log('[HTTP Proxies] Available:{:d} Deprecated:{:d}'.format(len(proxies), len(errors)))

    return list(proxies)


def test_instore(url):
    query = Proxy.select()
    proxies = [proxy.proxy for proxy in query]
    return test_proxies(proxies, single_url=url)


def main():
    import argparse
    import sys

    class DefaultParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n\n' % message)
            self.print_help()  # print help
            sys.exit(2)

    parser = DefaultParser(description='Get http proxies from some free proxy sites')

    parser.add_argument('-l', dest='logging', action='store_true',
                        help='Logging debug messages to a file')

    parser.add_argument('-t', dest='test', action='store_true',
                        help='Test availability of proxies stored in db')

    parser.add_argument('url', metavar='URL',
                        help='The url for testing proxies. Like "https://www.google.com"')

    args = parser.parse_args()

    if args.logging:
        enable_logging()

    if args.test:
        proxies = test_instore(args.url)
    else:
        init_db()
        proxies = test_proxies(fetch_proxies(), single_url=args.url)

    _log('Proxies amount: {:d}'.format(len(proxies)))


if __name__ == '__main__':
    main()

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

from gevent.pool import Pool

from peewee import SqliteDatabase, CharField, DateTimeField, Model, \
    FloatField, IntegrityError, IntegerField

from freeproxy import _headers, _user_agents, _home_dir, _log, fetch_proxies, enable_logging

# database
db = SqliteDatabase(os.path.join(_home_dir, 'proxy.db'))

class Proxy(Model):
    """
    数据库model
    """
    proxy = CharField(primary_key=True)  # ip:port
    check_time = DateTimeField(null=True)  # 测试时间
    response_time = FloatField(null=True)  # 响应时间
    status_code = IntegerField(null=True)  # 返回状态码

    class Meta:
        database = db


def store_in_db(proxy, escaped=None, status_code=None):
    """
    将测试过的proxy的信息存入数据库
    :param proxy:  port:ip
    :param escaped:  响应时间
    :param status_code: 返回码，为空则表示访问失败，proxy不可用
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
    测试代理。剔除响应时间大于timeout的代理

    或者在测试的同时进行数据处理 200则调用 call_back(url,source)
    :type proxies: list
    :param proxies:  代理列表
    :param timeout: 响应时间(s)
    :param single_url: 用作测试的url
    :param many_urls: 用作测试的url列表，测试时从中随机选取一个
    :param call_back: 处理测试url对应网页的源码,callback(url,source)
    :return:
    """

    proxies = set(proxies)
    errors = set()
    pool = Pool(100)

    def test(proxy):
        code = None
        url = random.choice(many_urls) if many_urls is not None else single_url

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

        store_in_db(proxy, status_code=code)  # 存

    for proxy in proxies:
        pool.spawn(test, proxy)
    pool.join()

    proxies = proxies - errors
    _log('[HTTP Proxies] Available:{:d} Deprecated:{:d}'.format(len(proxies), len(errors)))

    return list(proxies)


def test_instore(url):
    query = Proxy.select().where(~(Proxy.status_code >> None))
    proxies = [proxy.proxy for proxy in query]
    return test_proxies(proxies, single_url=url)


def main():
    import argparse
    import sys

    class DefaultParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n\n' % message)
            self.print_help()
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
        db.create_table(Proxy, safe=True)
        proxies = test_proxies(fetch_proxies(), single_url=args.url)

    _log('Proxies amount: {:d}'.format(len(proxies)))


if __name__ == '__main__':
    main()

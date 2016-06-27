# -*- coding: utf-8 -*-

"""
Get http proxies from some free proxy sites.

Created By YieldNull at 6/23/16
"""

import re
import random
import gevent
import requests

from time import sleep
from bs4 import BeautifulSoup

from freeproxy import _headers, _user_agents, _log


def _safe_http(url, data=None, session=None, proxies=None, timeout=10, want_obj=False):
    """
    Get the HTML source at url.
    :param url: url
    :param data: data of POST as dict
    :param session: send http requests in the session
    :param proxies: send http requests using proxies
    :param timeout: response timeout, default is 10s
    :param want_obj: return a response object instead of HTML source or not. Default is False.
    :return: The HTML source or response obj. If timeout or encounter exception, return '' or None(want_obj is set True).
    """
    try:
        _headers['User-Agent'] = random.choice(_user_agents)
        with gevent.Timeout(seconds=timeout, exception=Exception('[Connection Timeout]')):
            if data is None:
                res = requests.get(url, headers=_headers, proxies=proxies) if session is None \
                    else session.get(url, headers=_headers, proxies=proxies)
            else:
                res = requests.post(url, headers=_headers, data=data, proxies=proxies) if session is None \
                    else session.post(url, headers=_headers, data=data, proxies=proxies)

        code = res.status_code
        _log('[{:d}] {:s} {:s}'.format(code, 'POST' if data is not None else 'GET', url))

        if want_obj:
            return res
        else:
            return res.text if code == 200 else ''
    except Exception as e:
        # log(e.args)
        _log('[{:s}] {:s} {:s}'.format('HTTP Error', 'POST' if data is not None else 'GET', url))
        return None if want_obj else ''


def from_pachong_org():
    """
    From "http://pachong.org/"
    :return:
    """
    proxies = []

    urls = ['http://pachong.org/transparent.html',
            'http://pachong.org/high.html',
            'http://pachong.org/anonymous.html'
            ]
    for url in urls:
        sleep(0.5)
        res = _safe_http(url)

        # var duck=1159+2359
        m = re.search('var ([a-zA-Z]+)=(.*?);', res)
        if not m:
            return []

        var = {m.group(1): eval(m.group(2))}

        # var bee=6474+1151^duck;
        exprs = re.findall('var ([a-zA-Z]+)=(\d+)\+(\d+)\^([a-zA-Z]+);', res)

        for expr in exprs:
            var[expr[0]] = int(expr[1]) + int(expr[2]) ^ var[expr[3]]

        try:
            soup = BeautifulSoup(res, 'lxml')
        except:
            continue
        table = soup.find('table', class_='tb')

        for tr in table.find_all('tr'):
            data = tr.find_all('td')
            if len(data) != 7:
                continue

            ip = data[1].text

            if not re.match('\d+\.\d+\.\d+\.\d+', ip):
                continue

            # port=(15824^seal)+1327
            script = data[2].script.text
            expr = re.search('\((\d+)\^([a-zA-Z]+)\)\+(\d+)', script)

            port = (int(expr.group(1)) ^ var[expr.group(2)]) + int(expr.group(3))
            proxies.append('%s:%s' % (ip, port))
    proxies = list(set(proxies))
    return proxies


def from_cn_proxy():
    """
    From "http://cn-proxy.com/"
    :return:
    """
    urls = [
        'http://cn-proxy.com/archives/218',
        'http://cn-proxy.com/'
    ]
    proxies = []

    for url in urls:
        sleep(0.5)
        res = _safe_http(url)
        data = re.findall('<td>(\d+\.\d+\.\d+\.\d+)</td>.*?<td>(\d+)</td>', res, re.DOTALL)

        for item in data:
            proxies.append('%s:%s' % (item[0], item[1]))
    return proxies


def from_proxy_spy():
    """
    From "http://txt.proxyspy.net/proxy.txt"
    :return:
    """
    url = 'http://txt.proxyspy.net/proxy.txt'
    res = _safe_http(url)
    proxies = re.findall('(\d+\.\d+\.\d+\.\d+:\d+) .*', res)
    return proxies


def from_xici_daili():
    """
    From "http://www.xicidaili.com/"
    :return:
    """
    urls = [
        'http://www.xicidaili.com/nt/1',
        'http://www.xicidaili.com/nt/2',
        'http://www.xicidaili.com/nn/1',
        'http://www.xicidaili.com/nn/2',
        'http://www.xicidaili.com/wn/1',
        'http://www.xicidaili.com/wn/2',
        'http://www.xicidaili.com/wt/1',
        'http://www.xicidaili.com/wt/2'
    ]

    proxies = []
    for url in urls:
        sleep(4)
        res = _safe_http(url)
        data = re.findall('<td>(\d+\.\d+\.\d+\.\d+)</td>.*?<td>(\d+)</td>', res, re.DOTALL)
        proxies += ['{:s}:{:s}'.format(host, port) for (host, port) in data]
    return proxies


def from_hide_my_ip():
    """
    From "https://www.hide-my-ip.com/proxylist.shtml"
    :return:
    """
    url = 'https://www.hide-my-ip.com/proxylist.shtml'
    res = _safe_http(url)

    data = re.findall('"i":"(\d+\.\d+\.\d+\.\d+)","p":"(\d+)"', res)
    proxies = ['{:s}:{:s}'.format(host, port) for (host, port) in data]
    return proxies


def from_cyber_syndrome():
    """
    From "http://www.cybersyndrome.net/"
    :return:
    """
    urls = [
        'http://www.cybersyndrome.net/pld.html',
        'http://www.cybersyndrome.net/pla.html'
    ]

    proxies = []
    for url in urls:
        sleep(0.5)
        res = _safe_http(url)
        proxies += re.findall('(\d+\.\d+\.\d+\.\d+:\d+)', res)
    return proxies


def from_free_proxy_list():
    """
    From "http://free-proxy-list.net/"
    :return:
    """
    urls = [
        'http://www.us-proxy.org/',
        'http://free-proxy-list.net/uk-proxy.html'
    ]
    proxies = []

    for url in urls:
        sleep(0.5)
        res = _safe_http(url)
        data = re.findall('<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td>', res)
        proxies += ['{:s}:{:s}'.format(host, port) for (host, port) in data]
    return proxies


def from_gather_proxy():
    """
    From "http://www.gatherproxy.com"
    :return:
    """
    url_login = 'http://www.gatherproxy.com/subscribe/login'
    url_info = 'http://www.gatherproxy.com/subscribe/infos'
    url_download = 'http://www.gatherproxy.com/proxylist/downloadproxylist/?sid={:s}'

    session = requests.session()  # enable cookie

    # captcha like "Eight - 5"=?
    operand_map = {
        'Zero': 0, '0': 0,
        'One': 1, '1': 1,
        'Two': 2, '2': 2,
        'Three': 3, '3': 3,
        'Four': 4, '4': 4,
        'Five': 5, '5': 5,
        'Six': 6, '6': 6,
        'Seven': 7, '7': 7,
        'Eight': 8, '8': 8,
        'Nine': 9, '9': 9
    }
    operator_map = {
        'plus': '+', '+': '+',
        'multiplied': '*', 'X': '*',
        'minus': '-', '-': '-'
    }

    # get captcha
    res = _safe_http(url_login, session=session)
    m = re.search('Enter verify code: <span class="blue">(.*?) = </span>', res)
    if not m:
        return []

    calcu = m.group(1).strip()
    opers = calcu.split()
    if len(opers) != 3:
        return []

    operand1 = operand_map.get(opers[0])
    operator = operator_map.get(opers[1])
    operand2 = operand_map.get(opers[2])

    try:
        result = eval('{} {} {}'.format(operand1, operator, operand2))
    except:
        return []

    data = {
        'Username': 'jun-kai-xin@163.com',
        'Password': 'N}rS^>&3',
        'Captcha': result
    }

    # post to login and redirect to info page to get download `id`
    _safe_http(url_login, data=data, session=session)
    res = _safe_http(url_info, session=session)

    m = re.search('<p><a href="/proxylist/downloadproxylist/\?sid=(\d+)">Download', res)
    if m is None:
        return []

    data = {
        'ID': m.group(1),
        'C': '',
        'P': '',
        'T': '',
        'U': 90  # uptime
    }

    # post id to get proxy list
    res = _safe_http(url_download.format(m.group(1)), data=data, session=session)
    session.close()

    proxies = res.split('\n')  # split the txt file
    return proxies


def from_get_proxy():
    """
    From "http://www.getproxy.jp"
    :return:
    """
    base = 'http://www.getproxy.jp/proxyapi?' \
           'ApiKey=659eb61dd7a5fc509bef01f2e8b15669dfdb0f54' \
           '&area={:s}&sort=requesttime&orderby=asc&page={:d}'

    urls = [base.format('CN', i) for i in range(1, 25)]
    urls += [base.format('US', i) for i in range(1, 25)]
    urls += [base.format('CN', i) for i in range(25, 50)]
    urls += [base.format('US', i) for i in range(25, 50)]

    proxies = []

    i = 0
    retry = 0
    length = len(urls)
    while i < length:
        res = _safe_http(urls[i])
        try:
            soup = BeautifulSoup(res, 'lxml')
        except:
            i += 1
            continue

        data = soup.find_all('ip')
        if len(data) == 0:
            retry += 1
            if retry == 4:
                break
            else:
                sleep(62)
        else:
            retry = 0
            proxies += [pro.text for pro in data]
            i += 1
    return proxies


def fetch_proxies():
    """
    Get latest proxies from above sites.
    """
    functions = [
        from_cn_proxy,
        from_proxy_spy, from_xici_daili,
        from_hide_my_ip, from_cyber_syndrome,
        from_free_proxy_list, from_gather_proxy,
        from_get_proxy,
        from_pachong_org,
    ]

    proxies = []
    for func in functions:
        pro = func()
        _log('[{:s}] {:d} proxies'.format(func.__name__, len(pro)))
        proxies += pro
    return proxies

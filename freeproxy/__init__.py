# -*- coding: utf-8 -*-

"""
Get http proxies from some free proxy sites.

Created By YieldNull at 6/23/16
"""

import os
import logging
import requests

# http request headers
_headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
}

# http request user-agent
_user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36 OPR/36.0.2130.32',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 UBrowser/5.6.10551.6 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 4.4.4; HTC D820mt Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.91 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.0; Google Nexus 5 - 5.0.0 - API 21 - 1080x1920 Build/LRX21M) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
]

_use_logging = False
_logger = None

_home_dir = os.path.join(os.path.expanduser("~"), '.freeproxy')
if not os.path.exists(_home_dir):
    os.mkdir(_home_dir)

# Disable warning.
logging.getLogger("requests").setLevel(logging.ERROR)
requests.packages.urllib3.disable_warnings()


def _init_logger():
    from logging.handlers import RotatingFileHandler

    # logging file "~/.freeproxy/freeproxy.log"
    log_file = os.path.join(_home_dir, 'freeproxy.log')

    # logger config
    handler = RotatingFileHandler(log_file, mode='a', maxBytes=50 * 1024 * 1024, backupCount=2)
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    handler.setLevel(logging.INFO)

    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


def _log(msg):
    if _use_logging and _logger:
        _logger.info(msg)
    else:
        print(msg)


def enable_logging():
    global _use_logging
    _use_logging = True


from .proxy import from_cn_proxy, from_cyber_syndrome, from_free_proxy_list, from_gather_proxy, from_get_proxy, \
    from_hide_my_ip, from_pachong_org, from_proxy_spy, from_xici_daili, fetch_proxies

from client import Proxy, test_proxies, init_db


def read_proxies():
    query = Proxy.select().where(Proxy.status_code == 200)
    return [p.proxy for p in query]

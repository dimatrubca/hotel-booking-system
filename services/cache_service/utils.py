
from datetime import datetime, timedelta
from threading import Thread
from typing import List, Optional

from models import CacheRequest, CachedResponse
from settings import DEFAULT_EXPIRATION_TIME

import functools
import logging
import settings
import requests
import data_store

logger = logging.getLogger(__name__)


def parse_query(query: str):
    if query is None:
        return None #todo: raise exception, return error

    tokens = query.split()

    if len(tokens) != 2:
        raise Exception("Invalid query (2 tokens required)")

    if tokens[0] != 'GET':
        raise Exception("Invalid query (must start with GET)")

    urls = tokens[1].split('|')
    urls = [url if url.endswith('/') else url + '/' for url in urls]

    return urls


def parse_url(url):
    if not url.endswith('/'):
        url = url + '/'

    service_domain, path = url.split('/', maxsplit=1)

    return service_domain, path


def get_responses(urls: List[str]):
    result = {}

    for url in urls:
        service_domain, path = parse_url(url)

        response = data_store.get(service_domain, path)

        if response is None:
            cached_response = CachedResponse(success=False)
        else:    
            cached_response = CachedResponse(success=True, response=response)

        result[url] = cached_response

    logger.info(f"get_responses: {result}")

    return result


# todo: solve header not passing as list
def add_to_cache(cache_params: CacheRequest, cache_control_header: Optional[List[str]]):
    expires_in = DEFAULT_EXPIRATION_TIME
    
    if not cache_params.url.endswith('/'):
        cache_params.url = cache_params.url + '/'

    if cache_control_header != None:
        if 'private' in cache_control_header:
            raise Exception("Private cache")

        max_age_list = list(filter(lambda x: x.startswith('max-age'), cache_control_header))
        print(cache_control_header)
        
        if len(max_age_list) >= 1:
            logger.info(f"Expiration time: {max_age_list[0][8:]}")

            expires_in = int(max_age_list[0][8:])
        else:
            logger.info("No max-age cache control value, using default value")

    service_domain, path = parse_url(cache_params.url)
    expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)

    logger.info(f"Adding to cache, url={cache_params.url}, data={cache_params.data}, expiration_time={expiration_time}")

    data_store.add(service_domain, path, expiration_time, cache_params.data)



def register_on_service_discovery():
    result = requests.post(settings.SERVICE_DISCOVERY + 'register', json = {
        'service_id': settings.SERVICE_ID,
        'name': settings.SERVICE_NAME,
        'port': settings.PORT
    })
    
    logger.info(f"register_service_discovery: {result.status_code}")


def unregister_on_service_discovery():
    result = requests.post(settings.SERVICE_DISCOVERY + 'unregister', json = {
        'service_id': settings.SERVICE_ID,
    })
    
    logger.info(f"unregister_service_discovery: {result.status_code}")


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco
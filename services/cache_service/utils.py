
from datetime import datetime, timedelta
import json
from threading import Thread, Timer
from typing import List, Optional

import asyncio
import aiohttp

from models import CacheRequest, CachedResponse
from config import settings
from bully import Bully

import functools
import logging
from config import settings
import requests
import data_store
from schemas import Event

logger = logging.getLogger(__name__)


def parse_query(query: str):
    if query is None:
        return None #todo: raise exception, return error

    tokens = query.split()

    if len(tokens) != 3:
        raise Exception("Invalid query (2 tokens required)")

    if tokens[0] != 'GET':
        raise Exception("Invalid query (must start with GET)")

    service_name = tokens[1]
    urls = tokens[2].split('|')
    urls = [url if url.endswith('/') else url + '/' for url in urls]

    return service_name, urls


def parse_url(url):
    if not url.endswith('/'):
        url = url + '/'

    service_domain, path = url.split('/', maxsplit=1)

    return service_domain, path


# todo: tackle service_domain redundancy
def get_responses(service_name, urls: List[str]):
    result = {}

    for url in urls:
        service_domain, path = parse_url(url)

        response = data_store.get(service_name, path)

        if response is None:
            cached_response = CachedResponse(success=False)
        else:    
            cached_response = CachedResponse(success=True, response=response)

        result[url] = cached_response

    logger.info(f"get_responses: {result}")

    return result


# todo: solve header not passing as list
def add_to_cache(cache_params: CacheRequest, cache_control_header: Optional[List[str]]):
    expires_in = settings.DEFAULT_EXPIRATION_TIME
    
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

    data_store.add(cache_params.service_name, path, expiration_time, cache_params.data)


def get_events_by_offset_start(start_offset):
    backlog = data_store.get_backlog()

    start_index = list(x['offset'] == start_offset for x in backlog).index(True)
    
    events = backlog[start_index:]

    return events



def register_on_service_discovery():
    # return
    result = requests.post(settings.SERVICE_DISCOVERY + 'register', json = {
        'service_id': settings.SERVICE_ID,
        'name': settings.SERVICE_NAME,
        'port': settings.PORT
    })
    print({
        'service_id': settings.SERVICE_ID,
        'name': settings.SERVICE_NAME,
        'port': settings.PORT
    })
    
    logger.info(f"register_service_discovery: {result.status_code}")


def unregister_on_service_discovery():
    # return
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


async def fetch(session, url):
    async with session.get(url) as response:
        return response


async def fetch_all(urls, loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        results = await asyncio.gather(*[fetch(session, url) for url in urls], return_exceptions=True)
     
        return results


async def post_json(session, url, data_json):
    logger.info(f"Post_json to: {url}, data={data_json}")
    async with session.post(url, json=data_json) as response:
        return response


async def post_json_all(urls, data_list, loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        results = await asyncio.gather(*[post_json(session, url, data) for url, data in zip(urls, data_list)], return_exceptions=True)# todo: set to true, handle excpeptions outside

        return results


def fire_event(event):
    response = requests.get(settings.SERVICE_DISCOVERY_CACHE_URL)
    json_response = response.json()
    nodes = {}

    for node in json_response:
        nodes[node['id']] = 'http://' f'{node["host"]}:{node["port"]}' #todo: add htttp to host while registering
        print(f"queried cache nodes from service_discovery:\n")

    nodes.pop(settings.SERVICE_ID, None)
    urls = list(nodes.values())
    urls = [x + '/update' for x in urls]

    json_event = json.dumps(event, indent=4, sort_keys=True, default=str)

    logger.info(f"firing event {json_event} to {urls}")

    for url in urls:
        try:

            requests.post(url, data=json_event, timeout=0.0000000001)
        except requests.exceptions.ReadTimeout: 
            pass

    # loop = asyncio.get_event_loop()
    # _ = await post_json_all(urls, [event] * len(urls), loop) 


def process_event(event: Event):
    # todo: check event send by coordinator, check replication id matches
    # todo: check fields, if add requiers expiration time
    data_store.process_event(event)
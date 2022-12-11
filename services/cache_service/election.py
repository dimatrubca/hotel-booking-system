

import asyncio
import logging
import socket
import time
import uuid
import aiohttp
from threading import Timer

import requests
from bully import Bully
from config import settings

from utils import fetch_all, post_json_all
import data_store

logger = logging.getLogger(__name__)

async def send_victory_messages(urls):
    urls = [url + '/announce_victory' for url in urls]
    print(f'sending victory messages to urls: {urls}')
    loop = asyncio.get_event_loop()

    results  = await post_json_all(urls, [{
        'host': f'http://{socket.gethostbyname(socket.gethostname())}:{settings.PORT}',
        'replication_id': data_store.get_replication_id(),
        'offset': data_store.get_replication_offset(),
        'secondary_id': data_store.get_secondary_id(),
        'secondary_offset': data_store.get_secondary_offset()       
    }] * len(urls), loop) # await>??? todo: check

    return results


async def send_election_messages(urls):
    urls = [url + '/election' for url in urls] # todo: check urls
    print(f'sending election messages to urls: {urls}')
    loop = asyncio.get_event_loop()

    results = await post_json_all(urls, [{
        'replication_id': data_store.get_replication_id(),
        'replication_offset': data_store.get_replication_offset(),
        'node_id': settings.SERVICE_ID
    }] * len(urls), loop)

    return results


async def heart_beat_leader(bully: Bully):
    logger.info("Entering heart_beating leader loop")

    while True:
        logger.info("Before sleep")
        await asyncio.sleep(4) # todo: parametarize
        
        logger.info("Heart-beating leader...")
        logger.info(f"Leader: {bully.coordinator}")
        

        if not bully.election and bully.coordinator != True and bully.coordinator != None:
            loop = asyncio.get_event_loop()

            try:
                async with aiohttp.ClientSession(loop=loop) as session:
                    async with session.get(bully.coordinator + '/status') as response:
                        print(response.status) 
            except Exception as e:
                print(type(e))
                logger.info(f"Heart-beating failed, error: {e}")

                asyncio.create_task(init_election(bully))
                # init_election


async def check_victory_message_received(bully: Bully):
    timestamp = time.time()

    await asyncio.sleep(5)

    if bully.last_leader_change_timestamp and bully.last_leader_change_timestamp - timestamp < 5:
        logger.info("Victory was registered...")
        bully.election = False # todo: check placement
        return

    logger.info("Victory wasn't registered, timeout passed")
    bully.election = False

    await init_election(bully)


async def self_elect_as_leader(bully: Bully, other_nodes):
    bully.coordinator = True
    bully.election = False

    data_store.on_become_leader()

    results = await send_victory_messages(other_nodes)

    logger.info(f"self_elect_as_leader results: {results}")


async def init_election(bully: Bully):
    logger.info('init_election, starting...')
    
    if bully.election:
        return

    bully.election = True

    if not bully.heart_beating_leader:
        bully.heart_beating_leader = True

        asyncio.create_task(heart_beat_leader(bully))

    response = requests.get(settings.SERVICE_DISCOVERY_CACHE_URL)
    json_response = response.json()
    nodes = {}

    print(f"service discovery response: {json_response}")

    for node in json_response:
        nodes[node['id']] = 'http://' f'{node["host"]}:{node["port"]}' #todo: add htttp to host while registering
        print(f"queried cache nodes from service_discovery:\n")

    # higher_id_nodes = [ nodes[node_id] for node_id in nodes if node_id > settings.SERVICE_ID ]
    # lower_id_nodes = [ nodes[node_id] for node_id in nodes if node_id < settings.SERVICE_ID ]
    other_nodes = [ nodes[node_id] for node_id in nodes if node_id != settings.SERVICE_ID ]

    if len(other_nodes) == 0:
        await self_elect_as_leader(bully, other_nodes)

        return

    results = await send_election_messages(other_nodes)
    print("results:", results)
    is_success_any = any([r.ok for r in results if isinstance(r, aiohttp.client_reqrep.ClientResponse)])

    if is_success_any == False:
        await self_elect_as_leader(bully, other_nodes)
    else:
        # election failed, try again later
        asyncio.create_task(check_victory_message_received(bully))

import asyncio
import logging
import random
import time
from typing import Optional, List
from fastapi.responses import RedirectResponse

from fastapi import FastAPI, Header, Body, HTTPException, Query
from fastapi import status
import requests
import uvicorn
from models import CacheRequest
from starlette.responses import Response
from schemas import ElectionMessage, Event, LeaderUpdated

from utils import add_to_cache, parse_query, get_responses, process_event, register_on_service_discovery, unregister_on_service_discovery, get_events_by_offset_start
from election import init_election

from config import settings
from bully import bully

import data_store
from fastapi.middleware.cors import CORSMiddleware
import socket

# __import__('IPython').embed()

logging.basicConfig(
                    filename='logs/server.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

format = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(format)

logging.getLogger().addHandler(handler)

                    
logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def init_election_delayed(delay): 
    await asyncio.sleep(delay)
    logger.info(f"running on port {settings.PORT}... (sd)")
    register_on_service_discovery()

    await init_election(bully)

    return
    logger.info("sending...")

    response = requests.get(settings.SERVICE_DISCOVERY_CACHE_URL)
    json_response = response.json()
    nodes = {}

    logger.info(f"service discovery response: {json_response}")

    for node in json_response:
        if str(node['port']) == str(settings.PORT):
            continue
        
        nodes[node['id']] = 'http://' f'{node["host"]}:{node["port"]}' #todo: add htttp to host while registering

    logger.info(f"Nodes: {nodes}")
    logger.info(f"Node items: {nodes.items()}")

    for key, url in nodes.items():
        logger.info(f"sending request to: {url}")

        try:
            result = requests.get(f'{url}/status')
        except Exception as e:
            print(f"Exception sending request: {e}")

        logger.info(f"result url {url}: {result.status_code}")


@app.on_event("startup")
async def check_services_activity_task() -> None:
    

    delay = random.randint(5, 30)
    asyncio.create_task(init_election_delayed(delay))


@app.on_event("shutdown")
def shutdown_event():
    unregister_on_service_discovery()


@app.get("/request")
async def send_request():
    response = requests.get(settings.SERVICE_DISCOVERY_CACHE_URL)
    json_response = response.json()
    nodes = {}

    logger.info(f"service discovery response: {json_response}")

    for node in json_response:
        if str(node['port']) == str(settings.PORT):
            continue
        
        nodes[node['id']] = 'http://' f'{node["host"]}:{node["port"]}' #todo: add htttp to host while registering

    logger.info(f"Nodes: {nodes}")
    logger.info(f"Node items: {nodes.items()}")

    for key, url in nodes.items():
        logger.info(f"sending request to: {url}")

        try:
            result = requests.get(f'{url}/status')
            logger.info(f"result url {url}: {result.status_code}")
        except Exception as e:
            print(f"Exception sending request: {e}")

        


@app.get("/status")
def get_status():
    return Response(status_code=status.HTTP_200_OK)


@app.post('/update')
def update(event: Event = Body()):
    # todo: check coordinator sent message
    process_event(event)
    
    return Response(status_code=status.HTTP_200_OK)


@app.post("/announce_victory")
def anounce_victory(leader_info:LeaderUpdated = Body()):
    logger.info(f"victory announced, node: {leader_info.host}")

    bully.coordinator = leader_info.host
    bully.election = False # ?
    bully.last_leader_change_timestamp = time.time()

    # todo: sync data
    # logger.info("requesting copy from:" + f'{leader_info.host}/full_copy')

    # r = requests.get(f'{leader_info.host}/full_copy')
    # state_copy = r.content

    data_store.on_leader_updated(leader_info.host, leader_info.replication_id,\
        leader_info.offset, leader_info.secondary_id, leader_info.secondary_offset)
    # data_store.update_state_from_copy(state_copy)

    logger.info("success, announce_victory")

    return Response(status_code=status.HTTP_200_OK)


@app.post("/election")
async def election(election_message: ElectionMessage):
    # start election in new thread
    if election_message.replication_id == data_store.get_replication_id():
        if election_message.replication_offset > data_store.get_replication_offset() or \
            election_message.replication_offset == data_store.get_replication_offset() and election_message.node_id > settings.SERVICE_ID:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        if election_message.replication_offset > data_store.get_replication_offset() or\
            (election_message.node_id > settings.SERVICE_ID and election_message.replication_offset == data_store.get_replication_offset()):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

    if bully.election == False:
        asyncio.create_task(init_election(bully))


    return Response(status_code=status.HTTP_200_OK)

from fastapi.responses import Response

@app.get("/full_copy")
def request_full_copy():
    copy = data_store.get_copy()

    return Response(content=copy)


@app.get("/events")
def request_events_by_offset_start(start: int = Query()):
    events = get_events_by_offset_start(start)

    return events

    
@app.get("/")
def get_cache(query: str = Query()):
    logger.info(f"get cache: {query}!")

    # raise HTTPException(status_code=400, detail=str(e))
    try:
        service_name, urls = parse_query(query)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

    response = get_responses(service_name, urls)

    return response


@app.post("/")
def cache(cache_params: CacheRequest, cache_control: Optional[List[str]] = Header(None)):
    # logger.info(cache_params)
    if bully.coordinator == None: # todo: rename coordinator to leader
        return 'error... no leader'

    if bully.coordinator != True:
        response = RedirectResponse(bully.coordinator)

        return response

    try:
        add_to_cache(cache_params, cache_control)
    except ValueError as e:
        raise HTTPException(status_code=400, detail='max-age not int')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {'success': True}


if __name__ == "__main__":
    logger.info(f"running on port {settings.PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)

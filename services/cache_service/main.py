import asyncio
import logging
import time
from typing import Optional, List
from fastapi.responses import RedirectResponse

from fastapi import FastAPI, Header, Body, HTTPException, Query
from fastapi import status
import uvicorn
from models import CacheRequest
from starlette.responses import Response
from schemas import Event

from utils import add_to_cache, parse_query, get_responses, register_on_service_discovery, unregister_on_service_discovery, get_events_by_offset_start
from election import init_election

from config import settings
from bully import bully

# __import__('IPython').embed()

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(message)s', datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)

app = FastAPI()


async def init_election_delayed(delay):
    await asyncio.sleep(delay)
    await init_election(bully)


@app.on_event("startup")
async def check_services_activity_task() -> None:
    register_on_service_discovery()

    asyncio.create_task(init_election_delayed(5))


@app.on_event("shutdown")
def shutdown_event():
    unregister_on_service_discovery()


@app.get("/status")
def get_status():
    return Response(status_code=status.HTTP_200_OK)


@app.post('/update')
def update(event: Event = Body(embed=True)):
    # todo: check coordinator sent message
    
    pass


@app.post("/announce_victory")
def anounce_victory(node_id: str = Body(embed=True)):
    logger.info(f"victory announced, node: {node_id}")

    bully.coordinator = node_id
    bully.election = False # ?
    bully.last_leader_change_timestamp = time.time()

    # todo: sync data

    return Response(status_code=status.HTTP_200_OK)


@app.post("/election")
async def election():
    # start election in new thread
    if bully.election == False:
        asyncio.create_task(init_election(bully))


    return Response(status_code=status.HTTP_200_OK)


@app.get("/events")
def request_events_by_offset_start(start: int = Query()):
    events = get_events_by_offset_start(start)

    return events

    
@app.get("/")
def get_cache(query: str = Query()):
    logger.info(f"get cache: {query}")
    try:
        urls = parse_query(query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = get_responses(urls)

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

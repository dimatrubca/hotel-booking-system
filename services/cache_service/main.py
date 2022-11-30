import logging
from typing import Optional, List

from fastapi import FastAPI, Header, Body, HTTPException, Query
from models import CacheRequest
from starlette.responses import Response

from utils import add_to_cache, parse_query, get_responses, register_on_service_discovery, unregister_on_service_discovery

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(message)s', datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
def check_services_activity_task() -> None:
    register_on_service_discovery()
    

@app.on_event("shutdown")
def shutdown_event():
    unregister_on_service_discovery()

    
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

    try:
        add_to_cache(cache_params, cache_control)
    except ValueError as e:
        raise HTTPException(status_code=400, detail='max-age not int')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {'success': True}
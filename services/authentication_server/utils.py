import logging
import requests
import settings

logger = logging.getLogger(__name__)

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

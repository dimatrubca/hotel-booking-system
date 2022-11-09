import requests
import settings
import logging

logger = logging.getLogger(__name__)

def register_on_service_discovery():
    result = requests.post(settings.SERVICE_DISCOVERY + 'register', json = {
        'service_id': settings.SERVICE_ID,
        'name': settings.SERVICE_NAME,
        'port': settings.PORT
    })
    
    logger.info(f"register_service_discovery: {result.status_code}")
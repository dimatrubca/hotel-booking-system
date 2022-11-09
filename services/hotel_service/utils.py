import functools
import threading
import requests
import settings
import logging

logger = logging.getLogger(__name__)

def register_on_service_discovery():
    result = requests.post(settings.SERVICE_DISCOVERY + 'register', json = {
        'service_id': settings.SERVICE_ID,
        'name': settings.SERVICE_NAME
    })
    
    logger.info(f"register_service_discovery: {result.status_code}")


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

            t = threading.Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret

            return ret
        return wrapper
    return deco
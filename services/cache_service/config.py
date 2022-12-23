from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

# sid = os.getenv('SERVICE_ID')
# print('...\n',sid,'...\n\n\n')

class Settings(BaseSettings):
    DEFAULT_EXPIRATION_TIME = 180*2

    SERVICE_DISCOVERY = "http://service_discovery:8005/"
    SERVICE_DISCOVERY_CACHE_URL = "http://service_discovery:8005/services/cache"

    # SERVICE_DISCOVERY = "http://localhost:8005/"
    # SERVICE_DISCOVERY_CACHE_URL = "http://localhost:8005/services/cache"
    SERVICE_NAME = "cache"

    # SERVICE_ID: str
    # PORT: int
    SERVICE_ID = "cache3"
    PORT = 8024


settings = Settings()
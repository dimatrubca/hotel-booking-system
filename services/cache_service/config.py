from pydantic import BaseSettings

class Settings(BaseSettings):
    DEFAULT_EXPIRATION_TIME = 30

    SERVICE_ID = "cache1"
    PORT = 8004

    SERVICE_DISCOVERY = "http://localhost:8005/"
    SERVICE_DISCOVERY_CACHE_URL = "http://localhost:8005/services/cache"
    SERVICE_NAME = "cache"



settings = Settings()
from .config import Settings
from functools import lru_cache
from fastapi.templating import Jinja2Templates
import httpx

@lru_cache
def get_settings():
    return Settings()

class HTTPXClientWrapper:
    
    async_client = None
    
    def start(self):
        """ Instantiate the client. Call from the FastAPI startup hook."""
        self.async_client = httpx.AsyncClient()
        
    async def stop(self):
        """ Gracefully shutdown. Call from FastAPI shutdown hook."""
        await self.async_client.aclose()
        self.async_client = None
        
    def __call__(self):
        """ Calling the instantiated HTTPXClientWrapper returns the wrapped singleton."""
        # Ensure we don't use it if not started / running
        assert self.async_client is not None
        return self.async_client
    
httpx_client_wrapper = HTTPXClientWrapper()
templates = Jinja2Templates(directory='templates')
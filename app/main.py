from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore

from .routers import inv, pwc
from .utils import *
from .models import DataManager, Document
from .constants import *

jobstores = {
    'default': MemoryJobStore()
}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone='Asia/Kuala_Lumpur')
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    httpx_client_wrapper.start()
    scheduler.start()
    await get_token()
    await get_token_pwc()
    yield
    await httpx_client_wrapper.stop()
    scheduler.shutdown()
    
templates = Jinja2Templates(directory='templates')
app = FastAPI(dependencies=[], title='App', description='App API description', version='1.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*'],
)

app.include_router(inv.router)
app.include_router(pwc.router)

async def get_token():
    cli = httpx_client_wrapper()
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded'
    # }
    settings = get_settings()
    data = {
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'grant_type': 'client_credentials',
        'scope': 'InvoicingAPI'
    }
    res = await cli.post(f'{settings.api_base_url}/connect/token', data=data)
    m = res.json()
    DataManager.access_token = m.get('access_token')
    print(DataManager.access_token)
    print('===')
    
async def get_token_pwc():
    cli = httpx_client_wrapper()
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded'
    # }
    settings = get_settings()
    data = {
        'client_id': settings.client_id_pwc,
        'client_secret': settings.client_secret_pwc,
        'grant_type': 'client_credentials',
        'scope': settings.scope_pwc
    }
    res = await cli.post(f'{settings.api_base_url_pwc}/oauth2/v2.0/token', data=data)
    m = res.json()
    DataManager.access_token_pwc = m.get('access_token')
    print(DataManager.access_token_pwc)
    print('===')

@scheduler.scheduled_job('interval', minutes=50)
async def interval_task_test():
    await get_token()
    
@scheduler.scheduled_job('interval', minutes=50)
async def interval_task_test_pwc():
    await get_token_pwc()
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from .constants import *
import httpx, jinja2, json, hashlib, base64

class DataManager:
    
    access_token = None

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
jobstores = {
    'default': MemoryJobStore()
}
scheduler = AsyncIOScheduler(jobstores=jobstores)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    httpx_client_wrapper.start()
    scheduler.start()
    await get_token()
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

async def get_token():
    cli = httpx_client_wrapper()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'InvoicingAPI'
    }
    res = await cli.post(f'{API_BASE_URL}/connect/token', headers=headers, data=data)
    m = res.json()
    DataManager.access_token = m.get('access_token')
    return DataManager.access_token

@scheduler.scheduled_job('interval', seconds=50)
async def interval_task_test():
    s = await get_token()
    print(s)

@app.get('/login')
async def login():
    cli = httpx_client_wrapper()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'InvoicingAPI'
    }
    res = await cli.post(f'{API_BASE_URL}/connect/token', headers=headers, data=data)
    m = res.json()
    DataManager.access_token = m.get('access_token')
    return m

@app.get('/validate')
async def validate():
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}'
    }
    prm = {
        'idType': 'BRN',
        'idValue': '200201024235'
    }
    res = await cli.get(f'{API_BASE_URL}/api/v1.0/taxpayer/validate/C10924204010', headers=headers, params=prm)
    if res.status_code == 200:
        return 'success'
    
    return 'fail'

@app.get('/documentsubmissions')
async def documentsubmissions():
    # S79HNH3XM3CBA7Y1FB1GPNYH10
    data = {
        'inv': 'INV1234594',
        'issue_date': '2024-05-23',
        'tin': TIN,
        'brn': BRN
    }
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template('invoice.json.jinja2')
    s = template.render(data)
    
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}'
    }
    x = hashlib.sha256(s.encode('utf-8')).hexdigest()
    d = s.encode('utf-8')
    c = base64.b64encode(d)
    v = c.decode('utf-8')
    fx = {
        'documents': [
            {
                'format': 'JSON',
                'document': v,
                'documentHash': x,
                'codeNumber': 'codenumINV1234594'
            }
        ]
    }
    res = await cli.post(f'{API_BASE_URL}/api/v1.0/documentsubmissions', headers=headers, json=fx)
    return res.json()

@app.get('/getsubmission/:submissionUid')
async def getsubmission(submissionUid: str):
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}'
    }
    res = await cli.get(f'{API_BASE_URL}/api/v1.0/documentsubmissions/{submissionUid}', headers=headers)
    return res.json()

@app.get('/documenttypes')
async def documenttypes():
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}'
    }
    res = await cli.get(f'{API_BASE_URL}/api/v1.0/documenttypes', headers=headers)
    return res.json()

@app.get('/datax')
async def test():
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template('data.json.jinja2')
    outputText = template.render({"name": 'ben'})
    return json.loads(outputText)

@app.get('/data', response_class=FileResponse)
async def data(req: Request):
    return templates.TemplateResponse(
        request=req, name='data.json.jinja2', context={"name": 'ben'},
        media_type='application/json',
        headers={
            'Content-disposition': 'attachment; filename=data.json',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'filename': 'data.json'
        }
    )
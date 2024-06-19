from fastapi import Depends, FastAPI, Request, APIRouter
from fastapi.responses import FileResponse
from typing import Annotated

from app.utils import *
from app.models import DataManager, Document
from app.config import Settings
from app.constants import *

import jinja2, json

router = APIRouter(tags=['inv'], prefix='/inv')

@router.get('/login')
async def login(settings: Annotated[Settings, Depends(get_settings)]):
    cli = httpx_client_wrapper()
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded'
    # }
    data = {
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'grant_type': 'client_credentials',
        'scope': 'InvoicingAPI'
    }
    res = await cli.post(f'{settings.api_base_url}/connect/token', data=data)
    m = res.json()
    DataManager.access_token = m.get('access_token')
    return m

@router.get('/validate')
async def validate(settings: Annotated[Settings, Depends(get_settings)]):
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}'
    }
    prm = {
        'idType': 'BRN',
        'idValue': '200201024235'
    }
    res = await cli.get(f'{settings.api_base_url}/api/v1.0/taxpayer/validate/C10924204010', headers=headers, params=prm)
    if res.status_code == 200:
        return 'success'
    
    return 'fail'

@router.get('/documentsubmissions')
async def documentsubmissions(settings: Annotated[Settings, Depends(get_settings)]):
    # S79HNH3XM3CBA7Y1FB1GPNYH10
    data = {
        'inv': 'INV1234598',
        'issue_date': '2024-05-28',
        'tin': settings.tin,
        'brn': settings.brn
    }
    templateLoader = jinja2.FileSystemLoader(searchpath='./templates')
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template('invoice.xml.jinja2')
    s = template.render(data)
    doc = Document(s)
    
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}'
    }
    fx = {
        'documents': [
            doc.getDoc('INV1234598')
        ]
    }
    res = await cli.post(f'{settings.api_base_url}/api/v1.0/documentsubmissions', headers=headers, json=fx)
    return res.json()

@router.get('/getsubmission/:submissionUid')
async def getsubmission(submissionUid: str, settings: Annotated[Settings, Depends(get_settings)]):
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}'
    }
    res = await cli.get(f'{settings.api_base_url}/api/v1.0/documentsubmissions/{submissionUid}', headers=headers)
    return res.json()

@router.get('/documenttypes')
async def documenttypes(settings: Annotated[Settings, Depends(get_settings)]):
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}'
    }
    res = await cli.get(f'{settings.api_base_url}/api/v1.0/documenttypes', headers=headers)
    return res.json()

@router.get('/datax')
async def test():
    templateLoader = jinja2.FileSystemLoader(searchpath='./templates')
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template('data.json.jinja2')
    outputText = template.render({"name": 'ben'})
    return json.loads(outputText)

@router.get('/data', response_class=FileResponse)
async def data(req: Request, settings: Annotated[Settings, Depends(get_settings)]):
    prm = {
        'inv': 'INV1234595',
        'issue_date': '2024-05-25',
        'tin': settings.tin,
        'brn': settings.brn
    }
    return templates.TemplateResponse(
        request=req, name='invoice.xml.jinja2', context=prm,
        media_type='application/xml',
        headers={
            'Content-disposition': 'attachment; filename=invoice.xml',
            'Content-Type': 'application/xml',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'filename': 'invoice.xml'
        }
    )
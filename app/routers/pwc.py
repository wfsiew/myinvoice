from fastapi import FastAPI, Request, Response, APIRouter, Depends, HTTPException, status
from typing import Annotated

from app.utils import *
from app.models import DataManager
from app.config import Settings

import base64, jinja2, traceback

router = APIRouter(tags=['pwc'], prefix='/pwc')

@router.get('/login')
async def login(settings: Annotated[Settings, Depends(get_settings)]):
    cli = httpx_client_wrapper()
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded'
    # }
    data = {
        'client_id': settings.client_id_pwc,
        'client_secret': settings.client_secret_pwc,
        'grant_type': 'client_credentials',
        'scope': settings.scope_pwc
    }
    res = await cli.post(f'{settings.api_base_url_pwc}/oauth2/v2.0/token', data=data)
    m = res.json()
    DataManager.access_token_pwc = m.get('access_token')
    return m

@router.post('/submission/new')
async def submissions(response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Content-Type': 'application/xml',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0',
            'ErpId': 'wf002'
        }
        doc = '''<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>INV1234567_v001</cbc:ID>
        <cbc:IssueDate>2024-06-01</cbc:IssueDate>
        <cbc:IssueTime>04:30:00Z</cbc:IssueTime>
        <cbc:InvoiceTypeCode listVersionID="1.0">01</cbc:InvoiceTypeCode>
        <cbc:DocumentCurrencyCode>MYR</cbc:DocumentCurrencyCode>
        <cac:InvoicePeriod>
            <cbc:StartDate>2017-11-26</cbc:StartDate>
            <cbc:EndDate>2017-11-30</cbc:EndDate>
            <cbc:Description>Monthly</cbc:Description>
        </cac:InvoicePeriod>
        <cac:AccountingSupplierParty>
            <cbc:AdditionalAccountID schemeAgencyName="CertEX">CPT-CCN-W-211111-KL-000002</cbc:AdditionalAccountID>
            <cac:Party>
                <cbc:IndustryClassificationCode name="Growing of maize">01111</cbc:IndustryClassificationCode>
                <cac:PartyIdentification>
                    <cbc:ID schemeID="TIN">C1865789030</cbc:ID>
                </cac:PartyIdentification>
                <cac:PartyIdentification>
                    <cbc:ID schemeID="BRN">199801008604</cbc:ID>
                </cac:PartyIdentification>
                <cac:PostalAddress>
                    <cbc:CityName>Kuala Lumpur</cbc:CityName>
                    <cbc:PostalZone>50480</cbc:PostalZone>
                    <cbc:CountrySubentityCode>14</cbc:CountrySubentityCode>
                    <cac:AddressLine>
                        <cbc:Line>Lot 66</cbc:Line>
                    </cac:AddressLine>
                    <cac:AddressLine>
                        <cbc:Line>Bangunan Merdeka</cbc:Line>
                    </cac:AddressLine>
                    <cac:AddressLine>
                        <cbc:Line>Persiaran Jaya</cbc:Line>
                    </cac:AddressLine>
                    <cac:Country>
                        <cbc:IdentificationCode listID="ISO3166-1" listAgencyID="6">MYS</cbc:IdentificationCode>
                    </cac:Country>
                </cac:PostalAddress>
                <cac:PartyLegalEntity>
                    <cbc:RegistrationName>AMS Setia Jaya Sdn. Bhd.</cbc:RegistrationName>
                </cac:PartyLegalEntity>
                <cac:Contact>
                    <cbc:Telephone>+60-123456789</cbc:Telephone>
                    <cbc:ElectronicMail>general.ams@supplier.com</cbc:ElectronicMail>
                </cac:Contact>
            </cac:Party>
        </cac:AccountingSupplierParty>
        <cac:AccountingCustomerParty>
            <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="TIN">C10329126010</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyIdentification>
                <cbc:ID schemeID="BRN">199601003944</cbc:ID>
            </cac:PartyIdentification>
                <cac:PostalAddress>
                    <cbc:CityName>Kuala Lumpur</cbc:CityName>
                    <cbc:PostalZone>50480</cbc:PostalZone>
                    <cbc:CountrySubentityCode>14</cbc:CountrySubentityCode>
                    <cac:AddressLine>
                        <cbc:Line>Lot 66</cbc:Line>
                    </cac:AddressLine>
                    <cac:AddressLine>
                        <cbc:Line>Bangunan Merdeka</cbc:Line>
                    </cac:AddressLine>
                    <cac:AddressLine>
                        <cbc:Line>Persiaran Jaya</cbc:Line>
                    </cac:AddressLine>
                    <cac:Country>
                        <cbc:IdentificationCode listID="ISO3166-1" listAgencyID="6">MYS</cbc:IdentificationCode>
                    </cac:Country>
                </cac:PostalAddress>
                <cac:PartyLegalEntity>
                    <cbc:RegistrationName>Hebat Group</cbc:RegistrationName>
                </cac:PartyLegalEntity>
                <cac:Contact>
                    <cbc:Telephone>+60-123456789</cbc:Telephone>
                    <cbc:ElectronicMail>name@buyer.com</cbc:ElectronicMail>
                </cac:Contact>
            </cac:Party>
        </cac:AccountingCustomerParty>
        <cac:PaymentMeans>
            <cbc:PaymentMeansCode>01</cbc:PaymentMeansCode>
            <cac:PayeeFinancialAccount>
                <cbc:ID>1234567890123</cbc:ID>
            </cac:PayeeFinancialAccount>
        </cac:PaymentMeans>
        <cac:PaymentTerms>
            <cbc:Note>Payment method is cash</cbc:Note>
        </cac:PaymentTerms>
        <cac:TaxTotal>
            <cbc:TaxAmount currencyID="MYR">0</cbc:TaxAmount>
            <cac:TaxSubtotal>
                <cbc:TaxableAmount currencyID="MYR">0</cbc:TaxableAmount>
                <cbc:TaxAmount currencyID="MYR">0</cbc:TaxAmount>
                <cac:TaxCategory>
                    <cbc:ID>06</cbc:ID>
                    <cac:TaxScheme>
                        <cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">OTH</cbc:ID>
                    </cac:TaxScheme>
                </cac:TaxCategory>
            </cac:TaxSubtotal>
        </cac:TaxTotal>
        <cac:LegalMonetaryTotal>
            <cbc:LineExtensionAmount currencyID="MYR">1000</cbc:LineExtensionAmount>
            <cbc:TaxExclusiveAmount currencyID="MYR">1000</cbc:TaxExclusiveAmount>
            <cbc:TaxInclusiveAmount currencyID="MYR">1000</cbc:TaxInclusiveAmount>
            <cbc:PayableAmount currencyID="MYR">1000</cbc:PayableAmount>
        </cac:LegalMonetaryTotal>
        <cac:InvoiceLine>
            <cbc:ID>1</cbc:ID>
            <cbc:InvoicedQuantity unitCode="C62">1</cbc:InvoicedQuantity>
            <cbc:LineExtensionAmount currencyID="MYR">1000</cbc:LineExtensionAmount>
            <cac:TaxTotal>
                <cbc:TaxAmount currencyID="MYR">0</cbc:TaxAmount>
                <cac:TaxSubtotal>
                    <cbc:TaxableAmount currencyID="MYR">1000</cbc:TaxableAmount>
                    <cbc:TaxAmount currencyID="MYR">0</cbc:TaxAmount>
                    <cbc:Percent>6.00</cbc:Percent>
                    <cac:TaxCategory>
                        <cbc:ID>06</cbc:ID>
                        <cbc:Percent>6.00</cbc:Percent>
                        <cbc:TaxExemptionReason>Exempt New Means of Transport</cbc:TaxExemptionReason>
                        <cac:TaxScheme>
                            <cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">OTH</cbc:ID>
                        </cac:TaxScheme>
                    </cac:TaxCategory>
                </cac:TaxSubtotal>
            </cac:TaxTotal>
            <cac:Item>
                <cbc:Description>Laptop Peripherals</cbc:Description>
                <cac:OriginCountry>
                    <cbc:IdentificationCode>MYS</cbc:IdentificationCode>
                </cac:OriginCountry>
                <cac:CommodityClassification>
                    <cbc:ItemClassificationCode listID="PTC">001</cbc:ItemClassificationCode>
                </cac:CommodityClassification>
                <cac:CommodityClassification>
                    <cbc:ItemClassificationCode listID="CLASS">001</cbc:ItemClassificationCode>
                </cac:CommodityClassification>
            </cac:Item>
            <cac:Price>
                <cbc:PriceAmount currencyID="MYR">1000</cbc:PriceAmount>
            </cac:Price>
            <cac:ItemPriceExtension>
                <cbc:Amount currencyID="MYR">1000</cbc:Amount>
            </cac:ItemPriceExtension>
        </cac:InvoiceLine>
    </Invoice>'''
    
        data = {
            'inv': 'INV1234598',
            'issue_date': '2024-06-02',
            'tin': settings.tin,
            'brn': settings.brn
        }
        templateLoader = jinja2.FileSystemLoader(searchpath='./templates')
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template('invoice.xml.jinja2')
        s = template.render(data)
        xml = doc.encode('utf-8')
        res = await cli.post(f'{settings.api_base_url_pwc}/api/submissions', headers=headers, content=s)
        if res.status_code == 202:
            return 'ok'
        
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return None
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_400_BAD_REQUEST
    return None

@router.get('/submission/{erpid}')
async def getsubmission_by_erpid(erpid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'PwC-User-Agent': 'pwc_excel',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        prm = {
            'erp_id': erpid
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/submissions', headers=headers, params=prm)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/submissions')
async def getsubmissions(response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        prm = {
            'sorts': '-created',
            'pageSize': '100'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/outgoing_invoices/submissions', headers=headers, params=prm)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/outgoing/invoices')
async def getoutgoing_invoices(response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        prm = {
            'sorts': '-id',
            'pageSize': '100'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/outgoing_invoices', headers=headers, params=prm)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/outgoing/invoices/{outgoinginvoiceid}')
async def getoutgoing_invoice_by_id(outgoinginvoiceid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/outgoing_invoices/{outgoinginvoiceid}', headers=headers)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/outgoing/invoices/{outgoinginvoiceid}/attachments')
async def getoutgoing_invoice_attachments_by_id(outgoinginvoiceid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/outgoing_invoices/{outgoinginvoiceid}/attachments', headers=headers)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/outgoing/invoices/{outgoinginvoiceid}/ubl')
async def getoutgoing_invoice_ubl_by_id(outgoinginvoiceid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/outgoing_invoices/{outgoinginvoiceid}/ubl', headers=headers)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/outgoing/invoices/{outgoinginvoiceid}/pdf')
async def getoutgoing_invoice_pdf_by_id(outgoinginvoiceid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/outgoing_invoices/{outgoinginvoiceid}/pdf', headers=headers)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/incoming/invoices')
async def getincoming_invoices(response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        prm = {
            'sorts': '-id',
            'pageSize': '100'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/incoming_invoices', headers=headers, params=prm)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/incoming/invoices/{incominginvoiceid}')
async def getincoming_invoice_by_id(incominginvoiceid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/incoming_invoices/{incominginvoiceid}', headers=headers)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/incoming/invoices/{incominginvoiceid}/attachments')
async def getincoming_invoice_attachments_by_id(incominginvoiceid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/incoming_invoices/{incominginvoiceid}/attachments', headers=headers)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/incoming/invoices/{incominginvoiceid}/ubl')
async def getincoming_invoice_ubl_by_id(incominginvoiceid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/incoming_invoices/{incominginvoiceid}/ubl', headers=headers)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

@router.get('/incoming/invoices/{incominginvoiceid}/pdf')
async def getincoming_invoice_pdf_by_id(incominginvoiceid: str, response: Response, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        cli = httpx_client_wrapper()
        headers = {
            'Authorization': f'Bearer {DataManager.access_token_pwc}',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.39.0'
        }
        res = await cli.get(f'{settings.api_base_url_pwc}/api/incoming_invoices/{incominginvoiceid}/pdf', headers=headers)
        if res.text == '':
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        
        return res.json()
    
    except Exception as e:
        print(traceback.format_exc())
        
    response.status_code = status.HTTP_204_NO_CONTENT
    return None
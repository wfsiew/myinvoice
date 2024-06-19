from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException, status
from typing import Annotated

from app.utils import *
from app.models import DataManager
from app.config import Settings

import base64

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

@router.get('/submissions')
async def submissions(settings: Annotated[Settings, Depends(get_settings)]):
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}',
        'Content-Type': 'application/xml',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'User-Agent': 'wf001',
        'ErpId': 'wf001'
    }
    doc = '''<document>
    <supplier_name>SupplierCompany</supplier_name>
    <supplier_tin>sup1234567890</supplier_tin>
    <supplier_regnumber>123456789100</supplier_regnumber>
    <supplier_sst>abcd12345678910</supplier_sst>
    <supplier_tourismtax_number></supplier_tourismtax_number>
    <supplier_email>supplier@test.com</supplier_email>
    <supplier_msic>00000</supplier_msic>
    <supplier_business_activity_description>test activity description</supplier_business_activity_description>
    <supplier_contactnumber>123456789</supplier_contactnumber>
    <supplier_address_line>Building 1 Road 2</supplier_address_line>
    <supplier_address_postalZone>51470</supplier_address_postalZone>
    <supplier_address_city>Kuala Lumpur</supplier_address_city>
    <supplier_address_countrysubentitycode>Region 1</supplier_address_countrysubentitycode>
    <supplier_address_country>MYS</supplier_address_country>
    <buyer_name>BuyerCompany</buyer_name>
    <buyer_tin>buy1234567890</buyer_tin>
    <buyer_regnumber>123456789100</buyer_regnumber>
    <buyer_sst>abcd12345678910</buyer_sst>
    <buyer_email>buyer@test.com</buyer_email>
    <buyer_contactnumber>123456789</buyer_contactnumber>
    <buyer_address_line>Building 1 Road 2</buyer_address_line>
    <buyer_address_postalZone>51470</buyer_address_postalZone>
    <buyer_address_city>Kuala Lumpur</buyer_address_city>
    <buyer_address_countrysubentitycode>Region 1</buyer_address_countrysubentitycode>
    <buyer_address_country>MYS</buyer_address_country>
    <shipping_recipient_name>shipping recipient name</shipping_recipient_name>
    <shipping_recipient_address_line>Building 1 Road 2</shipping_recipient_address_line>
    <shipping_recipient_address_postalZone>51470</shipping_recipient_address_postalZone>
    <shipping_recipient_address_city>Kuala Lumpur</shipping_recipient_address_city>
    <shipping_recipient_address_countrysubentitycode>Region 1</shipping_recipient_address_countrysubentitycode>
    <shipping_recipient_address_country>MYS</shipping_recipient_address_country>
    <shipping_recipient_tin>shi1234567890</shipping_recipient_tin>
    <shipping_recipient_regnumber>123456789100</shipping_recipient_regnumber>
    <invoice_number>invnumber123</invoice_number>
    <invoice_type>01</invoice_type>
    <original_invoice_number></original_invoice_number>
    <issue_date>2002-05-30T09:00:00</issue_date>
    <currency_code>MYR</currency_code>
    <exchange_rate>1</exchange_rate>
    <billing_frequency>Daily</billing_frequency>
    <billing_period_start>2025-01-01</billing_period_start>
    <billing_period_end>2025-01-31</billing_period_end>
    <payment_mode>05</payment_mode>
    <payment_terms>30 days</payment_terms>
    <prepayment_amount>100</prepayment_amount>
    <prepayment_date>2002-05-30T09:00:00</prepayment_date>
    <prepayment_reference_number>pre123456789</prepayment_reference_number>
    <bill_reference_number>brf123456789</bill_reference_number>
    <customs_form_reference_number>cfr123456789</customs_form_reference_number>
    <incoterms>testincoterm</incoterms>
    <tax_summary>
        <total_excluding_tax>10000</total_excluding_tax>
        <total_including_tax>10400</total_including_tax>
        <total_tax_amount>400</total_tax_amount>
        <total_net_amount>10000</total_net_amount>
        <total_payable_amount>10400</total_payable_amount>
        <rounding_amount>0</rounding_amount>
        <discount_amount>500</discount_amount>
        <fee_amount>100</fee_amount>
        <tax_type>
            <tax_type>01</tax_type>
            <tax_amount>400</tax_amount>
            <tax_exemption></tax_exemption>
            <exempted_tax_amount></exempted_tax_amount>
            <taxable_amount>5000</taxable_amount>
        </tax_type>
        <tax_type>
            <tax_type>02</tax_type>
            <tax_amount>0</tax_amount>
            <tax_exemption>Buyer’s sales tax exemption certificate number</tax_exemption>
            <exempted_tax_amount>400</exempted_tax_amount>
            <taxable_amount>5000</taxable_amount>
        </tax_type>
    </tax_summary>
    <line>
        <classification>service</classification>
        <description>service</description>
        <unit_price>5000</unit_price>
        <tax_type>02</tax_type>
        <tax_rate>0.08</tax_rate>
        <tax_amount>0</tax_amount>
        <tax_exemption>Buyer’s sales tax exemption certificate number</tax_exemption>
        <exempted_tax_amount>400</exempted_tax_amount>
        <subtotal>5000</subtotal>
        <total_excluding_tax>5000</total_excluding_tax>
        <quantity></quantity>
        <measurement></measurement>
        <discount_rate></discount_rate>
        <discount_amount></discount_amount>
        <fee_rate></fee_rate>
        <fee_amount></fee_amount>
    </line>
      <line>
        <classification>goods</classification>
        <description>goods</description>
        <unit_price>500</unit_price>
        <tax_type>01</tax_type>
        <tax_rate>0.08</tax_rate>
        <tax_amount>400</tax_amount>
        <tax_exemption></tax_exemption>
        <exempted_tax_amount></exempted_tax_amount>
        <subtotal>4400</subtotal>
        <total_excluding_tax>5000</total_excluding_tax>
        <quantity>10</quantity>
        <measurement>piece</measurement>
        <discount_rate>0.1</discount_rate>
        <discount_amount>500</discount_amount>
        <fee_rate>0.1</fee_rate>
        <fee_amount>100</fee_amount>
    </line>
</document>'''
    xml = doc.encode('utf-8')
    v = base64.b64encode(xml)
    k = v.decode('utf-8')
    res = await cli.post(f'{settings.api_base_url}/api/submissions', headers=headers, content=k)
    print(res.status_code)
    return 'ok'

@router.get('/getsubmission')
async def getsubmission_by_erpid(erpid: str, settings: Annotated[Settings, Depends(get_settings)]):
    cli = httpx_client_wrapper()
    headers = {
        'Authorization': f'Bearer {DataManager.access_token}',
        'PwC-User-Agent': 'pwc_excel',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'User-Agent': 'wf001'
    }
    prm = {
        'erp_id': erpid
    }
    res = await cli.get(f'{settings.api_base_url}/api/submissions', headers=headers, params=prm)
    return res.json()

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
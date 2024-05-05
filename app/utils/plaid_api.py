import os
import json
import time
from datetime import datetime
import logging
import traceback
import sys

from django.conf import settings

import plaid
from plaid.api import plaid_api

from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.transactions_recurring_get_request import TransactionsRecurringGetRequest

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

from django.conf import settings

PLAID_CLIENT_ID = settings.PLAID_CLIENT_ID
PLAID_SECRET = settings.PLAID_SECRET
PLAID_ENV = settings.PLAID_ENV
PLAID_PRODUCTS = settings.PLAID_PRODUCTS.split(',')
PLAID_COUNTRY_CODES = settings.PLAID_COUNTRY_CODES.split(',')
PLAID_REDIRECT_URI = settings.PLAID_REDIRECT_URI
PUBLIC_URL = settings.PUBLIC_URL

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox
if PLAID_ENV == 'development':
    host = plaid.Environment.Development
if PLAID_ENV == 'production':
    host = plaid.Environment.Production


configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def format_error(e):
    response = json.loads(e.body)
    return {
        'error': {
            'status_code': e.status, 
            'display_message': response['error_message'],
            'error_code': response['error_code'],
            'error_type': response['error_type']
        }
    }

def get_profile_data(public_token):
    try:
        response = exchange_public_token(public_token)
        access_token = response['access_token']
        item_id = response['item_id']

        item_data = get_item_data(access_token)
        item_data[0]['updated_at'] = datetime.fromtimestamp(time.time())
        institution_data = get_institution_data(item_data[0]['institution_id'])
        accounts_data = get_accounts_data(access_token, item_id)

        logging.info(f"Public Token: {public_token}")
        logging.info(f"Item: {item_data}")
        logging.info(f"Institution: {institution_data}")
        logging.info(f"Accounts: {accounts_data}")

        return {'data': [item_data, institution_data, accounts_data]}

    except plaid.ApiException as e:
        logging.error(f"Error exchanging public token: {public_token} | Error: {e} | Stack Trace: {traceback.format_exc()}")
        return {'error': format_error(e)}

def get_item_data(access_token):
    item_request = ItemGetRequest(access_token=access_token)
    response = client.item_get(item_request)
    item = response['item']

    item_data = {
        "id": item['item_id'],
        "access_token": access_token,
        "transaction_cursor": '',
        "institution_id": item['institution_id'],
        "status": 'good'
    }

    return item_data

def get_accounts_data(access_token):
    account_request = AccountsGetRequest(access_token=access_token)
    response = client.accounts_get(account_request)
    accounts = response['accounts']

    accounts_data = []
    for account in accounts:
        account_data = {
            'id': account['account_id'],
            'available_balance': account['balances']['available'],
            'current_balance': account['balances']['current'],
            'iso_currency_code': account['balances']['iso_currency_code'],
            'credit_limit': account['balances']['limit'],
            'mask': account['mask'],
            'name': account['name'],
            'official_name': account['official_name'],
            'subtype': str(account['subtype']),
            'type': str(account['type'])
        }
        accounts_data.append(account_data)

    return accounts_data


def get_institution_data(institution_id):
    institution_request = InstitutionsGetByIdRequest(
        institution_id=institution_id,
        country_codes= [CountryCode("US")],
        options={
            "include_optional_metadata": True
        }
    )
    institution_response = client.institutions_get_by_id(institution_request)
    institution = institution_response['institution']

    institution_data = {
        'id': institution['institution_id'],
        'name': institution['name'],
        'color': institution['primary_color'],
        'logo': institution['logo'],
        'url': institution['url']
    }

    return institution_data


def get_transactions_data(access_token, cursor):
    added = []
    modified = []
    removed = []
    has_more = True

    try:
        while has_more:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor,
            )
            response = client.transactions_sync(request).to_dict()
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            has_more = response['has_more']
            cursor = response['next_cursor']

        return {
            'data':{
                'added': added,
                'modified': modified,
                'removed': removed,
                'cursor': cursor
            }
        }

    except plaid.ApiException as e:
        logging.error(f"Error getting transaction data | Error: {e} | Stack Trace: {traceback.format_exc()}")
        return {'error': format_error(e)}
    
def get_recurring_data(access_token, account_ids=None):
    request_data = {
        'access_token': access_token
    }
    if account_ids:
        request_data['account_ids'] = account_ids

    request = TransactionsRecurringGetRequest(**request_data)

    response = client.transactions_recurring_get(request)
    
    return response.to_dict()

def create_link_token(user_id):
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Finch",
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(user_id)
            ),
            webhook=PUBLIC_URL + '/api/webhook',
        )
        if PLAID_REDIRECT_URI!=None:
            request['redirect_uri']=PLAID_REDIRECT_URI

        response = client.link_token_create(request)

        return {'data': response.to_dict()}

    except plaid.ApiException as e:
        logging.error(f"Error creating link token | Error: {e} | Stack Trace: {traceback.format_exc()}")
        return {'error': format_error(e)}


def exchange_public_token(public_token):
    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    return client.item_public_token_exchange(exchange_request)



if __name__ == '__main__':
    # result, error = create_link_token()

    # if error:
    #     print(error)

    # print(result)

    response = get_recurring_data('access-production-c64a9c87-d22d-47e2-8f70-8e2d1342ff2d', ['3mEBmVgVPduozqXqywJpIg1RypKJbwuPAOOrw'])

    print(response)

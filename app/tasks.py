from django.db import transaction
from celery import shared_task
from .utils import plaid_api

from .serializers import InstitutionSerializer, AccountSerializer


@shared_task
def save_institution_data(institution_id):

    institution_data = plaid_api.get_institution_data(institution_id)
    serializer = InstitutionSerializer(data=institution_data)
    
    print('institution data', institution_data)
    print('institution valid', serializer.is_valid())
    
    if serializer.is_valid():
        instance = serializer.save()
        return instance.id
    else:
        print(serializer.errors)

@shared_task
def save_accounts_data(access_token, item_id):

    accounts_data = plaid_api.get_accounts_data(access_token)
    for account_data in accounts_data:
        account_data['item'] = item_id

    instance_ids = []
    for account_data in accounts_data:
        serializer = AccountSerializer(data=account_data)

        print('account data', account_data)
        print('account valid', serializer.is_valid())

        if serializer.is_valid():
            instance = serializer.save()
            instance_ids.append(instance.id)
        else:
            print(serializer.errors)

    return instance_ids

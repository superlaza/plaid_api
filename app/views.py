from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions
from .models import Transaction, Item, Account, Institution, Stream
from .serializers import TransactionSerializer, ItemSerializer, AccountSerializer, InstitutionSerializer, StreamSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated]

class StreamViewSet(viewsets.ModelViewSet):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [permissions.IsAuthenticated]

from rest_framework.permissions import IsAuthenticated


from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .utils import plaid_api

from .tasks import save_institution_data, save_accounts_data


from django.shortcuts import render

def link(request):
    return render(request, 'app/link.html')

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def create_link_token(request):
    user = request.user

    response = plaid_api.create_link_token(user.id)
    if 'error' in response:
        return Response({'error': response})
    return Response(response['data'])

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def set_access_token(request):
    user = request.user
    user_id = '1'

    public_token = request.data['public_token'] 

    response = plaid_api.exchange_public_token(public_token)

    access_token = response['access_token']

    item_data = plaid_api.get_item_data(access_token)
    item_data['user'] = user_id
    serializer = ItemSerializer(data=item_data)
    
    if serializer.is_valid():
        item_instance = serializer.save()

        save_institution_data.delay(item_instance.institution_id)
        save_accounts_data.delay(access_token, item_instance.id)

        return Response({'success': True})
    
    else:
        print(serializer.errors)
        return Response({'error': 'serializer error'})


# @api_view(['GET'])
# def transactions_sync(request):
#     items = db.get_items_for_profile('default')
#     for item in items:
#         response = update_transactions(item)
#         if 'error' in response:
#             return Response({'error': response['error']})
#     return Response({'success': True})

# @api_view(['GET'])
# def recurring(request):
#     items = db.get_items_for_profile('default')
#     for item in items:
#         account_ids = [account.id for account in item.accounts]
#         response = plaid_api.get_recurring_data(item.access_token, account_ids)
#         for stream_type in ['inflow_streams', 'outflow_streams']:
#             for stream_data in response[stream_type]:
#                 stream_data['stream_type'] = stream_type
#                 result = db.save([stream_data])
#                 if 'error' in result:
#                     return Response({'error': result['error']})
#     return Response({'success': True})


# @api_view(['POST'])
# def webhook_handler(request):
#     webhook_data = request.data
#     if webhook_data['webhook_type'] == 'ITEM':
#         webhooks.item_webhook_handler(webhook_data)
#     elif webhook_data['webhook_type'] == 'TRANSACTION':
#         webhooks.transaction_webhook_handler(webhook_data)
#     else:
#         # todo: log webhook not handled
#         pass
#     return Response({'status': 'ok'})



if __name__ == '__main__':
    from django.test import Client
    client = Client()

    response = client.get('/api/set_access_token/')
    print(response.content)
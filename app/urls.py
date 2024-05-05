from django.urls import path
from .views import link, create_link_token, set_access_token
# from .views import create_link_token, set_access_token, transactions_sync, recurring, webhook_handler

urlpatterns = [
    path('link', link, name='link'),
    path('create_link_token', create_link_token, name='create_link_token'),
    path('set_access_token', set_access_token, name='set_access_token'),
    # path('api/transactions_sync', transactions_sync, name='transactions_sync'),
    # path('api/recurring', recurring, name='recurring'),
    # path('api/webhook', webhook_handler, name='webhook_handler'),
]
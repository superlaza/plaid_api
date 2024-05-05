from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Transaction, Item, Account, Institution, Stream

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    accounts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'user', 'access_token', 'transaction_cursor', 'institution_id', 'status', 'accounts']

class AccountSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
    )
    class Meta:
        model = Account
        fields = '__all__'

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'

class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = '__all__'
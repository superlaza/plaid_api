from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone

class Item(models.Model):
    id = models.TextField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    access_token = models.TextField()
    transaction_cursor = models.TextField(blank=True)
    institution_id = models.TextField()
    status = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Account(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='accounts')
    available_balance = models.FloatField()
    current_balance = models.FloatField()
    iso_currency_code = models.CharField(max_length=3)
    credit_limit = models.FloatField(null=True)
    mask = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    official_name = models.CharField(max_length=255, null=True, blank=True)
    subtype = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Institution(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    color = models.TextField(null=True)
    logo = models.TextField(null=True)
    url = models.TextField(null=True)


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=255, primary_key=True)
    account_id = models.CharField(max_length=255)
    account_owner = models.CharField(max_length=255, blank=True)
    amount = models.FloatField()
    authorized_date = models.DateField()
    authorized_datetime = models.DateTimeField()
    category = models.JSONField()
    category_id = models.CharField(max_length=255, blank=True)
    check_number = models.CharField(max_length=255, blank=True)
    counterparties = models.JSONField()
    date = models.DateField()
    datetime = models.DateTimeField()
    iso_currency_code = models.CharField(max_length=3)
    location = models.JSONField()
    logo_url = models.CharField(max_length=255, blank=True)
    merchant_entity_id = models.CharField(max_length=255, blank=True)
    merchant_name = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    payment_channel = models.CharField(max_length=255)
    payment_meta = models.JSONField()
    pending = models.BooleanField()
    pending_transaction_id = models.CharField(max_length=255, blank=True)
    personal_finance_category = models.JSONField()
    personal_finance_category_icon_url = models.CharField(max_length=255, blank=True)
    transaction_code = models.CharField(max_length=255, blank=True)
    transaction_type = models.CharField(max_length=255)
    unofficial_currency_code = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    category_user = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Stream(models.Model):
    stream_id = models.CharField(max_length=255, primary_key=True)
    stream_type = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255)
    average_amount = models.FloatField()
    category = models.JSONField()
    category_id = models.CharField(max_length=255)
    description = models.TextField()
    first_date = models.DateField()
    frequency = models.CharField(max_length=255)
    is_active = models.BooleanField()
    is_user_modified = models.BooleanField()
    last_amount = models.FloatField()
    last_date = models.DateField()
    last_user_modified_datetime = models.DateTimeField()
    merchant_name = models.CharField(max_length=255, blank=True)
    personal_finance_category = models.JSONField()
    status = models.CharField(max_length=255)
    transaction_ids = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
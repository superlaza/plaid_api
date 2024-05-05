from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import Transaction, Item, Account, Institution, Stream

# Create your tests here.

from django.urls import reverse

# class MyViewTests(TestCase):
#     def setUp(self):
#         # Create a user
#         self.user = User.objects.create(id=1, username='superlaza')
#         self.user.set_password('password')
#         self.user.save()

#     def test_my_view(self):
#         self.client.login(username='superlaza', password='password')
#         response = self.client.post(reverse('set_access_token'), {'public_token': 'public-production-e6c25608-a8c1-497a-8587-f49fd02c6eb6'})

#         print('response', response.data)
#         item = Item.objects.filter(id=response.data['instance_id'])

#         self.assertTrue(Item.objects.filter(id=instance.id).exists())

#         print('item', item)
#         # self.assertEqual(response.status_code, 200)
#         # self.assertContains(response, "Hello, world!")


from .tasks import save_institution_data, save_accounts_data

class TestSaveInsitution(TestCase):
    def test_save_institution_data(self):
        instance_id = save_institution_data('ins_56')
        
        self.assertTrue(Institution.objects.filter(id=instance_id).exists())

        # self.assertEqual(result, 12)

class TestSaveInsitution(TestCase):
    def setUp(self):
        User.objects.create(id=1, username='superlaza')
        Item.objects.create(id='3Ypex3yMA1fQ68PqjwdPCaMZKbYbz3UKAPBqV', user_id=1, access_token='access-production-5667242a-bd33-4ef1-becb-f2bf3d3cce88', status='good')

    def test_save_institution_data(self):
        access_token = 'access-production-5667242a-bd33-4ef1-becb-f2bf3d3cce88'
        item_id = '3Ypex3yMA1fQ68PqjwdPCaMZKbYbz3UKAPBqV'

        instance_ids = save_accounts_data(access_token, item_id)

        for instance_id in instance_ids:
            self.assertTrue(Account.objects.filter(id=instance_id).exists())

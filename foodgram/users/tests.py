from django.test import TestCase, Client
from django.urls import reverse


class TestSubscription(TestCase):
    def setUp(self):
        self.client = Client()

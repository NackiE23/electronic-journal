from django.test import TestCase, Client, LiveServerTestCase
from selenium import webdriver

from .models import *


class SeleniumTestCase(TestCase):
    def test_title(self):
        driver = webdriver.Firefox()

        driver.get('http://127.0.0.1:8000/profile/47/')
        assert 'Profile' in driver.title


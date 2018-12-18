import pytest
import logging
import json

from django.test import Client

logging.disable(logging.ERROR)

@pytest.mark.django_db(transaction=True)
class TestFrontend:
    def test_smoke(self):
        c = Client()
        response = c.get("/")
        assert response.status_code == 200
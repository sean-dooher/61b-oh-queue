import pytest
import logging
import json

logging.disable(logging.ERROR)

@pytest.mark.django_db(transaction=True)
class TestBackend:
    def test_smoke(self):
        pass
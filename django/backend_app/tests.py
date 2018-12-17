import pytest
import logging
import json

logging.disable(logging.ERROR)

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestAsync:
    async def test_create(self):
        pass

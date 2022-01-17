import json
import pytest
from django.conf import settings
from app.users.models import User
from app.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture()
def bot_client(db, user):
    """A Django test client logged in as an admin user."""
    from django.test.client import Client

    data = json.dumps({"user_id": str(user.id), "app_key": settings.BOT_SECRET_KEY})
    client = Client(HTTP_AUTHORIZATION=data)
    return client

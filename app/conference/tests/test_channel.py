import json
import pytest
from app.conference.factories import ChannelFactory, ConferenceFactory, CourseFactory
from ..models import Channel


@pytest.mark.django_db
def test_create_channel(user, bot_client):
    response = bot_client.get("/api/admin/channel")
    assert response.status_code == 200
    assert len(Channel.objects.filter(owner=user)) == 1


@pytest.mark.django_db
def test_update_channel(user, bot_client):
    ChannelFactory(owner=user)
    response = bot_client.patch(
        "/api/admin/channel",
        data=json.dumps({"name": "some_name"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert len(Channel.objects.filter(owner=user, name="some_name")) == 1


def test_has_one_public_conference(bot_client, user):
    channel = ChannelFactory(owner=user, published=True)
    ConferenceFactory(owner=user, active=True, course=None)
    response = bot_client.get("/api/channels/")
    assert response.status_code == 200
    assert response.data["results"][0]["id"] == str(channel.id)
    assert response.data["results"][0]["conference_count"] == 1
    assert response.data["results"][0]["course_count"] == 0


def test_has_one_public_conference_in_course(bot_client, user):
    channel = ChannelFactory(owner=user, published=True)
    course = CourseFactory(users=[user])
    ConferenceFactory(owner=user, active=True, course=course)
    response = bot_client.get("/api/channels/")
    assert response.status_code == 200
    assert response.data["results"][0]["id"] == str(channel.id)
    assert response.data["results"][0]["conference_count"] == 0
    assert response.data["results"][0]["course_count"] == 1

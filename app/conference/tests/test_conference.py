import pytest
import json
from unittest.mock import patch
from app.conference.models.user_conference import UserConference
from app.users.tests.factories import UserFactory
from app.conference.factories import (
    ChannelFactory,
    ConferenceFactory,
    CourseFactory,
    SlideFactory,
    UserConferenceFactory,
)
from ..models import Slide


def test_update(bot_client, user):
    conference = ConferenceFactory(owner=user)
    response = bot_client.patch(
        f"/api/admin/conferences/{str(conference.id)}/",
        data=json.dumps({"name": "conference 1 updated"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.data["name"] == "conference 1 updated"


def test_create_with_course(bot_client):
    course = CourseFactory()
    response = bot_client.post("/api/admin/conferences/", data={"name": "conference 1", "course": course.id})
    assert response.status_code == 201
    assert response.data["name"] == "conference 1"
    assert response.data["course"] == course.id


def test_list(bot_client, user):
    conference = ConferenceFactory(owner=user)
    response = bot_client.get(f"/api/admin/conferences/?course={conference.course.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1


def test_delete(bot_client, user):
    conference = ConferenceFactory(owner=user)
    response = bot_client.delete(f"/api/admin/conferences/{str(conference.id)}/")
    assert response.status_code == 204


@pytest.mark.django_db
@patch("app.conference.signals.evaluated_conference.send")
def test_evaluate(signal_mock, bot_client, user):
    user_owner = UserFactory()
    conference = ConferenceFactory(owner=user_owner, active=True)
    UserConferenceFactory(conference=conference, user=user)
    response = bot_client.post(f"/api/conferences/{str(conference.id)}/evaluate/")
    assert response.status_code == 200
    assert signal_mock.called
    assert conference == signal_mock.call_args_list[0][1]["conference"]
    assert isinstance(signal_mock.call_args_list[0][1]["user_conference"], UserConference)


def test_cant_update(bot_client):
    user = UserFactory()
    conference = ConferenceFactory(owner=user)
    response = bot_client.patch(
        f"/api/admin/conferences/{str(conference.id)}/",
        data=json.dumps({"name": "conference 1 updated"}),
        content_type="application/json",
    )
    assert response.status_code == 404


def test_cant_delete(bot_client):
    user = UserFactory()
    conference = ConferenceFactory(owner=user)
    response = bot_client.patch(f"/api/admin/conferences/{str(conference.id)}/")
    assert response.status_code == 404


def test_doesnt_list_conference_of_other(bot_client):
    user = UserFactory()
    ConferenceFactory(owner=user)
    response = bot_client.get("/api/admin/conferences/", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 0


def test_conference_by_course(bot_client):
    course_1 = CourseFactory()
    course_2 = CourseFactory()
    ConferenceFactory(course=course_1, active=True)

    response = bot_client.get(f"/api/conferences/?course={course_1.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1

    response = bot_client.get(f"/api/conferences/?course={course_2.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 0


def test_conference_active_list(bot_client):
    course = CourseFactory()
    ConferenceFactory(active=False, course=course)
    conference = ConferenceFactory(active=True, course=course)
    response = bot_client.get(f"/api/conferences/?course={course.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(conference.id)


def test_conference_list(bot_client):
    course = CourseFactory()
    conference = ConferenceFactory(active=True, course=course)
    ConferenceFactory(course=course)
    response = bot_client.get(f"/api/conferences/?course={course.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(conference.id)


def test_conference_retrieve_all(bot_client):
    course = CourseFactory()
    visible = ConferenceFactory(active=True, course=course)
    active = ConferenceFactory(active=True, course=course)
    no_active = ConferenceFactory(course=course)

    response = bot_client.get(f"/api/conferences/{visible.id}/?course={course.id}", content_type="application/json")
    assert response.status_code == 200

    response = bot_client.get(f"/api/conferences/{active.id}/?course={course.id}", content_type="application/json")
    assert response.status_code == 200

    response = bot_client.get(f"/api/conferences/{no_active.id}/?course={course.id}", content_type="application/json")
    assert response.status_code == 200


def test_search(bot_client):
    conference = ConferenceFactory(name="aaa", active=True)
    ConferenceFactory(name="bbb", active=True)
    response = bot_client.get("/api/conferences/?search=aa", content_type="application/json")
    assert response.status_code == 200
    data = response.data
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == str(conference.id)


def test_search_in_admin(bot_client, user):
    conference = ConferenceFactory(name="aaa", active=True, owner=user)
    ConferenceFactory(name="aaa", active=True)  # It is of the other user
    ConferenceFactory(name="bbb", active=True, owner=user)
    response = bot_client.get("/api/admin/conferences/?search=aa", content_type="application/json")
    assert response.status_code == 200
    data = response.data
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == str(conference.id)


@pytest.mark.django_db
def test_conference_files():
    conference = ConferenceFactory()
    SlideFactory(voice="voice1", image="image1", conference=conference)
    SlideFactory(voice="voice2", image="image2", conference=conference)
    files = conference.files
    assert len(files) == 4
    assert "voice1" in files
    assert "voice2" in files
    assert "image1" in files
    assert "image2" in files


@pytest.mark.django_db
def test_conference_remove_files():
    conference = ConferenceFactory()
    SlideFactory(voice="voice1", image="image1", conference=conference)
    SlideFactory(voice="voice2", image="image2", conference=conference)
    with patch("app.conference.tasks.remove_files_in_bots.apply_async") as task_mock:
        conference.delete()
    task_mock.assert_any_call(kwargs={"files": ["image1", "voice1"]})
    task_mock.assert_any_call(kwargs={"files": ["image2", "voice2"]})


@pytest.mark.django_db
def test_orphan_conferences(bot_client, user):
    conference_1 = ConferenceFactory(owner=user, course=None)
    ConferenceFactory(owner=user)
    response = bot_client.get("/api/admin/conferences/?orphan_conferences", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(conference_1.id)


@pytest.mark.django_db
def test_clear_slides(bot_client, user):
    conference = ConferenceFactory(owner=user)
    SlideFactory(conference=conference)
    SlideFactory(conference=conference)
    assert len(Slide.objects.all()) == 2
    response = bot_client.post(f"/api/admin/conferences/{conference.id}/clear_slides/")
    assert response.status_code == 200
    assert len(Slide.objects.all()) == 0


@pytest.mark.django_db
def test_by_position(bot_client):
    conference = ConferenceFactory()
    SlideFactory(conference=conference, text="slide1")
    SlideFactory(conference=conference, text="slide2")
    response = bot_client.get(f"/api/conferences/{conference.id}/by-position/2/")
    assert response.status_code == 200
    assert response.data["data"]["text"] == "slide2"
    assert response.data["is_last"]


@patch("app.conference.signals.start_conference.send")
@pytest.mark.django_db
def test_start_conference_signal(signal_mock, bot_client):
    conference = ConferenceFactory()
    SlideFactory(conference=conference)
    response = bot_client.get(f"/api/conferences/{conference.id}/by-position/1/")
    assert response.status_code == 200
    assert signal_mock.called
    assert conference == signal_mock.call_args_list[0][1]["conference"]


@patch("app.conference.signals.start_conference.send")
@pytest.mark.django_db
def test_no_start_conference_signal(signal_mock, bot_client):
    conference = ConferenceFactory()
    SlideFactory(conference=conference)
    SlideFactory(conference=conference)
    response = bot_client.get(f"/api/conferences/{conference.id}/by-position/2/")
    assert response.status_code == 200
    assert not signal_mock.called


@pytest.mark.django_db
def test_filter_by_channel(bot_client, user):
    channel = ChannelFactory(owner=user)
    conference = ConferenceFactory(active=True, owner=user, course=None)
    ConferenceFactory(active=True, owner=user, course=CourseFactory())
    response = bot_client.get(
        f"/api/conferences/?channel={channel.id}&orphan_conferences=true", content_type="application/json"
    )
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(conference.id)


@pytest.mark.django_db
def test_filter_by_other_channel(bot_client):
    channel = ChannelFactory()
    ConferenceFactory(active=True)
    response = bot_client.get(f"/api/conferences/?channel={channel.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 0

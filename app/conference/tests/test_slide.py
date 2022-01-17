from unittest.mock import patch
from app.conference.models.slide import Slide
from app.users.tests.factories import UserFactory
import json
import pytest
from ..factories import ConferenceFactory, SlideFactory


@pytest.mark.django_db
def test_add_with_position():
    conference = ConferenceFactory()
    slide_1 = SlideFactory(conference=conference)
    assert slide_1.position == 1

    slide_2 = SlideFactory(conference=conference)
    assert slide_2.position == 2

    slide_3 = SlideFactory(conference=conference)
    assert slide_3.position == 3

    slide_4 = SlideFactory(conference=conference)
    assert slide_4.position == 4

    slide_5 = SlideFactory()
    slide_5.position = 5
    slide_5.save()
    assert slide_5.position == 5

    slide_2.delete()
    slide_1.refresh_from_db()
    slide_3.refresh_from_db()
    slide_4.refresh_from_db()
    slide_5.refresh_from_db()
    assert slide_1.position == 1
    assert slide_3.position == 2
    assert slide_4.position == 3
    assert slide_5.position == 5

    slide_4.delete()
    slide_1.refresh_from_db()
    slide_3.refresh_from_db()
    slide_5.refresh_from_db()
    assert slide_1.position == 1
    assert slide_3.position == 2
    assert slide_5.position == 5


def test_create(bot_client, user):
    conference = ConferenceFactory(owner=user)
    response = bot_client.post(f"/api/admin/conferences/{str(conference.id)}/slides/", data={"text": "slide 1"})
    assert response.status_code == 201
    assert response.data["text"] == "slide 1"


def test_update(bot_client, user):
    conference = ConferenceFactory(owner=user)
    slide = SlideFactory(conference=conference, text="slide 1")
    response = bot_client.patch(
        f"/api/admin/conferences/{str(conference.id)}/slides/{str(slide.id)}/",
        data=json.dumps({"text": "slide 1 updated"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.data["text"] == "slide 1 updated"


def test_list(bot_client, user):
    conference = ConferenceFactory(owner=user)
    SlideFactory(conference=conference, text="slide 1")
    response = bot_client.get(
        f"/api/admin/conferences/{str(conference.id)}/slides/",
        content_type="application/json",
    )
    assert response.status_code == 200
    assert len(response.data["results"]) == 1


def test_delete(bot_client, user):
    conference = ConferenceFactory(owner=user)
    slide = SlideFactory(conference=conference, text="slide 1")
    response = bot_client.delete(
        f"/api/admin/conferences/{str(conference.id)}/slides/{str(slide.id)}/",
        content_type="application/json",
    )
    assert response.status_code == 204


def test_cant_update(bot_client):
    user = UserFactory()
    conference = ConferenceFactory(owner=user)
    slide = SlideFactory(conference=conference, text="slide 1")
    response = bot_client.patch(
        f"/api/admin/conferences/{str(conference.id)}/slides/{str(slide.id)}/",
        data=json.dumps({"text": "slide 1 updated"}),
        content_type="application/json",
    )
    assert response.status_code == 404


def test_cant_delete(bot_client):
    user = UserFactory()
    conference = ConferenceFactory(owner=user)
    slide = SlideFactory(conference=conference, text="slide 1")
    response = bot_client.delete(
        f"/api/admin/conferences/{str(conference.id)}/slides/{str(slide.id)}/",
        content_type="application/json",
    )
    assert response.status_code == 404


def test_public_list(bot_client):
    conference = ConferenceFactory()
    SlideFactory(conference=conference, text="slide 1")
    response = bot_client.get(f"/api/conferences/{str(conference.id)}/slides/", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_files_no_voice_no_images():
    slide: Slide = SlideFactory()
    assert len(slide.files) == 0


@pytest.mark.django_db
def test_files_voice_images():
    slide: Slide = SlideFactory(voice="voice", image="image")
    assert len(slide.files) == 2
    assert "voice" in slide.files
    assert "image" in slide.files


@pytest.mark.django_db
def test_remove_files_voice_images():
    slide: Slide = SlideFactory(voice="voice", image="image")
    with patch("app.conference.tasks.remove_files_in_bots.apply_async") as task_mock:
        slide.delete()
    task_mock.assert_called_once_with(kwargs={"files": ["image", "voice"]})


@pytest.mark.django_db
def test_update_image():
    slide: Slide = SlideFactory(voice="voice", image="image")
    with patch("app.conference.tasks.remove_files_in_bots.apply_async") as task_mock:
        slide.image = "image_updated"
        slide.save()
    task_mock.assert_called_once_with(kwargs={"files": ["image"]})


@pytest.mark.django_db
def test_update_voice():
    slide: Slide = SlideFactory(voice="voice", image="image")
    with patch("app.conference.tasks.remove_files_in_bots.apply_async") as task_mock:
        slide.voice = "voice_updated"
        slide.save()
    task_mock.assert_called_once_with(kwargs={"files": ["voice"]})


@pytest.mark.django_db
def test_update_other_field():
    slide: Slide = SlideFactory(voice="voice", image="image")
    with patch("app.conference.tasks.remove_files_in_bots.apply_async") as task_mock:
        slide.text = "text_updated"
        slide.save()
    task_mock.assert_not_called()

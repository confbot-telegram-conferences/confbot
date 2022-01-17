import pytest
from unittest.mock import patch
from app.conference.factories import ConferenceFactory, SlideFactory, UserConferenceFactory
from app.conference.models import UserConference
from app.users.tests.factories import UserFactory


def test_set_as_viewed(bot_client, user):
    conference = ConferenceFactory()
    slide_1 = SlideFactory(conference=conference)
    slide_2 = SlideFactory(conference=conference)
    slide_3 = SlideFactory(conference=conference)

    assert len(UserConference.objects.all()) == 0

    response = bot_client.post(f"/api/conferences/{conference.pk}/slides/{slide_1.pk}/set_as_viewed/")
    assert response.status_code == 200
    assert len(UserConference.objects.all()) == 1
    entity: UserConference = UserConference.objects.get_by_conference_user(conference=conference, user=user)
    assert entity.slide_position == 1

    response = bot_client.post(f"/api/conferences/{conference.pk}/slides/{slide_2.pk}/set_as_viewed/")
    assert response.status_code == 200
    assert len(UserConference.objects.all()) == 1
    entity.refresh_from_db()
    assert entity.slide_position == 2

    response = bot_client.post(f"/api/conferences/{conference.pk}/slides/{slide_3.pk}/set_as_viewed/")
    assert response.status_code == 200
    assert len(UserConference.objects.all()) == 1
    entity.refresh_from_db()
    assert entity.slide_position == 3

    # Don't udate the slide_position because the slide is smaller
    response = bot_client.post(f"/api/conferences/{conference.pk}/slides/{slide_1.pk}/set_as_viewed/")
    assert response.status_code == 200
    assert len(UserConference.objects.all()) == 1
    entity: UserConference = UserConference.objects.get_by_conference_user(conference=conference, user=user)
    assert entity.slide_position == 3


@patch("app.conference.signals.evaluated_conference.send")
def test_conference_evaluation(signal_mock, bot_client, user):
    conference = ConferenceFactory(active=True)
    slide_1 = SlideFactory(conference=conference)
    slide_2 = SlideFactory(conference=conference)

    response = bot_client.post(f"/api/conferences/{conference.pk}/evaluate/", data={"evaluation": 5})
    assert response.status_code == 404

    response = bot_client.post(f"/api/conferences/{conference.pk}/slides/{slide_1.pk}/set_as_viewed/")
    assert response.status_code == 200

    response = bot_client.post(f"/api/conferences/{conference.pk}/evaluate/", data={"evaluation": 5})
    assert response.status_code == 400

    response = bot_client.post(f"/api/conferences/{conference.pk}/slides/{slide_2.pk}/set_as_viewed/")
    assert response.status_code == 200

    response = bot_client.post(f"/api/conferences/{conference.pk}/evaluate/", data={"evaluation": 15})
    assert response.status_code == 400

    response = bot_client.post(f"/api/conferences/{conference.pk}/evaluate/", data={"evaluation": 0})
    assert response.status_code == 400

    response = bot_client.post(f"/api/conferences/{conference.pk}/evaluate/", data={"evaluation": 3})
    assert response.status_code == 200
    assert signal_mock.called

    user_conference = UserConference.objects.get(conference=conference, user=user)
    assert user_conference.evaluation == 3


@pytest.mark.django_db
def test_count_unique_show():
    conference = ConferenceFactory()
    user_1 = UserFactory()
    user_2 = UserFactory()
    UserConferenceFactory(user=user_1, conference=conference)
    UserConferenceFactory(user=user_1, conference=conference)
    UserConferenceFactory(user=user_2, conference=conference)
    assert UserConference.objects.count_unique_show(conference) == 2


@pytest.mark.django_db
def test_evaluation_avg():
    conference = ConferenceFactory()
    user_1 = UserFactory()
    user_2 = UserFactory()
    UserConferenceFactory(user=user_1, conference=conference, evaluation=1)
    UserConferenceFactory(user=user_2, conference=conference, evaluation=5)
    assert UserConference.objects.evaluation_avg(conference) == 3


@pytest.mark.django_db
def test_slide_show_avg():
    conference = ConferenceFactory()
    for _ in range(5):
        SlideFactory(conference=conference)
    user_1 = UserFactory()
    user_2 = UserFactory()
    UserConferenceFactory(user=user_1, conference=conference, slide_position=1)
    UserConferenceFactory(user=user_2, conference=conference, slide_position=5)
    assert UserConference.objects.slide_show_avg(conference) == 3

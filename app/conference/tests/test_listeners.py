import pytest
from app.conference.models.channel import Channel
from app.conference.listener import start_conference_alert_owner, evaluated_conference_alert_owner
from app.conference.factories import ChannelFactory, ConferenceFactory, UserConferenceFactory
from app.users.tests.factories import UserFactory


@pytest.mark.django_db
def test_start_conference_alert_owner_alert_false(mocker, user):
    send_message_mock = mocker.patch("app.conference.listener.send_message")
    get_bot_mock = mocker.patch("app.conference.listener.get_bot")
    conference = ConferenceFactory(owner=user)
    start_conference_alert_owner(conference, user)
    assert not send_message_mock.called
    assert not get_bot_mock.called


@pytest.mark.django_db
def test_start_conference_alert_owner_is_the_owner(mocker, user):
    send_message_mock = mocker.patch("app.conference.listener.send_message")
    get_bot_mock = mocker.patch("app.conference.listener.get_bot")
    conference = ConferenceFactory(owner=user)
    start_conference_alert_owner(conference, user)
    assert not send_message_mock.called
    assert not get_bot_mock.called


@pytest.mark.django_db
def test_start_conference_alert_owner(user, mocker):
    send_message_mock = mocker.patch("app.conference.listener.send_message")
    get_bot_mock = mocker.patch("app.conference.listener.get_bot")
    conference = ConferenceFactory(alert_to_owner=True, owner=user)
    start_conference_alert_owner(conference, UserFactory())
    assert send_message_mock.called
    assert get_bot_mock.called


@pytest.mark.django_db
def test_evaluated_conference_alert_owner_alert_false(mocker, user):
    send_message_mock = mocker.patch("app.conference.listener.send_message")
    get_bot_mock = mocker.patch("app.conference.listener.get_bot")
    conference = ConferenceFactory(owner=user)
    user_conference = UserConferenceFactory()
    evaluated_conference_alert_owner(conference, user, user_conference)
    assert not send_message_mock.called
    assert not get_bot_mock.called


@pytest.mark.django_db
def test_evaluated_conference_alert_owner_is_the_owner(mocker, user):
    send_message_mock = mocker.patch("app.conference.listener.send_message")
    get_bot_mock = mocker.patch("app.conference.listener.get_bot")
    conference = ConferenceFactory(owner=user)
    user_conference = UserConferenceFactory()
    evaluated_conference_alert_owner(conference, user, user_conference)
    assert not send_message_mock.called
    assert not get_bot_mock.called


@pytest.mark.django_db
def test_evaluated_conference_alert_owner(user, mocker):
    send_message_mock = mocker.patch("app.conference.listener.send_message")
    get_bot_mock = mocker.patch("app.conference.listener.get_bot")
    conference = ConferenceFactory(alert_to_owner=True, owner=user)
    user_conference = UserConferenceFactory()
    evaluated_conference_alert_owner(conference, UserFactory(), user_conference)
    assert send_message_mock.called
    assert get_bot_mock.called


@pytest.mark.django_db
def test_channel_active_no_change(mocker):
    send_message_mock = mocker.patch("app.conference.listener.send_message")
    channel: Channel = ChannelFactory(published=False)
    channel.name = "channel name"
    channel.save()
    assert not send_message_mock.called


@pytest.mark.django_db
def test_channel_active_change(mocker):
    send_message_mock = mocker.patch("app.conference.listener.send_message")
    channel = ChannelFactory()
    channel.published = True
    channel.save()
    assert send_message_mock.called

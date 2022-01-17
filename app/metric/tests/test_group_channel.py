from app.conference.factories import ConferenceFactory
from app.metric.factories import GroupChannelFactory
from app.metric.models.group_channel import GroupChannel
import json


def test_group_channel_doesnt_exists(bot_client):
    response = bot_client.post(
        "/api/admin/group-channels/",
        data={"external_id": "123456", "title": "group 1", "type": "group", "data": json.dumps({})},
    )
    assert response.status_code == 201
    groups = GroupChannel.objects.all()
    assert len(groups) == 1
    assert groups[0].external_id == "123456"


def test_group_channel_exists(bot_client):
    GroupChannelFactory(external_id="123456", active=False)
    response = bot_client.post(
        "/api/admin/group-channels/",
        data={"external_id": "123456", "title": "group 1", "type": "group", "data": json.dumps({})},
    )
    assert response.status_code == 200
    groups = GroupChannel.objects.all()
    assert len(groups) == 1
    assert groups[0].external_id == "123456"
    assert groups[0].active == True


def test_group_channel_desactive(bot_client):
    group: GroupChannel = GroupChannelFactory()
    response = bot_client.post(f"/api/admin/group-channels/{group.id}/desactive/")
    assert response.status_code == 200
    group.refresh_from_db()
    assert group.active == False


def test_start_conferece(bot_client):
    group: GroupChannel = GroupChannelFactory()
    conference = ConferenceFactory()
    response = bot_client.post(
        f"/api/admin/group-channels/{group.id}/start_conference/", data={"conference_id": conference.id}
    )
    assert response.status_code == 200
    group.refresh_from_db()
    assert len(group.conferences.all()) == 1


def test_start_conference_the_group_has_one(bot_client):
    group: GroupChannel = GroupChannelFactory()
    conference_1 = ConferenceFactory()
    conference_2 = ConferenceFactory()
    group.conferences.add(conference_1)
    group.save()
    response = bot_client.post(
        f"/api/admin/group-channels/{group.id}/start_conference/", data={"conference_id": conference_2.id}
    )
    assert response.status_code == 200
    group.refresh_from_db()
    assert len(group.conferences.all()) == 2


def test_find_by_external_id(bot_client):
    group: GroupChannel = GroupChannelFactory(external_id="159")
    response = bot_client.get("/api/admin/group-channels/get_by_external_id/159/")
    assert response.status_code == 200
    assert response.data["id"] == str(group.id)


def test_find_by_external_id_not_found(bot_client):
    response = bot_client.get("/api/admin/group-channels/get_by_external_id/159/")
    assert response.status_code == 404

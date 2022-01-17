import pytest
from app.conference.models.course import Course
from app.conference.factories import CategoryFactory, ChannelFactory, ConferenceFactory, CourseFactory, SlideFactory


def test_num_of_conferences(bot_client):
    course = CourseFactory()
    ConferenceFactory(active=True, course=course)
    ConferenceFactory(course=course)
    response = bot_client.get(f"/api/courses/{course.id}/", content_type="application/json")
    assert response.status_code == 200
    assert response.data["number_of_conferences"] == 2
    assert response.data["number_of_active_conferences"] == 1


def test_get_by_category(bot_client):
    category = CategoryFactory()
    course = CourseFactory(category=category)
    ConferenceFactory(active=True, course=course)
    course_2 = CourseFactory()
    ConferenceFactory(active=True, course=course_2)
    response = bot_client.get(f"/api/courses/?category={category.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(course.id)

    response = bot_client.get("/api/courses/", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 2


def test_get_visible_to_all(bot_client):
    category = CategoryFactory()
    course = CourseFactory(category=category)
    ConferenceFactory(active=True, course=course)
    ConferenceFactory(active=True, course=course)
    course_without_active_conferences = CourseFactory(category=category)  # It doesn't have active conferences
    ConferenceFactory(active=False, course=course_without_active_conferences)

    response = bot_client.get(f"/api/courses/?category={category.id}&public_courses=1", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(course.id)


def test_only_see_owns_courses(bot_client, user):
    course = CourseFactory(users=[user])
    CourseFactory()

    response = bot_client.get("/api/admin/courses/", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(course.id)


def test_create_course(bot_client, user):
    response = bot_client.post("/api/admin/courses/", data={"name": "course test"})
    assert response.status_code == 201
    assert Course.objects.filter(owners=user, name="course test").exists()


@pytest.mark.django_db
def test_course_files():
    course = CourseFactory()
    SlideFactory(voice="voice1", image="image1", conference=ConferenceFactory(course=course))
    SlideFactory(voice="voice2", image="image2", conference=ConferenceFactory(course=course))
    files = course.files
    assert len(files) == 4
    assert "voice1" in files
    assert "voice2" in files
    assert "image1" in files
    assert "image2" in files


def test_filter_by_channel(bot_client, user):
    channel = ChannelFactory(owner=user)
    course = CourseFactory(users=[user])
    ConferenceFactory(active=True, course=course)
    response = bot_client.get(f"/api/courses/?channel={channel.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1


def test_filter_by_other_channel(bot_client):
    channel = ChannelFactory()
    course = CourseFactory()
    ConferenceFactory(active=True, course=course)
    response = bot_client.get(f"/api/courses/?channel={channel.id}", content_type="application/json")
    assert response.status_code == 200
    assert len(response.data["results"]) == 0

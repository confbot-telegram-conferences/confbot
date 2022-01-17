from app.conference.models.channel import Channel
from app.users.tests.factories import UserFactory
from factory.django import DjangoModelFactory
import factory
from . import models


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = models.Category

    name = factory.Faker("last_name")


class ChannelFactory(DjangoModelFactory):
    class Meta:
        model = Channel

    name = factory.Faker("last_name")
    owner = factory.SubFactory(UserFactory)


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = models.Course

    name = factory.Faker("last_name")
    category = factory.SubFactory(CategoryFactory)

    @factory.post_generation
    def users(self, _, users):
        if users:
            self.owners.set(users)


class ConferenceFactory(DjangoModelFactory):
    class Meta:
        model = models.Conference

    name = factory.Faker("last_name")
    course = factory.SubFactory(CourseFactory)


class SlideFactory(DjangoModelFactory):
    class Meta:
        model = models.Slide

    text = factory.Faker("last_name")
    conference = factory.SubFactory(ConferenceFactory)


class UserConferenceFactory(DjangoModelFactory):
    class Meta:
        model = models.UserConference

    conference = factory.SubFactory(ConferenceFactory)
    user = factory.SubFactory(UserFactory)

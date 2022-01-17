import factory
from factory.django import DjangoModelFactory
from . import models


class GroupChannelFactory(DjangoModelFactory):
    class Meta:
        model = models.GroupChannel

    external_id = factory.Faker("last_name")
    title = factory.Faker("last_name")
    type = "group"

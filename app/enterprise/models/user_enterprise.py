from django.db.models import ForeignKey, CASCADE
from app.users.models import User
from app.utils.models import BaseModel
from .enterprise import Enterprise


class UserEnterprise(BaseModel):
    """
    This class can be used in the future, to register the user permission by enterprise
    """

    user = ForeignKey(User, on_delete=CASCADE)
    enterprise = ForeignKey(Enterprise, on_delete=CASCADE)

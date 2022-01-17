from django.core.validators import MaxValueValidator, MinValueValidator
from app.conference.models import Conference, Slide
from django.utils.translation import gettext_lazy as _
from django.db.models import ForeignKey, CASCADE, IntegerField, QuerySet, Avg, Sum
from app.utils.models import BaseModel
from app.users.models import User


class ManagerQuerySet(QuerySet):
    def get_by_conference_user(self, conference: Conference, user: User):
        return self.get(user=user, conference=conference)

    def update_or_create_with_slide(self, conference: Conference, user: User, slide: Slide) -> "UserConference":
        try:
            entity: UserConference = self.get(conference=conference, user=user)
            if entity.slide_position > slide.position:
                return entity
            entity.slide_position = slide.position
            entity.save()
            return entity
        except UserConference.DoesNotExist:
            return self.create(conference=conference, user=user, slide_position=slide.position)

    def count_unique_show(self, conference: Conference):
        return self.filter(conference=conference).distinct("user").count()

    def evaluation_avg(self, conference: Conference):
        evaluation_avg = self.filter(conference=conference, evaluation__gt=0).aggregate(
            evaluation_avg=Avg("evaluation")
        )["evaluation_avg"]
        return round(evaluation_avg, 2) if evaluation_avg else 0

    def slide_show_avg(self, conference: Conference):
        slide_position_sum = self.filter(conference=conference).aggregate(slide_position_sum=Sum("slide_position"))[
            "slide_position_sum"
        ]
        count_show = self.count_unique_show(conference=conference)
        if not slide_position_sum or not count_show:
            return 0
        return round(slide_position_sum / count_show, 2)

    def statistics(self, conference: Conference):
        return {
            "count_unique_show": self.count_unique_show(conference),
            "evaluation_avg": self.evaluation_avg(conference),
            "slide_show_avg": self.slide_show_avg(conference),
            "count_slide": conference.number_of_slides,
        }


class UserConference(BaseModel):
    conference: Conference = ForeignKey(Conference, related_name="user_conferences", on_delete=CASCADE)
    user = ForeignKey(User, null=True, related_name="user_conferences", on_delete=CASCADE)
    slide_position = IntegerField(_("Slide Position"), default=1)
    evaluation = IntegerField(_("Evaluation"), default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])

    objects: ManagerQuerySet = ManagerQuerySet.as_manager()

    def __str__(self) -> str:
        return f"Conf: {self.conference}, User: {self.user}"

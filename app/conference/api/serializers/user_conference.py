from app.conference.models.user_conference import UserConference
from rest_framework import serializers


class UserConferenceEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConference
        fields = ["evaluation"]

    def validate(self, data):
        if self.instance.slide_position < self.instance.conference.number_of_slides:
            raise serializers.ValidationError("You need to complete the conference visualitation to evaluate it.")
        return data

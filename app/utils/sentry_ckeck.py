from app.conference.models.conference import Conference
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from app.conference.tasks import sentry_check_task


@api_view(["GET"])
@permission_classes([])
def sentry_check(request, pk):
    """
    This endpoint is used to test the integration with sentry.
    """
    sentry_check_task.apply_async(kwargs={"value": pk})
    object = Conference.objects.get(pk=pk)
    return Response({"name": object.name})

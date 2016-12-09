from django.conf.urls import url, include
from rest_framework import routers
from .views import ModerationActionModelViewSet, slack_response

router = routers.DefaultRouter()
router.register(r'moderations', ModerationActionModelViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^slack/response/$', slack_response, name='slack_response'),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework'))
]

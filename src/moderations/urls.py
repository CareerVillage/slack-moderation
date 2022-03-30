from django.urls import re_path, include
from rest_framework import routers
from .views import ModerationActionModelViewSet, slack_response, generate_stats

router = routers.DefaultRouter()
router.register(r'moderations', ModerationActionModelViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
app_name = 'moderations'
urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path(r'^slack/response/$', slack_response, name='slack_response'),
    re_path(r'^slack/generate-stats/$', generate_stats, name='generate_stats'),
    re_path(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework'))
]

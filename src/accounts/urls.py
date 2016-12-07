from django.conf.urls import url
from .views import AuthListView


urlpatterns = [
    url(r'^auth/$', AuthListView.as_view(), name='auth'),
]

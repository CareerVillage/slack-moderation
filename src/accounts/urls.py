from django.conf.urls import url
from .views import AuthListView

app_name = 'accounts'
urlpatterns = [
    url(r'^auth/$', AuthListView.as_view(), name='auth'),
]

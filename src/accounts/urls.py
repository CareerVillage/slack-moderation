from django.urls import re_path
from .views import AuthListView

app_name = 'accounts'
urlpatterns = [
    re_path(r'^auth/$', AuthListView.as_view(), name='auth'),
]

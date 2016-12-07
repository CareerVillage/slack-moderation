from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import ListView
from .models import AuthToken


class AuthListView(ListView):
    """
    Show Slack connect button with required data
    """
    model = AuthToken
    template_name = 'auth.html'


def social_complete(*args, **kwargs):
    data = kwargs.get('response')
    print data
    service_name = 'slack'
    channel = data['incoming_webhook']['channel']
    access_token = data['access_token']
    entry = AuthToken.objects.filter(service_name=service_name,
                                     service_entity_auth_name=channel).first()
    if not entry:
        AuthToken.objects.create(service_name=service_name,
                                 service_entity_auth_name=channel,
                                 service_auth_token=access_token,
                                 username=data['user'])
    return redirect(reverse('accounts:auth'))


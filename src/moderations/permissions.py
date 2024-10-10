import typing

from django.conf import settings
from django.http import HttpRequest
from rest_framework import permissions


class HasModerationApiKey(permissions.BasePermission):
    """
    Allows access only to users with a valid moderation API key.
    """

    def get_from_authorization(self, request: HttpRequest) -> typing.Optional[str]:
        expected_header_keyword = "Api-Key"
        authorization = request.META.get("HTTP_AUTHORIZATION", "")

        if not authorization:
            return None

        keyword, found, key = authorization.partition(" ")

        if not found:
            return None

        if keyword.lower() != expected_header_keyword.lower():
            return None

        return key

    def has_permission(self, request, view):
        # Verifiy if authorization header contains API key
        key_in_header = self.get_from_authorization(request)

        if not key_in_header:
            return False
        return key_in_header == settings.CV_MODERATION_API_KEY

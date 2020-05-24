from django.urls import path

from . import api

urlpatterns = [
    path(
        'create_access',
        api.create_access,
    ),
    path(
        '',
        api.get_access_by_key
    )
]

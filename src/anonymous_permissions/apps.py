# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals, print_function
from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.signals import pre_save


class AnonymousPermissionsConfig(AppConfig):
    name = 'anonymous_permissions'

    def ready(self):
        import anonymous_permissions.checks  # noqa
        UserModel = get_user_model()

        pre_save.connect(disable_anon_user_password_save, sender=UserModel)


def disable_anon_user_password_save(sender, instance, **kwargs):
    if instance.username == settings.ANONYMOUS_USERNAME:
        instance.passwork = make_password(None)

# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals, print_function
from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.signals import pre_save

caches = (
    '_group_perm_cache',
    '_user_perm_cache',
    '_dsspermissionchecker',
    '_officepermissionchecker',
    '_perm_cache',
    '_dss_acl_cache',
)


class AnonymousPermissionsConfig(AppConfig):
    name = 'anonymous_permissions'

    def ready(self):
        import anonymous_permissions.checks  # noqa
        UserModel = get_user_model()

        pre_save.connect(disable_anon_user_password_save, sender=UserModel)


def disable_anon_user_password_save(sender, instance, **kwargs):
    field = getattr(instance, instance.USERNAME_FIELD)
    if field == settings.ANONYMOUS_USERNAME:
        instance.password = make_password(None)
        for cache in caches:
            if hasattr(instance, cache):
                delattr(instance, cache)

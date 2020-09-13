# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.core.checks import Error, register


@register()
def check_settings(app_configs, **kwargs):
    errors = []
    ok = hasattr(settings, 'ANONYMOUS_USERNAME')
    if not ok:
        errors.append(
            Error(
                'Missing ANONYMOUS_USERNAME',
                hint='set `ANONYMOUS_USERNAME` attribute in your settings.py to a valid username',
                obj=None,
                id='anonymous_permissions.E001',
            )
        )
    # User = get_user_model()
    # try:
    #     u = User.objects.get(**{User.USERNAME_FIELD:settings.ANONYMOUS_USERNAME})
    # except User.DoesNotExist:
    #     errors.append(
    #         Error(
    #             'Wrong ANONYMOUS_USERNAME',
    #             hint='`settings.ANONYMOUS_USERNAME` point to a non existent user',
    #             obj=None,
    #             id='anonymous_permissions.E002',
    #         )
    #     )

    return errors

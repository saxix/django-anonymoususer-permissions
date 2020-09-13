# -*- coding: utf-8 -*-
import logging

import functools
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password

from anonymous_permissions import compat

logger = logging.getLogger(__name__)


@compat.lru_cache()
def get_anonymous_user():
    UserModel = get_user_model()
    return UserModel._default_manager.get(**{UserModel.USERNAME_FIELD: settings.ANONYMOUS_USERNAME})


def createanonymoususer(**user_data):
    UserModel = get_user_model()
    user_data[UserModel.USERNAME_FIELD] = settings.ANONYMOUS_USERNAME
    user_data['password'] = make_password(None)
    user_data['is_staff'] = False
    user_data['is_active'] = True
    user_data['is_superuser'] = False

    manager = UserModel._default_manager
    return manager.create(**user_data)


class AnonymousUserBackend(ModelBackend):

    def get_all_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous:
            if not hasattr(user_obj, '_perm_cache'):
                anon_user = get_anonymous_user()
                user_obj._perm_cache = self.get_all_permissions(anon_user)
            return user_obj._perm_cache
        return super(AnonymousUserBackend, self).get_all_permissions(user_obj)

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username == settings.ANONYMOUS_USERNAME:
            return None
        return super(AnonymousUserBackend, self).authenticate(request, username, password, **kwargs)

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active and not user_obj.is_anonymous:
            return False
        return perm in self.get_all_permissions(user_obj)

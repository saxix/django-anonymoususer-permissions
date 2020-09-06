# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from contextlib import ContextDecorator

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.contenttypes.models import ContentType

from anonymous_permissions import compat
from anonymous_permissions.apps import caches
from anonymous_permissions.backend import get_anonymous_user

pytestmarker = pytest.mark.djangodb


def test_cache(anonymous):
    get_anonymous_user()
    get_anonymous_user()
    info = get_anonymous_user.cache_info()
    assert info.hits == 2
    assert info.misses == 1


def test_get_all_permissions(anonymous, backend):
    assert not backend.get_all_permissions(anonymous)


def test_get_all_permissions_st(anonymous, backend):
    user = AnonymousUser()
    assert not backend.get_all_permissions(user)

    # again to check _perm_cache
    assert not backend.get_all_permissions(user)


def test_login_success(rf, backend, admin_user):
    request = rf.post('/')
    if compat.DJANGO_PRE_11:
        assert backend.authenticate(username=admin_user.username,
                                    password='password')
    else:
        assert backend.authenticate(request,
                                    username=admin_user.username,
                                    password='password')


def test_login_fail(rf, backend):
    request = rf.post('/')
    if compat.DJANGO_PRE_11:
        assert backend.authenticate(username=settings.ANONYMOUS_USERNAME) is None
    else:
        assert backend.authenticate(request,
                                    username=settings.ANONYMOUS_USERNAME) is None


def test_has_perm(anonymous, backend):
    assert not backend.has_perm(AnonymousUser(), "auth.change_user")

    with user_grant_permissions(anonymous, ["auth.change_user"]):
        assert backend.has_perm(AnonymousUser(), "auth.change_user")

    anonymous.is_active = False
    assert not backend.has_perm(AnonymousUser(), "auth.change_user")


class user_grant_permissions(object):  # noqa
    caches = caches

    def __init__(self, user, permissions=None, clear_caches=False):
        self.user = user
        self.permissions = permissions
        self._added = []
        self._clear_caches = clear_caches

    def clear_caches(self):
        for cache in self.caches:
            if hasattr(self.user, cache):
                delattr(self.user, cache)

    def __enter__(self):
        if self._clear_caches:
            self.clear_caches()

        for permission_name in self.permissions:
            try:
                app_label, codename = permission_name.split('.')
            except ValueError:
                raise ValueError("Invalid permission name `{0}`".format(permission_name))
            __, model_name = codename.rsplit('_', 1)
            ct = ContentType.objects.get(app_label__iexact=app_label,
                                         model__iexact=model_name)
            permission = Permission.objects.get(content_type=ct,
                                                codename=codename)
            self._added.append(permission.id)
            self.user.user_permissions.add(permission)
            self.user.save()
        return self.user

    def __exit__(self, e_typ, e_val, trcbak):
        self.user.user_permissions.filter(id__in=self._added).delete()

        if e_typ:
            raise e_typ(e_val).with_traceback(trcbak)

    def start(self):
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        return result

    def stop(self):
        """Stop an active patch."""
        return self.__exit__(None, None, None)

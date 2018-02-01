# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from anonymous_permissions.checks import check_settings


def test_missing_settings(settings):
    delattr(settings, 'ANONYMOUS_USERNAME')
    ret = check_settings(None)
    assert ret[0].msg == 'Missing ANONYMOUS_USERNAME'


def test_settings(settings):
    ret = check_settings(None)
    assert ret == []

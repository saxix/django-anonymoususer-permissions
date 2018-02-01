# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from io import StringIO

import pytest
from django.core.management import call_command


@pytest.mark.django_db()
def test_command():
    ret = call_command('createanonymoususer')
    assert ret is None


@pytest.mark.django_db()
def test_command_missing_settings(settings):
    delattr(settings, 'ANONYMOUS_USERNAME')
    with pytest.raises(SystemExit):
        call_command('createanonymoususer',
                     stdout=StringIO(),
                     stderr=StringIO())


@pytest.mark.django_db()
def test_command_extra_args(settings):
    call_command('createanonymoususer',
                 email='aa@bb.com',
                 stdout=StringIO(),
                 stderr=StringIO())


@pytest.mark.django_db()
def test_command_interactive(settings):
    call_command('createanonymoususer',
                 interactive=False,
                 stdout=StringIO(),
                 stderr=StringIO())

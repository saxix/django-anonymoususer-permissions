# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import django
import six

DJANGO3 = django.VERSION[0] == 3
DJANGO2 = django.VERSION[0] == 2
#
# if DJANGO2 or DJANGO3:
#     def is_anonymous(user):
#         return user.is_anonymous
#
# else:
#     def is_anonymous(user):
#         return user.is_anonymous()

if six.PY2:
    from django.utils.lru_cache import lru_cache
else:
    from functools import lru_cache

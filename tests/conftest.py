import pytest

from anonymous_permissions.backend import get_anonymous_user, AnonymousUserBackend, createanonymoususer


@pytest.fixture
def anonymous(db):
    createanonymoususer()
    return get_anonymous_user()


@pytest.fixture
def backend():
    return AnonymousUserBackend()

#!/usr/bin/env python
import os
import imp
import codecs
from setuptools import setup, find_packages

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
init = os.path.join(ROOT, 'src', 'anonymous_permissions', '__init__.py')
app = imp.load_source('anonymous_permissions', init)


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts)).read()


tests_requires = read('src/requirements/testing.pip')
install_requires = read('src/requirements/install.pip')
dev_requires = read('src/requirements/develop.pip')

setup(
    name=app.NAME,
    version=app.VERSION,
    url='https://github.com/saxix/django-anonymoususer-permissions',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    license="MIT",
    long_description=codecs.open('README.rst').read(),
    description='Small backend to grant permission to Anonymous using django admin interface',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_requires,
    extras_require={
        'dev': dev_requires,
        'tests': tests_requires,
    },
    platforms=['linux'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers'
    ]
)

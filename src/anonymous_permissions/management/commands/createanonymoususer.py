"""
Management utility to create anonymous user.
"""
from __future__ import unicode_literals
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.utils.text import capfirst

from anonymous_permissions.backend import createanonymoususer


class NotRunningInTTYException(Exception):
    pass


class Command(BaseCommand):
    help = 'Used to create a anonymous user.'
    requires_migrations_checks = True
    requires_system_checks = False
    stealth_options = ('stdin',)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.UserModel = get_user_model()
        self.username_field = self.UserModel._meta.get_field(self.UserModel.USERNAME_FIELD)

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help=('Tells Django to NOT prompt the user for input of any kind. '
                  'You must use --%s with --noinput, along with an option for '
                  'any other required field. anonymoususers created with --noinput will '
                  'not be able to log in until they\'re given a valid password.' %
                  self.UserModel.USERNAME_FIELD
                  ),
        )
        parser.add_argument(
            '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".',
        )
        parser.add_argument(
            '--email', action='store', dest='email',
            default="noreply@noreply.com",
            help='Specifies the email to use. Default is "noreply@noreply.com".',
        )
        for field in self.UserModel.REQUIRED_FIELDS:
            if field == 'email':
                continue
            parser.add_argument(
                '--%s' % field, dest=field, default=None,
                help='Specifies the %s for the anonymoususer.' % field,
            )

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super(Command, self).execute(*args, **options)

    def handle(self, *args, **options):  # noqa
        if not hasattr(settings, 'ANONYMOUS_USERNAME'):
            self.stderr.write('set `ANONYMOUS_USERNAME` attribute in your settings.py to a valid username')
            sys.exit(1)

        username = settings.ANONYMOUS_USERNAME
        database = options['database']

        # If not provided, create the user with an unusable password
        user_data = {}
        # Same as user_data but with foreign keys as fake model instances
        # instead of raw IDs.
        fake_user_data = {}

        # Do quick and dirty validation if --noinput
        if not options['interactive']:
            try:
                username = self.username_field.clean(username, None)

                for field_name in self.UserModel.REQUIRED_FIELDS:
                    if options[field_name]:
                        field = self.UserModel._meta.get_field(field_name)
                        user_data[field_name] = field.clean(options[field_name], None)
                    else:
                        raise CommandError("You must use --%s with --noinput." % field_name)
            except exceptions.ValidationError as e:
                raise CommandError('; '.join(e.messages))

        else:
            # Enclose this whole thing in a try/except to catch
            # KeyboardInterrupt and exit gracefully.
            try:

                if hasattr(self.stdin, 'isatty') and not self.stdin.isatty():
                    raise NotRunningInTTYException("Not running in a TTY")

                for field_name in self.UserModel.REQUIRED_FIELDS:
                    field = self.UserModel._meta.get_field(field_name)
                    user_data[field_name] = options[field_name]
                    while user_data[field_name] is None:
                        message = '%s%s: ' % (
                            capfirst(field.verbose_name),
                            ' (%s.%s)' % (
                                field.remote_field.model._meta.object_name,
                                field.remote_field.field_name,
                            ) if field.remote_field else '',
                        )
                        input_value = self.get_input_data(field, message)
                        user_data[field_name] = input_value
                        fake_user_data[field_name] = input_value

                        # Wrap any foreign keys in fake model instances
                        if field.remote_field:
                            fake_user_data[field_name] = field.remote_field.model(input_value)

            except KeyboardInterrupt:
                self.stderr.write("\nOperation cancelled.")
                sys.exit(1)

            except NotRunningInTTYException:
                self.stdout.write(
                    "Anonymous user creation skipped due to not running in a TTY. "
                    "You can run `manage.py createanonymoususer` in your project "
                    "to create one manually."
                )

        manager = self.UserModel._default_manager.db_manager(database)
        if manager.filter(**{self.UserModel.USERNAME_FIELD: username}).exists():
            self.stderr.write("User `%s` already exists" % username)
            sys.exit(1)

        createanonymoususer(**user_data)

        if options['verbosity'] >= 1:
            self.stdout.write("Anonymous user `%s` created successfully." % username)

    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if default and raw_value == '':
            raw_value = default
        try:
            val = field.clean(raw_value, None)
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % '; '.join(e.messages))
            val = None

        return val

"""Compiles the per-route i18n message files

The final .po and .mo files will be stored
in the directory side by side with the original locale
directory and name with postfix _compiled.
For example, if the original directory is:
/path/to/locale, the compiled directory will be
/path/to/locale_compiled.

Do not edit files in the _compiled directory.
"""
import os
from django.conf import settings as django_settings
from babel.messages.pofile import read_po
from svelte_i18n.const import ROUTE_COMMENT_PREFIX

class Compiler:
    """Creates the per-route message .po and .mo files.
    The main method is .compile_messages()
    """

    def __init__(self, app_name): #pylint: disable=missing-docstring
        self.app_name = app_name
        self.config = django_settings.SVELTE_I18N[app_name]
        # nested dicts, first key - lang, second key - route
        self.per_route_catalogs = dict()


    def compile_messages(self):
        """Reads the original .po files and creates per-route .po files"""
        for lang, path in self.get_per_language_pofile_paths():
            source_catalog = read_po(open(path, 'r'))
            for message in source_catalog:
                if not message.id:
                    continue

                for route in self.get_message_routes(message):
                    cat = self.get_catalog(lang, route)
                    cat[message.id] = message

        self.write_pofiles()
        self.write_mofiles()

    def write_mofiles(self): #pylint: disable=missing-docstring
        pass


    def write_pofiles(self): #pylint: disable=missing-docstring
        pass


    def get_catalog(self, lang, route):
        """Returns a catalog for a given language and the route.
        If catalog is missing, create it.
        """


    def get_per_language_pofile_paths(self):
        """Yields tuples (lang, filepath)
        `filepath` - filesystem path to the pofile containing
        all messages for the given language.

        Route information is stored in the message comments.
        """
        locale_dir = self.config['locale_dir']
        for lang in os.listdir(locale_dir):
            lang_dir = os.path.join(locale_dir, lang)
            if os.path.isdir(lang_dir):
                pofile_path = os.path.join(lang_dir, 'LC_MESSAGES', 'svelte.po')
                if os.path.exists(pofile_path):
                    yield lang, pofile_path


    def get_message_routes(self, message):
        """Returns routes where `message` appears"""
        routes = list()
        prefix_len = len(ROUTE_COMMENT_PREFIX)
        for comment in message.auto_comments:
            if comment.startswith(ROUTE_COMMENT_PREFIX):
                route = comment[prefix_len:]
                routes.append(route)
        return routes

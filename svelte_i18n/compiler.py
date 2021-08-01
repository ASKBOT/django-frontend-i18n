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
from collections import defaultdict
from django.conf import settings as django_settings
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog
from svelte_i18n.const import ROUTE_COMMENT_PREFIX
from svelte_i18n.utils import get_compiled_catalog_path

class LangRouteCatalogs:
    """Factory class returning per-route catalog for a given language"""
    def __init__(self):
        self.route_catalogs = dict()


    def __getitem__(self, lang):
        """Emulates the dict['key'] access"""
        if lang not in self.route_catalogs:
            self.route_catalogs[lang] = defaultdict(self.get_catalog_factory(lang))
        return self.route_catalogs[lang]


    def items(self):
        """Emulates dict().items()"""
        return self.route_catalogs.items()


    @classmethod
    def get_catalog_factory(cls, lang):
        """Returns a factory method that creates
        a babel Catalog for a given language"""
        def catalog_factory():
            return Catalog(locale=lang)
        return catalog_factory


class Compiler:
    """Creates the per-route message .po and .mo files.
    The main method is .compile_messages()
    """

    def __init__(self, app_name): #pylint: disable=missing-docstring
        self.app_name = app_name
        self.config = django_settings.SVELTE_I18N[app_name]
        # nested dicts, first key - lang, second key - route
        self.lang_route_catalogs = LangRouteCatalogs()


    def compile_messages(self):
        """Reads the original .po files and creates per-route .po files"""
        for lang, path in self.get_per_language_pofile_paths():
            source_catalog = read_po(open(path, 'r'))
            for message in source_catalog:
                if not message.id:
                    continue

                for route in self.get_message_routes(message):
                    cat = self.lang_route_catalogs[lang][route]
                    cat[message.id] = message

        self.write_catalogs()

    def write_catalogs(self): #pylint: disable=missing-docstring
        """Writes .po and .mo files for the
        per language per route catalogs"""
        for lang, route_catalogs in self.lang_route_catalogs.items():
            for route, catalog in route_catalogs.items():
                pofile_path = get_compiled_catalog_path(self.app_name, lang, route, '.po')
                dirname = os.path.dirname(pofile_path)
                os.makedirs(dirname, exist_ok=True)
                write_po(open(pofile_path, 'wb'), catalog)
                mofile_path = pofile_path[:-3] + '.mo'
                mofile_obj = open(mofile_path, 'wb')
                write_mo(open(mofile_path, 'wb'), catalog)


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


    @classmethod
    def get_message_routes(cls, message):
        """Returns routes where `message` appears"""
        routes = list()
        prefix_len = len(ROUTE_COMMENT_PREFIX)
        for comment in message.auto_comments:
            if comment.startswith(ROUTE_COMMENT_PREFIX):
                route = comment[prefix_len:]
                routes.append(route)
        return routes

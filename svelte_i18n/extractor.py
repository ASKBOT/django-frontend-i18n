"""Contains the message extractor file"""
import os
import esprima
from bs4 import BeautifulSoup
from django.conf import settings as django_settings
from babel.messages.catalog import Catalog, Message
from babel.messages.extract import extract_from_file
from babel.messages.pofile import write_po
from svelte_i18n import routify
from svelte_i18n.utils import is_route, get_route, get_app_file_path

class Extractor:
    """Extracts i18n messages from .js and .svelte files into svelte.po file
    of the default locale.

    Marks each phrase with the route where this phrase is used.

    Main methods are `.extract_messages()` and `.write_pofile()`
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.config = django_settings.SVELTE_I18N[self.app_name]
        self.catalog = Catalog(locale=django_settings.LANGUAGE_CODE)

    def extract_messages(self):
        """Extracts messages for the app"""
        # iterate over the routes directory
        routes_dir = self.config['routes_dir']

        for root, _, files in os.walk(routes_dir):
            rel_dir = root.replace(routes_dir, '', 1).lstrip(os.path.sep)
            if not is_route(self.app_name, rel_dir):
                #print(f'non-route: {rel_dir}')
                continue

            for fname in files:
                if not is_route(self.app_name, fname):
                    #print(f'non-route: {fname}')
                    continue

                path = os.path.join(routes_dir, rel_dir, fname)
                path = os.path.normpath(path)
                route = get_route(self.app_name, path)
                self.process_route(path, route)


    def write_pofile(self):
        """Writes catalog of the app to the pofile"""
        with self.open_pofile() as po_file:
            write_po(po_file, self.catalog)


    def open_pofile(self):
        """Returns writeable file object at the source language
        pofile location.
        Insures that all parent directories are created.
        """
        locale_dir = self.config['locale_dir']
        lang = django_settings.LANGUAGE_CODE
        src_locale_dir = os.path.join(locale_dir, lang, 'LC_MESSAGES')
        os.makedirs(src_locale_dir, exist_ok=True)
        pofile_path = os.path.join(src_locale_dir, 'svelte.po')
        return open(pofile_path, 'wb')


    def process_route(self, path, route):
        """Extracts messages for the route and all
        the imported files (recursively), EXCLUDING
        the third party libraries.

        * `path` - path to the route file relative
           to the app's routes root.
        * `app_name` - name of the Svelte app.
        """
        paths = [path]

        # Routify uses additional per-route files: layouts, reset and fallback.
        if self.config['router_type'] == 'routify':
            paths.extend(routify.get_special_route_files(self.app_name, path))

        # In addition to the thus far found files for this route,
        # recursively find imported files, excluding those
        # that are outside of the 'app_src_dir' - (i.e. excluding the 3rd party libs)
        for used_file_path in self.get_route_files_recursive(paths):
            # and extract the i18n messages from all of them
            self.extract_messages_from_file(used_file_path, route)


    def get_route_files_recursive(self, paths):
        """Returns list of all files used in the route,
        belonging to the current app.
        Does not include 3rd party library files.
        """
        untested_paths = set(paths)
        tested_paths = set()
        while untested_paths:
            path = untested_paths.pop()
            more_paths = set(self.get_imported_paths(path))
            tested_paths.add(path)
            untested_paths |= (more_paths - tested_paths)

        return list(tested_paths)


    def get_imported_paths(self, path):
        """For a given file, returns paths of the imported files
        relative to the router root"""
        src = open(path).read()
        script = BeautifulSoup(src, 'lxml').find('script')
        if not script:
            return list()

        tokens = esprima.tokenize(script.text)
        paths = list()
        idx = 0

        while idx < len(tokens):
            token = tokens[idx]
            if token.type == 'Keyword' and token.value == 'import':
                idx += 1
                imported_path, new_idx = self.get_imported_path(tokens, idx, path)
                if imported_path and self.file_exists(imported_path):
                    paths.append(imported_path)
                if new_idx <= idx:
                    raise ValueError(f'Could not extract imported paths from {path}')
                idx = new_idx
            else:
                idx += 1
        return paths


    def file_exists(self, path):
        """Returns `true` if path exists relative
        to the routes path"""
        app_src_dir = self.config['app_src_dir']
        #must be within the app and must exist
        return path.startswith(app_src_dir) and os.path.exists(path)


    def get_imported_path(self, tokens, idx, container_path):
        """Extracts import path or the module name from the ES token stream.

        Returns a tuple: (path, idx) where path is the file path
        if it can be found within the project source code, or `None`.
        idx is the next token stream position."""
        token = tokens[idx]
        if token.type == 'Punctuator':
            if token.value == '{':
                path, next_idx = self.get_statically_imported_path(tokens, idx + 1)
                return self.get_normpath(path, container_path), next_idx
            if token.value == '(':
                path, next_idx = self.get_dynamically_imported_path(tokens, idx + 1)
                return self.get_normpath(path, container_path), next_idx
            return None, idx

        if token.type == 'Identifier':
            path, next_idx = self.get_statically_imported_path(tokens, idx + 1)
            return self.get_normpath(path, container_path), next_idx
        return None, idx + 1


    @classmethod
    def get_normpath(cls, path, container_path):
        """Returns path relative to the routes_root"""
        if path.startswith('.'):
            container_dir = os.path.dirname(container_path)
            return os.path.normpath(os.path.join(container_dir, path))
        return path


    @classmethod
    def get_statically_imported_path(cls, tokens, idx):
        """Returns import path or the module name coming after the
        `from` keyword"""
        end = len(tokens)
        while idx < end:
            token = tokens[idx]
            if token.type == 'Identifier' and token.value == 'from':
                idx += 1
                token = tokens[idx]
                if token.type == 'String':
                    value = token.value
                    return value.strip('"').strip("'"), idx + 1
                raise ValueError('Unexpected token')
            idx += 1
        return None, idx

    @classmethod
    def get_dynamically_imported_path(cls, tokens, idx):
        """Returns import path or the module name coming after the (
        punctuator"""
        idx += 1
        token = tokens[idx]
        if token.type == 'Punctuator' and token.value == '(':
            idx += 1
            token = tokens[idx]
            if token.type == 'String':
                value = token.value
                return value.strip('"').strip("'"), idx + 1
            raise ValueError('Unexpected token')
        raise ValueError('Unexpected token')



    def extract_messages_from_file(self, path, route):
        """Extracts messages from the file at path into the
        Babel `Catalog` object

        `path` - absolute path to the file corresponding to the route.
        """
        results = extract_from_file('javascript',
                                    path,
                                    comment_tags=self.config['comment_tags'])
        for line_no, msg_id, tr_comments, _ in results:
            self.add_message(msg_id=msg_id,
                             line_no=line_no,
                             file_path=path,
                             route=route,
                             translator_comments=tr_comments)


    def add_message(self, msg_id=None, #pylint: disable=too-many-arguments
                     line_no=None, file_path=None,
                     route=None, translator_comments=None):
        """Adds message to the catalog"""
        msg = self.catalog.get(msg_id) or Message(msg_id)
        app_file_path = get_app_file_path(self.app_name, file_path)
        msg.locations.append((app_file_path, line_no))
        for comment in translator_comments:
            msg.user_comments.append(self.format_translator_comment(comment, app_file_path))
        msg.auto_comments.append(f'route: {route}')
        self.catalog[msg_id] = msg


    def format_translator_comment(self, comment, app_file_path):
        """Removes the translation comment prefix"""
        for tag in self.config['comment_tags']:
            if comment.startswith(tag):
                comment = comment[len(tag):].strip()
        return f'{app_file_path}: {comment}'

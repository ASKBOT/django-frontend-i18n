"""Contains the message extractor file"""
import os
from django.conf import settings as django_settings
from django.core.management.commands.makemessages import plural_forms_re
from babel.core import Locale
from babel.messages.catalog import Message
from babel.messages.extract import extract_from_file
from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog
from frontend_i18n.utils import get_app_file_path

class Extractor:
    """Extracts i18n messages from files in the frontend source directory,
    with file extensions, specfified in the FRONTEND_I18N setting.
    with specified file extematching file extensions.
    The messages will be placed in a catalog named by the app name,
    used as key in the FRONTEND_I18N setting dictionary.

    Main methods are `.extract_messages()` and `.write_pofile()`
    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.config = django_settings.FRONTEND_I18N[self.app_name]
        self.catalog = self.read_pofile() or Catalog()

    def extract_messages(self):
        """Extracts messages for the app"""
        # iterate over the app source directory
        src_dir = self.config['src_dir']

        for root, _, files in os.walk(src_dir):
            rel_dir = root.replace(src_dir, '', 1).lstrip(os.path.sep)
            for fname in files:
                ext = os.path.splitext(fname)[1]
                if ext not in self.config['file_extensions']:
                    continue

                path = os.path.join(src_dir, rel_dir, fname)
                path = os.path.normpath(path)
                self.extract_messages_from_file(path)


    def read_pofile(self):
        """Reads pofile and returns the catalog,
        if file does not exist, returns None
        """
        try:
            with self.open_pofile('rb') as po_file:
                return read_po(po_file, locale=self.get_locale())

        except IOError:
            return None


    def get_locale(self):
        """Returns Babel `Locale` object for the source language"""
        return Locale.parse(django_settings.LANGUAGE_CODE)

    def get_plural_forms_header(self, po_file):
        """Returns string with plural forms header, like in django makemessages command"""
        for line in po_file:
            match = plural_forms_re.match(line)
            if match:
                return match.group(0)


    def write_pofile(self):
        """Writes catalog of the app to the pofile"""
        with self.open_pofile('wb') as po_file:
            write_po(po_file, self.catalog)


    def open_pofile(self, mode):
        """
        `mode` - is the file open mode.

        Returns file object at the source language
        pofile location.
        Insures that all parent directories are created.
        """
        locale_dir = self.config['locale_dir']
        lang = django_settings.LANGUAGE_CODE
        src_locale_dir = os.path.join(locale_dir, lang, 'LC_MESSAGES')
        os.makedirs(src_locale_dir, exist_ok=True)
        pofile_path = os.path.join(src_locale_dir, f'{self.app_name}.po')
        return open(pofile_path, mode)


    def extract_messages_from_file(self, path):
        """Extracts messages from the file at path into the
        Babel `Catalog` object

        `path` - absolute path to the file where to look for the i18n strings.
        """
        results = extract_from_file('javascript',
                                    path,
                                    comment_tags=self.config.get('comment_tags', ('tr:',)))
        for line_no, msg_id, tr_comments, _ in results:
            self.add_message(msg_id=msg_id,
                             line_no=line_no,
                             file_path=path,
                             translator_comments=tr_comments)


    def add_message(self, msg_id=None, #pylint: disable=too-many-arguments
                    line_no=None, file_path=None, translator_comments=None):
        """Adds message to the catalog"""
        msg = self.catalog.get(msg_id) or Message(msg_id)
        app_file_path = get_app_file_path(self.app_name, file_path)
        msg.locations.append((app_file_path, line_no))
        for comment in translator_comments:
            msg.user_comments.append(self.format_translator_comment(comment, app_file_path))
        self.catalog[msg_id] = msg


    def format_translator_comment(self, comment, app_file_path):
        """Removes the translation comment prefix"""
        for tag in self.config['comment_tags']:
            if comment.startswith(tag):
                comment = comment[len(tag):].strip()
        return f'{app_file_path}: {comment}'

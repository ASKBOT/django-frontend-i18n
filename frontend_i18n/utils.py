"""Utility functions"""
import fnmatch
import os
import re
from django.conf import settings as django_settings

def get_app_file_path(app_name, path):
    """Returns path relative to the app root"""
    conf = django_settings.FRONTEND_I18N[app_name]
    app_dir = conf['app_src_dir']
    if path.startswith(app_dir):
        return path[len(app_dir):]
    raise ValueError(f'File {path} is not part of the {app_name}')


def get_compiled_locale_dir(app_name):
    """Returns path where the compiled locale must be"""


def get_compiled_catalog_path(app_name, lang, extension):
    """Returns path to the apps per language catalog
    with the requested file extension"""
    conf = django_settings.FRONTEND_I18N[app_name]
    dir_path = conf['locale_dir']
    return os.path.join(dir_path, lang, 'LC_MESSAGES') + extension

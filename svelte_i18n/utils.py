"""Utility functions"""
import fnmatch
import os
import re
from django.conf import settings as django_settings

def get_app_file_path(app_name, path):
    """Returns path relative to the app root"""
    conf = django_settings.SVELTE_I18N[app_name]
    app_dir = conf['app_src_dir']
    if path.startswith(app_dir):
        return path[len(app_dir):]
    raise ValueError(f'File {path} is not part of the {app_name}')


def get_compiled_locale_dir(app_name):
    """Returns path where the compiled locale must be"""
    conf = django_settings.SVELTE_I18N[app_name]
    return conf['locale_dir'] + '_compiled'


def get_compiled_catalog_path(app_name, lang, route, extension):
    """Returns path to the apps per language per route catalog
    with the requested file extension"""
    dir_path = get_compiled_locale_dir(app_name)
    route_slug = get_route_slug(route)
    return os.path.join(dir_path, lang, 'LC_MESSAGES', route_slug) + extension


def get_route_slug(route):
    """Returns slugified route, replacing forward slashes
    with double underscores"""
    return route.replace('/', '__')


def get_route(app_name, path):
    """Returns route for a given app and path to the file, e.g.:
    /path/to/app/src/pages/[slug]/items/[itemId].svelte -> /:slug/items/:itemId
    """
    routes_dir = django_settings.SVELTE_I18N[app_name]['routes_dir']
    if not path.startswith(routes_dir):
        raise ValueError(f'{path} is not a route in the {app_name}')

    rel_path = path.replace(routes_dir, '', 1).strip(os.path.sep)
    #list(os.path.split(rel_path)) <- does not work for one word paths
    bits = rel_path.split(os.path.sep)
    last_bit = bits.pop()
    route = ''
    for bit in bits:
        param_re = re.compile(r'\[([^\]]+)\]$')
        match = param_re.match(bit)
        if match:
            route += f'/:{match.group(1)}'
        else:
            route += f'/{bit}'

    last_param_re = re.compile(r'\[([^\]]+)\]\.svelte$')
    match = last_param_re.match(last_bit)
    if match:
        return route + f'/:{match.group(1)}'

    if last_bit == 'index.svelte':
        if route == '':
            return '/'
        return route

    return route + '/' + last_bit.replace('.svelte', '')


def is_route(app_name, path):
    """Returns `True` if `path` relative to the
    routes root can be considered as a route,
    otherwise returns `False`"""
    # index path
    if path == '':
        return True

    patterns = django_settings.SVELTE_I18N[app_name]['non_route_file_patterns']
    for pattern in patterns:
        bits = os.path.split(path)
        for bit in bits:
            if fnmatch.fnmatch(bit, pattern):
                return False
    return True

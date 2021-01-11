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

def get_route(app_name, path):
    """Returns route for a given app and path to the file, e.g.:
    /path/to/app/src/pages/[slug]/items/[itemId].svelte -> /:slug/items/:itemId
    """
    routes_dir = django_settings.SVELTE_I18N[app_name]['routes_dir']
    if not path.startswith(routes_dir):
        raise ValueError(f'{path} is not a route in the {app_name}')

    rel_path = path.replace(routes_dir, '', 1).strip(os.path.sep)
    bits = list(os.path.split(rel_path))
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

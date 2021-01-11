"""Routify-specific methods"""
import os
from django.conf import settings as django_settings

def get_special_route_files(app_name, path):
    """Returns paths to the corresponding
    _layout.svelte - may be multiple files per route
    _fallback.svelte - single file
    _reset.svelte - single file
    files, respecting the "routify" convention.
    """
    routes_root = django_settings.SVELTE_I18N[app_name]['routes_dir']
    file_paths = list()
    layout_reset_found = False
    fallback_found = False
    while path.startswith(routes_root):
        if not fallback_found:
            fallback_path = os.path.join(path, '_fallback.svelte')
            if os.path.exists(fallback_path):
                fallback_found = True
                file_paths.append(fallback_path)

        if not layout_reset_found:
            reset_path = os.path.join(path, '_reset.svelte')
            if os.path.exists(reset_path):
                layout_reset_found = True
                file_paths.append(reset_path)
            else:
                layout_path = os.path.join(path, '_layout.svelte')
                if os.path.exists(layout_path):
                    file_paths.append(layout_path)

        path = os.path.dirname(path)

    return file_paths

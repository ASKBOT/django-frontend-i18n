"""Using each translated master catalog and the per-message
comments within, creates the per-route catalogs and compiles them
into the .mo files"""
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand
from svelte_i18n.compiler import Compiler

class Command(BaseCommand):
    """Prepares i18n files for per-route usage
    by the frontend app."""

    def handle(self, *args, **options):
        # for each language in the source locale directory
        for app_name in django_settings.SVELTE_I18N:
            compiler = Compiler(app_name)
            compiler.compile_messages()

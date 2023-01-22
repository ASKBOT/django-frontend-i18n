"""Management command that creates the master locale
for each frontend app"""
import os
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand
from frontend_i18n.extractor import Extractor


class Command(BaseCommand): #pylint: disable=missing-docstring
    help = 'Extracts translation messages from the .frontend and .js files'

    def handle(self, *args, **options):
        """Iterates over the frontend apps and does the job for each"""
        for app_name in django_settings.FRONTEND_I18N:
            extractor = Extractor(app_name)
            extractor.extract_messages()
            extractor.write_pofile()

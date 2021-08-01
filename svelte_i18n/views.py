"""This is a copy of Django i18n JSONCatalog view,
minimally modified to serve the requested
catalog."""
import os.path
from django.conf import settings as django_settings
from django.http import Http404, JsonResponse
from django.views.i18n import JavaScriptCatalog
from django.utils.translation import get_language
from django.utils.translation.trans_real import DjangoTranslation
from babel.messages.mofile import read_mo

class JSONCatalog(JavaScriptCatalog):
    """
    Return the selected language catalog as a JSON object.

    Receive the same parameters as JavaScriptCatalog and return a response
    with a JSON object of the following format:

        {
            "catalog": {
                # Translations catalog
            },
            "formats": {
                # Language formats for date, time, etc.
            },
            "plural": '...'  # Expression for plural forms, or null.
        }
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translation = None

    def get_locale_domain(self, route):
        """Returns the locale domain for the given path.
        Slashes are replaced with double underscores"""
        return route.replace('/', '__')

    def get(self, request, *args, **kwargs):
        """Modified to receieve the catalog selection
        based on the GET request parameters.

        Locale paths are taken from the settings.
        """
        route = request.GET.get('route', '.')
        # If packages are not provided, default to all installed packages, as
        # DjangoTranslation without localedirs harvests them all.
        package = request.GET.get('package', '')

        config = django_settings.SVELTE_I18N

        if package in config:
            locale_path = config[package]['locale_dir']
            locale_path += '_compiled'
            #...get compiled per-route locale path
            locale = get_language()
            domain = self.get_locale_domain(route)
            self.translation = DjangoTranslation(locale, domain=domain, localedirs=[locale_path,])
            context = self.get_context_data(**kwargs)
            #file_path = os.path.join(locale_path, locale, 'LC_MESSAGES', domain + '.mo')
            #file_obj = open(file_path, 'rb')
            #catalog = read_mo(file_obj)
            #for msg in catalog:
            #    if msg.id == '':
            #        continue
            #    import pdb
            #    pdb.set_trace()
            #import pdb
            #pdb.set_trace()
            return JsonResponse(context)

        raise Http404

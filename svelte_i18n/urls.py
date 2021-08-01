from django.conf.urls import url
from svelte_i18n.views import JSONCatalog

urlpatterns = [url(r'^catalog$', JSONCatalog.as_view()),]

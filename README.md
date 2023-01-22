Django i18n localization for frontend apps
==========================================

NOTE: This app is experimental.

Django collects i18s strings from the frontend apps,
serves them via the REST endpoint.

The idea is to help migration of apps using backend templates (Django, Jinja2) to
frontend app using React, Svelte, etc.

Your frontend app should first call the i18n endpoint and retrieve the messages,
then render the translations.

The endpoint returns all messages for the app at once, this may be unacceptable 
for very large applications.

Serving per-route catalogs may be in the future plans.

If you have a SSR frontend - you could in the SSR load all messages on startup
and store them. The frontend would load the landing page and then asynchronously
load all the strings. This approach could work for relatively large apps.

How to use this app
-------------------

1) Install and configure the app as described in the section "Installation" below.
2) Create the global per-app translation catalogs by running `python manage.py frontend_makemessages`.
   The catalogs will be located in the directory specified
   by the `FRONTEND_I18N[<app_name>]['locale_path']` value.
3) Make the translations (refer to the Django documentation).
4) Create catalog by running `python manage.py frontend_compilemessages`


Installation
------------

To the urls.py add:

```
    from frontend_i18n import views

    urlpatterns += (url('^i18n/$', views.JSONCatalog.as_view(), name='frontend-i18n'),)
```

Add to the `settings.py` file:


```
    INSTALLED_APPS = [
        ... <other apps>,
        'frontend_i18n',
    ]


    FRONTEND_I18N = {
        '<frontend_package_name>': {
            'locale_dir': '<path to the app locale dir>', # for each package list path to the locale directory
            'src_dir': '<path to the frontend source code directory>,
            'file_extensions': <array of strings e.g.: ['.js', '.ts', '.svelte']>
        }
    }
```

* `package_name` - any string that identifies the frontend app, e.g. 'myapp_react_frontend'
* `src_dir` - root directory of the app code - to avoid extraction from any files
              outside this directory
* `locale_dir` - file system path to `locale` directory. Can be anywhere on disk,
                 for example at the `/home/smith/myapp/locale`
* `file_extensions` - list of file extensions, where to look for the i18n strings


JSONCatalog view
----------------

This app provides one view `JSONCatalog` which provide the translation strings.

This view returs JSON data, accepts a parameter `package` (required).

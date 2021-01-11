Django i18n localization for Svelte apps
========================================

Contains:

* View `JSONCatalog` serving the translation strings to the frontend
* Management command `svelte_makemessages` extracting the translatable strings.
* Management command `svelte_compilemessages` - creates the per-route catalogs and compiles them into .mo files.


How to internatialize your Svelte app
-------------------------------------

Todo: write this up.


How to use this app
-------------------

1) Install and configure the app as described in the section "Installation" below.
2) Create the global per-app translation catalogs by running `python manage.py svelte_makemessages`.
   The catalogs will be located in the directory specified
   by the `SVELTE_I18N[<app_name>]['locale_path']` value.
3) Make the translations (refer to the Django documentation).
4) Create the per-route catalogs by running `python manage.py svelte_compilemessages`


Installation
------------

```
    pip install django-svelte-i18n
```

To the urls.py add:

```
    from svelte_i18n import views

    urlpatterns += (url('^i18n/$', views.JSONCatalog.as_view(), name='svelte-i18n'),)
```

Add to the `settings.py` file:


```
    INSTALLED_APPS = [
        ... <other apps>,
        'svelte_i18n',
    ]


    SVELTE_I18N = {
        '<package_name>': {
            'locale_dir': '<path to the app locale dir>', # for each package list path to the locale directory
            'app_src_dir': '<path to the app source code directory>,
            'routes_dir': '<path to the root directory of the router>', #next.js, routify style router
            'router_type': 'routify',
            'non_route_patterns': ('_*', '.*'),
            'comment_tags': ('tr:',)
        }
    }
```

* `package_name` - any string that identifies the Svelte app, e.g. 'myapp'
* `app_src_dir` - root directory of the app code - to avoid extraction from any files
              outside this directory
* `locale_dir` - file system path to `locale` directory. Can be anywhere on disk,
                 for example at the `/home/smith/myapp/locale`
* `routes_dir` - root directory of the routes in the routify style
* `router_type` - the only supported value at the moment is 'routify'
* `non_route_patterns` - glob patterns for for the directories and file names
                          that should not be interpreted as routes, so that
                          we don't create unnecessary per-route translation catalogs.


JSONCatalog view
----------------

This app provides one view `JSONCatalog` which provide the translation strings.

This view returs JSON data, accepts two parameters: `route` and `package`.

Parameter `route` is optional. If not provided, the view will return all translation
strings for the given package (i.e. a Svelte app),
the downside in this case may be
that the view will serve a lot of data at once.

Parameter `package` is required if the app is serving strings for more than one package.
Package corresponds to a Svelte app.

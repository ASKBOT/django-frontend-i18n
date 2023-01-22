from distutils.core import setup
import sys

setup(
    name="django-frontend-i18n",
    version="0.0.1",
    description='A Django app for extraction and serving of translation strings for frontend apps (written in React, Vue, Svelte, etc.)',
    author='Evgeny.Fadeev',
    author_email='evgeny.fadeev@gmail.com',
    install_requires=['esprima', 'beautifulsoup'],
    license='GPLv3',
    keywords='translation, django, svelte, i18n',
    url='http://askbot.org',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
    ],
    long_description=open('./README.md').read(),
)

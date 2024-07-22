"""
WSGI config for EasyMeal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyMeal.settings')

# application = get_wsgi_application()

import os

from django.core.wsgi import get_wsgi_application

dbfile = 'EasyMeal.settings.production'

# f = open(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/.git/HEAD", "r")
# if 'ref: refs/heads/testing' in f.read():
# 	dbfile = 'EasyMeal.settings.testing'
# f.close()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', dbfile)

application = get_wsgi_application()

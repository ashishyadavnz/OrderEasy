from .base import *

DEBUG = False

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'ordereasy',
		'USER': 'ordereasy',
		'PASSWORD': 'Jish1405#',
		'HOST': 'ordereasydb.cj4y6c4c0ikd.ap-southeast-2.rds.amazonaws.com',
		'PORT': '5432'
	}
}

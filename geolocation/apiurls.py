from rest_framework.routers import DefaultRouter
from . import api

# Create a router and register our viewsets with it.

router = DefaultRouter()
router.register('geolocation/language', api.LanguageView, basename='language_geo')
router.register('geolocation/continent', api.ContinentView, basename='continent_geo')
router.register('geolocation/country', api.CountryView, basename='country_geo')
router.register('geolocation/state', api.StateView, basename='state_geo')
router.register('geolocation/timezone', api.TimezoneView, basename='timezone_geo')

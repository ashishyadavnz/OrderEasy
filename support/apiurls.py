from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register('support/details', api.SupportViewSet, basename='api_support')
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from geolocation.apiurls import router as router_geo
from blog.apiurls import router as router_blog
from home.apiurls import router as router_home
from restaurant.apiurls import router as router_restaurant
from support.apiurls import router as router_support

router = DefaultRouter()
router.registry.extend(router_home.registry)
router.registry.extend(router_blog.registry)
router.registry.extend(router_geo.registry)
router.registry.extend(router_restaurant.registry)
router.registry.extend(router_support.registry)

urlpatterns = [
	path('v1/', include(router.urls)),
]
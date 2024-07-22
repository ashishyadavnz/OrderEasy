from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register('restaurant/details', api.RestaurantViewSet, basename='restaurant_restaurant')
router.register('restaurant/category', api.CategoryViewSet, basename='restaurant_category')
router.register('restaurant/cuisine', api.CuisineViewSet, basename='restaurant_cuisine')
router.register('restaurant/menu', api.MenuViewSet, basename='restaurant_menu')
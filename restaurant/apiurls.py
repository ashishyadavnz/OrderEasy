from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register('restaurant/details', api.RestaurantViewSet, basename='restaurant_restaurant')
router.register('restaurant/category', api.CategoryViewSet, basename='restaurant_category')
router.register('restaurant/cuisine', api.CuisineViewSet, basename='restaurant_cuisine')
router.register('restaurant/menu', api.MenuViewSet, basename='restaurant_menu')
router.register('restaurant/fooditem', api.FoodItemViewSet, basename='restaurant_fooditem')
router.register('restaurant/voucher', api.VoucherViewSet, basename='restaurant_voucher')
router.register('restaurant/reservation', api.ReservationViewSet, basename='restaurant_reservation')
router.register('restaurant/cart', api.CartViewSet, basename='restaurant_cart')
router.register('restaurant/order', api.OrderViewSet, basename='restaurant_order')
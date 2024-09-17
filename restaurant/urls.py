from django.urls import path
from . import views
app_name = "restaurant"
urlpatterns = [
	path('ajax/<slug:restro>/food-items/<slug:slug>/edit/', views.edit_food_item, name='edit_food_item'),
	path('ajax/<slug:restro>/food-items/<slug:slug>/delete/', views.delete_food_item, name='delete_food_item'),
	path('ajax/<slug:restro>/food-items/create/', views.create_food_item, name='create_food_item'),
    path('ajax/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('ajax/clear_cart/', views.clear_cart, name='clear_cart'),
    path('ajax/update_order_type/', views.update_order_type, name='update_order_type'),
    path('validate-voucher/', views.validate_voucher, name='validate_voucher'),
	path('my-restaurant/<slug:restro>/food-items/', views.food_items, name='food_items'),
	path('my-restaurant/<slug:restro>/orders/', views.orders_items, name='orders_items'),
	path('cuisine/<slug:cuisine_slug>/', views.restaurant, name='restaurants-cuisine'),
	path('<slug:slug>/<str:category>/', views.restaurantCard, name='restaurant-card-category'),
	path('my-restaurant', views.myRestaurant, name='my_restaurant'),
	path('add-restaurant', views.addRestaurant, name='add_restaurant'),
	path('<slug:slug>/', views.restaurantCard, name='restaurant-card'),
	path('', views.restaurant, name='restaurant'),
]
from django.urls import path
from . import views
app_name = "restaurant"
urlpatterns = [
        path('cuisine/<slug:cuisine_slug>/', views.restaurant, name='restaurants-cuisine'),
        path('<slug:slug>/<str:category>/', views.restaurantCard, name='restaurant-card-category'),
        path('<slug:slug>/', views.restaurantCard, name='restaurant-card'),
        path('my-restaurant', views.myRestaurant, name='my_restaurant'),
        path('add-restaurant', views.addRestaurant, name='add_restaurant'),
        path('', views.restaurant, name='restaurant'),
]
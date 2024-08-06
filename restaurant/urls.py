from django.urls import path
from . import views
app_name = "restaurant"
urlpatterns = [
        path('', views.restaurant, name='restaurant'),
        path('restaurant-card/', views.restaurantCard, name='restaurant-card'),

]
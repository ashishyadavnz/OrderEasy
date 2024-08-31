from django.urls import path
from . import views
app_name = "restaurant"
urlpatterns = [
        path('', views.restaurant, name='restaurant'),
        path('<slug:slug>/', views.restaurantCard, name='restaurant-card'),
        path('<slug:slug>/<str:category>/', views.restaurantCard, name='restaurant-card-category'),


]
from django.urls import path
from . import views
app_name="home"
urlpatterns = [
        path('', views.home, name='home-page'),
        # path('restaurant-card/', views.restaurantCard, name='restaurant-card'),

]
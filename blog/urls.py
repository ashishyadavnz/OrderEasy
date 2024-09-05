from django.urls import path
from . import views
app_name = "blog"
urlpatterns = [
        path('<slug:slug>/add_comment/', views.add_comment, name='add_comment'),
        path('service/', views.services, name='service'),
        path('subscribe/', views.subscribe, name='subscribe'),
        path('<slug:slug>/', views.blogDetails, name='blog_detail'),
        path('', views.blog, name='blog_page'),
]
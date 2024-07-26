from django.urls import path
from . import views
app_name="home"
urlpatterns = [
        path('', views.home, name='home-page'),
        path('about/',views.about,name='about-page'),
        path('faq/',views.faq,name='faq'),
        path('faq/message/', views.faq_message, name='faq_message'),


]
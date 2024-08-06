from django.urls import path
from . import views
app_name="home"
urlpatterns = [
        path('', views.home, name='home-page'),
        path('about/',views.about,name='about-page'),
        path('faq/',views.faq,name='faq'),
        path('faq/message/', views.faq_message, name='faq_message'),
        path('pricing-table/',views.pricingTable,name='pricing-table'),
        path('contact/',views.contact,name='contact'),
        path('checkout/',views.checkout,name='checkout'),
        path('become-partner/',views.becomePartner,name='become-partner'),
        path('page-not-found/', views.notfound,name='page-not-found')

]
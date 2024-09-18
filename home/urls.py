from django.urls import path
from . import views
app_name="home"
urlpatterns = [
        path('<slug:slug>/submit-feedback/', views.submit_feedback, name='submit_feedback'),
        path('ajax/fcm-token/',views.fcm_token,name='fcm_token'),
        path('ajax/update_dtype/',views.update_dtype,name='update_dtype'),
        path('faq/message/', views.faq_message, name='faq_message'),
        path('about/',views.about,name='about-page'),
        path('faq/',views.faq,name='faq'),
        path('pricing-table/',views.pricingTable,name='pricing-table'),
        path('contact/',views.contact,name='contact'),
        path('checkout/',views.checkout,name='checkout'),
        path('become-partner/',views.becomePartner,name='become-partner'),
        path('page-not-found/', views.notfound,name='page-not-found'),
        path('myorder/',views.myorder,name='myorder'),
        path('register/',views.register,name='register'),
        path('login/', views.login, name='login'),
        path("notify/", views.index, name="index"),
        path('logout/', views.user_logout, name='logout'),
        path('forgot-password/', views.forgot_password, name='forgot_password'),
        path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
        path('reset-password/<int:user_id>/', views.reset_password, name='reset_password'),
        path('<slug:slug>/submit-feedback/', views.submit_feedback, name='submit_feedback'),
        path('profile/', views.profile, name='profile'),
        path('change-password/', views.change_password, name='change_password'),
        path('<str:slug>/', views.page_detail, name='page_detail'),
        path('', views.home, name='home-page'),   
]
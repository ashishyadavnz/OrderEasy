from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.utils import timezone
from restaurant.models import *
from blog.models import *
# Create your views here.

def home(request):
    restaurants = Restaurant.objects.all()
    cat = Category.objects.all()
    posts = Post.objects.all()
    testimonials = Testimonial.objects.all()

    return render(request, 'ui/indexThem.html',{'restaurants':restaurants,'cat':cat,'posts':posts,'testimonials':testimonials})


def about(request):
    testimonials = Testimonial.objects.all()
    
    return render(request, 'ui/about.html',{'testimonials':testimonials})


def pricingTable(request):
    return render(request, 'ui/pricing-table.html')


def contact(request):
    return render(request, 'ui/contact.html')


def becomePartner(request):
    return render(request, 'ui/become-partner.html')

def checkout(request):
    return render(request, 'ui/checkout.html')

def notfound(request):
    return render(request, 'ui/404.html')

def faq(request):
    delivery_faqs = Faqs.objects.filter(category='delivery')
    technical_faqs = Faqs.objects.filter(category='technical')
    restaurant_faqs = Faqs.objects.filter(category='restaurants')
    return render(request, 'ui/faq.html', {
        'delivery_faqs': delivery_faqs,
        'technical_faqs': technical_faqs,
        'restaurant_faqs': restaurant_faqs
    })

def faq_message(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_content = request.POST.get('message')

        if not name or not email or not message_content:
            messages.error(request, 'All fields are required.')
            return redirect('home:faq')

        FaqMessage.objects.create(
            name=name,
            email=email,
            message=message_content
        )

        messages.success(request, 'Your message has been submitted successfully.')
        return redirect('home:faq')

    return redirect('home:faq')
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
# Create your views here.

def restaurant(request):
    restaurants = Restaurant.objects.all()
    cat = Category.objects.all()
    return render(request, 'ui/restaurant.html', {'restaurants': restaurants,'cat':cat})
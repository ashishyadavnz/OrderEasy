from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.utils import timezone
# Create your views here.

def restaurant(request):
    restaurants = Restaurant.objects.all()
    cat = Category.objects.all()
    return render(request, 'ui/restaurant.html', {'restaurants': restaurants,'cat':cat})


def restaurantCard(request):
    restaurants = Restaurant.objects.all()
    cat = Category.objects.all()
    menus = Menu.objects.all()
    print(menus)
    breakfast_items = menus.filter(cuisine__category__title__contains="Breakfast")
    lunch_items = menus.filter(cuisine__category__title__contains="Lunch")
    dinner_items = menus.filter(cuisine__category__title__contains="Dinner")
    
    context = {
        'restaurants': restaurants,
        'cat': cat,
        'breakfast_items': breakfast_items,
        'lunch_items': lunch_items,
        'dinner_items': dinner_items
    }
    print(context, "yo!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    return render(request, 'ui/restaurants-card.html', context)
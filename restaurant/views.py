from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.utils import timezone
# Create your views here.

def restaurant(request):
    restaurants = Restaurant.objects.all()
    cat = Category.objects.all()
    return render(request, 'ui/restaurant.html', {'restaurants': restaurants,'cat':cat})


# def restaurantCard(request,  slug=None):
#     restaurant = Restaurant.objects.get(slug=slug)
#     cat = Category.objects.all()
#     menus = Menu.objects.all()
#     if not slug and restaurant.exists():
#         first_restaurant = restaurant.first()
#         return redirect('restaurant:restaurant-card', slug=first_restaurant.slug)

#     breakfast_items = menus.filter(cuisine__category__title__contains="Breakfast")
#     lunch_items = menus.filter(cuisine__category__title__contains="Lunch")
#     dinner_items = menus.filter(cuisine__category__title__contains="Dinner")

    
#     context = {
#         'restaurant': restaurant,
#         'cat': cat,
#         'breakfast_items': breakfast_items,
#         'lunch_items': lunch_items,
#         'dinner_items': dinner_items
#     }
#     return render(request, 'ui/restaurants-card.html', context)

def restaurantCard(request, slug=None):
    try:
        restaurant = Restaurant.objects.get(slug=slug)
    except Restaurant.DoesNotExist:
        return redirect('restaurant:restaurant-card', slug=Restaurant.objects.first().slug)

    cat = Category.objects.all()
    menus = Menu.objects.select_related('cuisine').filter(cuisine__category__in=cat)

    # Prepare the categories and their related cuisines
    category_cuisines = {}
    for category in cat:
        category_cuisines[category.title] = Menu.objects.filter(cuisine__category=category).select_related('cuisine')

    context = {
        'restaurant': restaurant,
        'cat': cat,
        'category_cuisines': category_cuisines
    }
    return render(request, 'ui/restaurants-card.html', context)
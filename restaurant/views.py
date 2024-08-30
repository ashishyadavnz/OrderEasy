from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import *
from django.utils import timezone
from django.db.models import Min
from datetime import datetime, timedelta
from django.db.models import F
from django.db.models.functions import ACos, Cos, Radians, Sin

# Create your views here.

def restaurant(request):
    user_lat = float(request.GET.get('latitude', 0))
    user_lon = float(request.GET.get('longitude', 0))

    # Calculate the distance using Haversine formula
    restaurants = Restaurant.objects.annotate(
        distance=ACos(
            Sin(Radians(user_lat)) * Sin(Radians(F('latitude'))) +
            Cos(Radians(user_lat)) * Cos(Radians(F('latitude'))) * Cos(Radians(F('longitude')) - Radians(user_lon))
        ) * 6371  # Earth radius in kilometers
    ).order_by('distance')

    cat = Category.objects.all()
    current_time = timezone.now().time()  
    for restaurant in restaurants:
        restaurant.lowest_price = Menu.objects.filter(restaurant=restaurant).aggregate(Min('price'))['price__min']
    return render(request, 'ui/restaurant.html', {'restaurants': restaurants, 'cat': cat, 'current_time': current_time})
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

# def restaurantCard(request, slug=None):
#     try:
#         restaurant = Restaurant.objects.get(slug=slug)
#     except Restaurant.DoesNotExist:
#         return redirect('restaurant:restaurant-card', slug=Restaurant.objects.first().slug)

#     cat = Category.objects.all()
#     menus = Menu.objects.select_related('cuisine').filter(cuisine__category__in=cat)
#     breakfast_items = menus.filter(cuisine__category__title__contains="Breakfast")
#     lunch_items = menus.filter(cuisine__category__title__contains="Lunch")
#     dinner_items = menus.filter(cuisine__category__title__contains="Dinner")
#     category_cuisines = {}
#     for category in cat:
#         category_cuisines[category.title] = Menu.objects.filter(cuisine__category=category).select_related('cuisine')

#     context = {
#         'restaurant': restaurant,
#         'cat': cat,
#         'category_cuisines': category_cuisines,
#         'breakfast_items': breakfast_items,
#         'lunch_items':lunch_items,
#         'dinner_items':dinner_items
#         }
#     return render(request, 'ui/restaurants-card.html', context)
def generate_time_slots(start_time, end_time, interval=60):
    slots = []
    current_time = start_time
    while current_time <= end_time:
        slots.append(current_time.strftime('%I:%M %p'))
        current_time += timedelta(minutes=interval)
    return slots

def restaurantCard(request, slug=None, category_title=None):
    try:
        restaurant = Restaurant.objects.get(slug=slug)
    except Restaurant.DoesNotExist:
        return redirect('restaurant:restaurant-card', slug=Restaurant.objects.first().slug)
    cat = Category.objects.all()
    if category_title:
        selected_category = get_object_or_404(Category, title=category_title)
        food_items = FoodItem.objects.filter(category=selected_category, restaurant=restaurant)
        cuisines = food_items.values_list('cuisine', flat=True)
    else:
        selected_category = None
        food_items = FoodItem.objects.filter(restaurant=restaurant)
        cuisines = food_items.values_list('cuisine', flat=True)
    menus = Menu.objects.filter(cuisine__in=cuisines).select_related('cuisine')
    category_cuisines = {}
    for category in cat:
        category_food_items = FoodItem.objects.filter(category=category, restaurant=restaurant)
        category_cuisine_ids = category_food_items.values_list('cuisine', flat=True)
        category_cuisines[category.title] = Menu.objects.filter(cuisine__in=category_cuisine_ids).select_related('cuisine')

    start_time = datetime.combine(datetime.today(), restaurant.start) if restaurant.start else None
    end_time = datetime.combine(datetime.today(), restaurant.end) if restaurant.end else None
    time_slots = generate_time_slots(start_time, end_time) if start_time and end_time else []

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        member = request.POST.get('member')
        user = request.user 

        try:
            time_obj = datetime.strptime(time, '%I:%M %p')
            time = time_obj.strftime('%H:%M:%S') 
        except ValueError:
            messages.error(request, "Invalid time format.")
            return redirect('restaurant:restaurant-card', slug=slug)

        reservation = Reservation(
            name=name,
            email=email,
            phone=phone,
            date=date,
            time=time,
            member=member,
            users=user,
        )
        reservation.save()
        messages.success(request, "Your table reservation has been successfully made!")
        return redirect('restaurant:restaurant-card', slug=slug)

    context = {
        'restaurant': restaurant,
        'cat': cat,
        'category_cuisines': category_cuisines,
        'menus': menus,
        'selected_category': category_title,
        'time_slots': time_slots,
    }
    return render(request, 'ui/restaurants-card.html', context)

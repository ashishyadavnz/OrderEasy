from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.utils import timezone
from django.db.models import Min
from datetime import datetime, timedelta


# Create your views here.

def restaurant(request):
    restaurants = Restaurant.objects.all()
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
def generate_time_slots(start_time, end_time):
    slots = []
    current_time = start_time
    while current_time <= end_time:
        slots.append(current_time.strftime('%I:%M %p'))
        current_time += timedelta(hours=1)
    return slots

def restaurantCard(request, slug=None, category_title=None):
    try:
        restaurant = Restaurant.objects.get(slug=slug)
    except Restaurant.DoesNotExist:
        return redirect('restaurant:restaurant-card', slug=Restaurant.objects.first().slug)

    cat = Category.objects.all()
    menus = Menu.objects.select_related('cuisine').filter(cuisine__category__in=cat)
    breakfast_items = menus.filter(cuisine__category__title__contains="Breakfast")
    lunch_items = menus.filter(cuisine__category__title__contains="Lunch")
    dinner_items = menus.filter(cuisine__category__title__contains="Dinner") 
    if category_title:
        selected_category = Category.objects.get(title=category_title)
        menus = Menu.objects.select_related('cuisine').filter(cuisine__category=selected_category)
    else:
        menus = Menu.objects.select_related('cuisine').all()

    category_cuisines = {}
    for category in cat:
        category_cuisines[category.title] = Menu.objects.filter(cuisine__category=category).select_related('cuisine')
    
    start_time = datetime.combine(datetime.today(), restaurant.start)
    end_time = datetime.combine(datetime.today(), restaurant.end)
    time_slots = generate_time_slots(start_time, end_time)


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
        'breakfast_items': breakfast_items,
        'lunch_items': lunch_items,
        'dinner_items': dinner_items,
        'time_slots' :time_slots
    }
    return render(request, 'ui/restaurants-card.html', context)
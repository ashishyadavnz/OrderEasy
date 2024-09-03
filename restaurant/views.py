from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect,HttpResponse
from django.contrib import messages
from .models import *
from django.utils import timezone
from django.db.models import Min
from datetime import datetime, timedelta
from django.db.models import F
from django.db.models.functions import ACos, Cos, Radians, Sin
from home.forms import *

# Create your views here.

def restaurant(request, cuisine_slug=None):
    restaurants = Restaurant.objects.filter(status='Active')
    cat = Category.objects.all()
    if cuisine_slug:
        cuisine = get_object_or_404(Cuisine, slug=cuisine_slug)
        fooditems = FoodItem.objects.filter(cuisine=cuisine)
        restaurants = restaurants.filter(fooditems_restaurant__in=fooditems).distinct()
    return render(request, 'ui/restaurant.html', {'restaurants': restaurants,'cat':cat})
  
def generate_time_slots(start_time, end_time, interval=60):
    slots = []
    current_time = start_time
    while current_time <= end_time:
        slots.append(current_time.strftime('%I:%M %p'))
        current_time += timedelta(minutes=interval)
    return slots

def restaurantCard(request, slug, category=None):
    restaurant = Restaurant.objects.get(slug=slug)
    categories = Category.objects.filter(status='Active')
    fooditems = FoodItem.objects.filter(restaurant=restaurant, status="Active")
    if category:
        fooditems = fooditems.filter(category__slug=category)
    start_time = datetime.datetime.combine(datetime.datetime.today(), restaurant.start) if restaurant.start else None
    end_time = datetime.datetime.combine(datetime.datetime.today(), restaurant.end) if restaurant.end else None
    time_slots = generate_time_slots(start_time, end_time) if start_time and end_time else []
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        print(form.errors)
        if form.is_valid():
            time = request.POST['time']
            cd = form.save(commit=False)
            if request.user.is_authenticated:
                user = request.user
            else:
                user = User.objects.filter(username=cd.phone).last()
                if not user:
                    user = User.objects.create_user(username=cd.phone, password=str(cd.name)[:3]+"@123", email=cd.email, mobile=cd.phone)
                    user.guest = True
                    user.save()
            try:
                time_obj = datetime.datetime.strptime(time, '%I:%M %p')
                time = time_obj.strftime('%H:%M:%S') 
            except ValueError:
                messages.error(request, "Invalid time format.")
                return redirect('restaurant:restaurant-card', slug=slug)
            cd.user = user
            cd.time = time
            cd.save()
            messages.success(request, "Your table reservation has been successfully made!")
            return redirect('restaurant:restaurant-card', slug=slug)
        else:
            messages.error(request, "Date is required.")

    context = {
        'restaurant': restaurant,
        'category': categories,
        'fooditems': fooditems,
        'time_slots': time_slots
    }
    return render(request, 'ui/restaurants-card.html', context)
  
def myRestaurant(request):
    user = None
    if request.user.is_authenticated:
        user = request.user
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            cd = form.save(commit=False)
            cd.owner = request.user
            cd.save()
        
    else:
        form = RestaurantForm(user=request.user)
    restaurants = Restaurant.objects.filter(status='Active',owner=user)
    if restaurants.count()<1:
        return redirect('restaurant:add_restaurant')
    cat = Category.objects.all()
    return render(request, 'ui/my-restaurant.html', {'restaurants': restaurants,'cat':cat,'form': form})

def addRestaurant(request):
    if request.user.is_authenticated and request.user.role == 'Owner' :
        if request.method == 'POST':
            form = RestaurantForm(request.POST, request.FILES)
            print(form.errors)
            if form.is_valid():
                cd = form.save(commit=False)
                cd.owner = request.user
                cd.save()
                messages.success(request,f'{cd.title} added successfully')
                return redirect('restaurant:my_restaurant')
            else:
                messages.warning(request,'error occurs while adding restaurant')
                return redirect('restaurant:add_restaurant')
        else:
            form = RestaurantForm(user=request.user)
        return render(request, 'ui/add-restaurant.html', {'form': form})
    else:
        return HttpResponse('you are not authorized to access this page')
    


def food_items(request ,restro):
    foodItem = FoodItem.objects.filter(restaurant__slug = restro,status='Active')
    categories = Category.objects.filter(status='Active')
    cuisines = Cuisine.objects.filter(status='Active')
    return render(request, 'ui/my-menu.html', {'food_items': foodItem,'restro':restro,'categories':categories,'cuisines':cuisines})

def orders_items(request ,restro):
    orderItem = Order.objects.filter(restaurant__slug = restro,status='Active')
    return render(request, 'ui/orders.html', {'orderItem': orderItem,'restro':restro})

def create_food_item(request ,restro):
    if request.method == 'POST':
        restroObj = Restaurant.objects.get(slug = restro)
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.save(commit=False)
            cd.restaurant = restroObj
            cd.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

def edit_food_item(request,restro, slug):
    food_item = get_object_or_404(FoodItem, slug=slug,restaurant__slug = restro)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food_item)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'errors': 'Invalid request'})

def delete_food_item(request,restro, slug):
    food_item = get_object_or_404(FoodItem, slug=slug,restaurant__slug = restro)
    food_item.status = 'Delete'
    food_item.save()
    return JsonResponse({'status': 'success'})
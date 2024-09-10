from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect,HttpResponse
from django.contrib import messages
from django.utils.dateparse import parse_date
from .models import *
from django.utils import timezone
from django.db.models import Min
from datetime import datetime, timedelta
from django.db.models import F
from django.db.models.functions import ACos, Cos, Radians, Sin
from home.forms import *
import pytz

# Create your views here.

def restaurant(request, cuisine_slug=None):
    if request.user.is_authenticated and request.user.role == 'Owner':
        return redirect('restaurant:my_restaurant')
    restaurants = Restaurant.objects.filter(status='Active')
    cat = Category.objects.all()
    user_address = request.session.get('user_address',None)
    if cuisine_slug:
        cuisine = get_object_or_404(Cuisine, slug=cuisine_slug)
        fooditems = FoodItem.objects.filter(cuisine=cuisine)
        restaurants = restaurants.filter(fooditems_restaurant__in=fooditems).distinct()
    if request.method == 'POST':
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if address and latitude and longitude:
            request.session['user_address'] = {'add':address,
                                            'lat':latitude,
                                            'long':longitude}
            return redirect('restaurant:restaurant')
    if user_address:
        R = 6371
        user_lat = float(user_address['lat'])
        user_long = float(user_address['long'])
        restaurants = restaurants.annotate(
            distance=R * ACos(
                Cos(Radians(user_lat)) * Cos(Radians(F('latitude'))) *
                Cos(Radians(F('longitude')) - Radians(user_long)) +
                Sin(Radians(user_lat)) * Sin(Radians(F('latitude')))
            )
        ).filter(distance__lte=15).order_by('distance').distinct()
    return render(request, 'ui/restaurant.html', {'restaurants': restaurants,'cat':cat,'user_address':user_address})
  
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
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    orderItem = Order.objects.filter(restaurant__slug=restro, status='Active')
    if start_date and end_date:
        start_date_parsed = parse_date(start_date)
        end_date_parsed = parse_date(end_date)
        if start_date_parsed and end_date_parsed:
            orderItem = orderItem.filter(timestamp__date__gte=start_date_parsed, timestamp__date__lte=end_date_parsed ,status='Active')
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


def validate_voucher(request):
    if request.method == 'POST':
        voucher_code = request.POST.get('voucher_code')
        total_amount = float(request.POST.get('total_amount'))

        if 'applied_vouchers' in request.session and voucher_code in request.session['applied_vouchers']:
            return JsonResponse({'status': 'error', 'message': 'This voucher has already been used.'})


        try:
            voucher = Voucher.objects.get(name=voucher_code)
            auckland_tz = pytz.timezone('Pacific/Auckland')
            if voucher.validity < timezone.now().astimezone(auckland_tz):
                return JsonResponse({'status': 'error', 'message': 'Voucher has expired.'})

            if total_amount < voucher.payment:
                return JsonResponse({'status': 'error', 'message': f'Order total must be at least ${voucher.payment} to apply this voucher.'})
             
            if 'applied_vouchers' not in request.session:
                request.session['applied_vouchers'] = []
            request.session['applied_vouchers'].append(voucher_code)
            request.session.modified = True

            return JsonResponse({'status': 'success', 'discount': voucher.discount, 'id':voucher.id})
        
        except Voucher.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid voucher code.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
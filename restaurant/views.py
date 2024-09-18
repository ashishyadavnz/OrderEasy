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
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict
from math import radians, sin, cos, sqrt, atan2

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
    flag = request.session.get("display_checkout", False)
    orderid = request.session.get("orderid", None)
    order = None
    if orderid:
        order = Order.objects.get(id=orderid)
    if flag:
        del request.session['display_checkout']
        del request.session['orderid']
    if request.method == 'POST':
        address = request.POST.get('address')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        cart = request.session.get('cart', [])
        if location and latitude and longitude:
            request.session['user_address'] = {'add': location, 'display': address, 'lat': latitude, 'long': longitude}
            for item in cart:
                res = Restaurant.objects.get(id=item['restaurant'])
                try:
                    item['rdistance'] = matrixdistance(useraddress=address, restaddress=res.address)
                except:
                    item['rdistance'] = haversine(lat1=res.latitude, lon1=res.longitude, lat2=float(latitude), lon2=float(longitude))
            request.session['cart'] = cart
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
        ).order_by('distance').distinct()
    return render(request, 'ui/restaurant.html', {'restaurants': restaurants,'cat':cat,'user_address':user_address, "flag":flag, 'order':order})

# def calculate_distance(lat1, lon1, lat2, lon2):

#     R = 6371  
#     lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))
#     distance = R * c
#     return distance

def generate_time_slots(start_time, end_time, interval=60):
    slots = []
    current_time = start_time
    while current_time <= end_time:
        slots.append(current_time.strftime('%I:%M %p'))
        current_time += timedelta(minutes=interval)
    return slots

def restaurantCard(request, slug, category=None):
    # request.session.clear()
    restaurant = Restaurant.objects.get(slug=slug)
    categories = Category.objects.filter(status='Active')
    fooditems = FoodItem.objects.filter(restaurant=restaurant, status="Active")
    user_address = request.session.get('user_address',None)
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
       
            owner_email = restaurant.email
            owner_subject = "New Table Reservation at Your Restaurant"
            owner_message = f"Dear {restaurant.owner.username},\n\nYou have received a new table reservation.\n\nReservation Details:\nName: {cd.name}\nPhone: {cd.phone}\nEmail: {cd.email}\nDate: {cd.date}\nTime: {cd.time}\nNumber of People: {cd.member}\n\nThank you!"
            custom_emailmessage(owner_subject, owner_message, owner_email)

            # Email to the customer
            customer_email = cd.email
            customer_subject = "Table Reservation Confirmation"
            customer_message = f"Dear {cd.name},\n\nThank you for your reservation at {restaurant.title}.\n\nReservation Details:\nDate: {cd.date}\nTime: {cd.time}\nNumber of People: {cd.member}\n\nWe look forward to hosting you!\n\nBest regards,\n{restaurant.title} Team"
            custom_emailmessage(customer_subject, customer_message, customer_email)

            messages.success(request, "Your table reservation has been successfully made!")
            return redirect('restaurant:restaurant-card', slug=slug)
        else:
            messages.error(request, "Date is required.")

    context = {
        'restaurant': restaurant,
        'category': categories,
        'fooditems': fooditems,
        'time_slots': time_slots,
        'user_address':user_address
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
        code = request.POST.get('voucher_code')
        total = float(request.POST.get('total_amount'))
        voucher = Voucher.objects.filter(name=code).last()
        if voucher:
            auckland_tz = pytz.timezone('Pacific/Auckland')
            if voucher.validity < timezone.now().astimezone(auckland_tz):
                return JsonResponse({'status': 'error', 'message': 'Voucher has expired.'})
            if total < voucher.payment:
                return JsonResponse({'status': 'error', 'message': f'Order total must be at least ${voucher.payment} to apply this voucher.'})
            total = total - voucher.discount
            request.session['discount'] = {"total":total, "name":voucher.name, "discount":voucher.discount, 'id':voucher.id}
            return JsonResponse({'status': 'success', 'discount': voucher.discount, 'id':voucher.id, 'total': total})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid voucher code.'})

@csrf_exempt
def add_to_cart(request):
    # request.session.clear()
    if request.method == 'POST':
        item_id = request.POST['item_id']
        restaurant_id = request.POST['restaurant_id']
        order_type = request.POST['order_type']
        rdistance = request.POST['rdistance']
        cart = request.session.get('cart', [])
        discount = request.session.get('discount', None)
        voucher = None
        if discount:
            voucher = discount
        if len(cart) > 0:
            if restaurant_id != cart[0]['restaurant']:
                return JsonResponse({'status': 'rchange', 'message': 'Restaurant changed.'})
            for i in cart:
                i['rdistance'] = rdistance
            items = next((i for i in cart if i['item_id'] == item_id), None)
            if items:
                items['quantity'] += 1
            else:
                item_obj = FoodItem.objects.get(id=item_id)
                cart.append({
                    'item_id': item_id,
                    'title': item_obj.title,
                    'price': item_obj.price,
                    'image': item_obj.image.url if item_obj.image else None,
                    'quantity': 1,
                    'restaurant': restaurant_id, 
                    'order_type': order_type,
                    'voucher': voucher,
                    'rdistance': rdistance,
                })
        else:
            item_obj = FoodItem.objects.get(id=item_id)
            cart.append({
                'item_id': item_id,
                'title': item_obj.title,
                'price': item_obj.price,
                'image': item_obj.image.url if item_obj.image else None,
                'quantity': 1,
                'restaurant': restaurant_id, 
                'order_type': order_type,
                'voucher': voucher,
                'rdistance': rdistance,
            })
        request.session['cart'] = cart
        return JsonResponse({'status': 'success', 'cart': cart, 'type':order_type, 'distance':rdistance, 'voucher':voucher})
    if request.method == 'GET':
        cart = request.session.get('cart', [])
        discount = request.session.get('discount', None)
        voucher = None
        if discount:
            voucher = discount
        return JsonResponse({'status': 'success', 'cart': cart, 'type':cart[0]['order_type'] if len(cart)>0 else 'Delivery', 'distance':cart[0]['rdistance'] if len(cart)>0 else 0, 'voucher':voucher})
    if request.method == 'PATCH':
        discount = request.session.get('discount', None)
        voucher = None
        if discount:
            voucher = discount
        patch_data = QueryDict(request.body)
        item_id = patch_data.get('item_id')
        cart = request.session.get('cart', [])
        rdistance = patch_data.get('rdistance')
        for i in cart:
            i['rdistance'] = rdistance
        patch_type = patch_data.get('type')
        items = next((i for i in cart if i['item_id'] == item_id), None)
        if items:
            if patch_type == 'decrease':
                items['quantity'] -= 1
                if items['quantity'] <= 0:
                    cart = [i for i in cart if i['item_id'] != item_id]
            else:
                items['quantity'] += 1
        request.session['cart'] = cart
        return JsonResponse({'status': 'success', 'cart': cart, 'type':cart[0]['order_type'] if len(cart)>0 else 'Delivery', 'distance':cart[0]['rdistance'] if len(cart)>0 else 0, 'voucher':voucher})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def clear_cart(request):
    if request.method == 'POST':
        # Clear the session's cart
        cart = request.session.get('cart', [])
        discount = request.session.get('discount', None)
        order = request.session.get('order', None)
        cart_items = request.session.get('cart_items', [])
        order_type = request.session.get('order_type', None)
        print(cart_items, "pppp")
        if len(cart) > 0:
            del request.session['cart']
        if discount:
            del request.session['discount']
        if order:
            del request.session['order']
        if len(cart_items) > 0:
            del request.session['cart_items']
        if order_type:
            del request.session['order_type']
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def update_order_type(request):
    if request.method == 'POST':
        discount = request.session.get('discount', None)
        voucher = None
        if discount:
            voucher = discount
        order_type = request.POST.get('order_type')
        resid = request.POST['resid']
        cart = request.session.get('cart', [])
        if cart:
            if resid != cart[0]['restaurant']:
                return JsonResponse({'status': 'rchange', 'message': 'Restaurant changed.'})
            for item in cart:
                item['order_type'] = order_type
        request.session['cart'] = cart
        return JsonResponse({'status': 'success', 'cart': cart, 'type':cart[0]['order_type'] if len(cart)>0 else 'Delivery', 'distance':cart[0]['rdistance'] if len(cart)>0 else 0, 'voucher':voucher})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

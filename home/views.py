from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import *
from django.utils import timezone
from restaurant.models import *
from blog.models import Post
from django.contrib.auth import authenticate,logout, login as auth_login


def home(request):
    restaurants = Restaurant.objects.all()
    categories = Category.objects.all()
    posts = Post.objects.all()
    testimonials = Testimonial.objects.all()
    # cuisines = Cuisine.objects.filter(menu_cuisine__restaurant__in=restaurants).distinct()
    cuisines = Cuisine.objects.filter(fooditems_cuisine__isnull=False).distinct()

    return render(request, 'ui/indexThem.html', {
        'restaurants': restaurants,
        'categories': categories,
        'posts': posts,
        'testimonials': testimonials,
        'cuisines': cuisines 
    })

def restaurants_by_cuisine(request, cuisine_slug):
    cuisine = get_object_or_404(Cuisine, slug=cuisine_slug)
    food_items = FoodItem.objects.filter(cuisine=cuisine)
    restaurants = Restaurant.objects.filter(fooditems_restaurant__in=food_items).distinct()
    cat = Category.objects.all()
    return render(request, 'ui/restaurant.html', {
        'restaurants': restaurants,
        'cuisine': cuisine,
        'cat': cat,
    })

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
    if request.method == 'POST':
        if 'cart_checkout' in request.POST:
            cart_data = request.POST.get('cart_data')
            order_type = request.POST['order_type']
            restaurent = request.POST['restaurent_id']
            voucher_id = request.POST.get('voucher_id',None)
            charge = request.POST['charge']
            try:
                cart_items = json.loads(cart_data)
            except json.JSONDecodeError:
                cart_items = []
            rests = Restaurant.objects.get(id=restaurent)
            voucher = None
            if voucher_id:
                voucher = Voucher.objects.filter(id=voucher_id).last()
            order = Order(
                restaurant=rests,
                voucher=voucher,
                otype = order_type,
                charge = float(charge),
            )
            if request.user.is_authenticated:
                order.fname = request.user.first_name
                order.lname = request.user.last_name
                order.email = request.user.email
                order.phone = request.user.mobile
                order.user = request.user
            order.save()
            request.session['order'] = order.id
            request.session['cart_items'] = cart_items
            request.session['order_type'] = cart_items
            for item in cart_items:
                try:
                    food_item = FoodItem.objects.get(id=item['id'])
                    cart_item = Cart(
                        order=order,
                        fooditem=food_item,
                        quantity=item['quantity'],
                        total=item['quantity'] * item['price']
                    )
                    cart_item.save()
                except FoodItem.DoesNotExist:
                    continue
            return redirect('home:checkout')
        if 'place_order' in request.POST:
            odrid = request.POST['oid']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            phone = request.POST['phone']
            otype = request.POST['otype']
            address = request.POST['address']
            instructions = request.POST.get('instructions')
            odr = Order.objects.get(id=odrid)
            if not odr.user:
                user = User.objects.filter(username=phone).last()
                if not user:
                    user = User.objects.create_user(username=phone, password=str(first_name)[:3]+"@123", email=email, mobile=int(phone))
                    user.guest = True
                    user.save()
                odr.user = user
            odr.fname = first_name
            odr.lname = last_name
            odr.email = email
            odr.phone = phone
            odr.otype = otype
            odr.address = address
            odr.instruction = instructions
            odr.save()
            devices = FCMDevice.objects.filter(user=odr.user)
            title = f'Order Created'
            body = f'{first_name} {last_name} has generated order in your restaurent. Order id is {odr.orderid}.'
            devices.send_message(
                Message(notification=Notification(title=title, body=body, image=settings.EASYLOGO),data={})
            )
            del request.session['order']
            del request.session['cart_items']
            messages.success(request, "Your order is placed successfully.")
            return redirect('restaurant:restaurant')
    oid = request.session.get('order', None)
    order = Order.objects.filter(id=oid).last()
    cart_items = request.session.get('cart_items', []) 
    total = 0
    for idx, item in enumerate(cart_items):
        tl = item['price'] * item['quantity']
        cart_items[idx]['total'] = tl
        total += tl
    
    context = {
        'cart': cart_items,
        'order': order,
        'total': total
    }
    return render(request, 'ui/checkout.html', context)

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


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        mobile = request.POST['mobile']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        profile_picture = request.FILES.get('profile_picture')
        guest = request.POST.get('guest') == 'on'

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('home:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('home:register')

        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already exists")
            return redirect('home:register')

        # Create the user

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            mobile=mobile,
            password=password,
            image=profile_picture,
            guest=guest    
        )
        if user:
            auth_login(request,user)

        messages.success(request, "Account created successfully")
        return redirect('restaurant:restaurant')

    return render(request, 'ui/register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful")
            return redirect('restaurant:restaurant')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('home:login')

    return render(request, 'ui/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('home:home-page')

def place_order(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        time = request.POST['time']
        address = request.POST['address']
        instruction = request.POST.get('instruction', '')
        otype = request.POST.get('otype', 'Delivery')  # 'Delivery' or 'Pickup'
        cart_items = request.POST.getlist('cart_items')  # This should contain the cart items

        # Calculate the total and delivery charge
        total = sum([item.price * item.quantity for item in cart_items])
        delivery_charge = 5 if otype == 'Delivery' else 0  # Adjust delivery charge as needed
        total += delivery_charge

        # Create the order
        order = Order.objects.create(
            name=name,
            email=email,
            phone=phone,
            time=time,
            address=address,
            instruction=instruction,
            total=total,
            charge=delivery_charge,
            otype=otype,
        )

        # Add cart items to the order
        for item in cart_items:
            order.cart.add(item)

        # Save the order
        order.save()

        return redirect('home:home-page')

    return render(request, 'ui/restaurant-card.html')


def submit_feedback(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)  
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        
        feedback = Feedback(
            user=request.user,
            rating=rating,
            review=review
        )
        feedback.save()
        messages.success(request, 'Thank you for your feedback!')

        return redirect(reverse('restaurant:restaurant-card', kwargs={'slug': slug}))  
    return render(request, 'ui/restaurant-card.html', {'restaurant': restaurant})
    
def fcm_token(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        token = request.POST.get('token')
        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        device, created = FCMDevice.objects.get_or_create(registration_id=token)
        if device:
            device.user= user
            device.name= f'{user.first_name} {user.last_name}' if user.first_name else user.username
            device.type='web'
            device.save()

        return JsonResponse({'token': device.registration_id, 'created': created})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
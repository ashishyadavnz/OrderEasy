from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from .models import *
from django.utils import timezone
from restaurant.models import *
from blog.models import Post
from django.contrib.auth import authenticate,logout, login as auth_login
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from datetime import timedelta
from random import randint
from django.contrib.auth.hashers import make_password
from django.db.models import Sum,Avg
from .forms import ProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

import threading


def home(request):
    today = datetime.datetime.now()
    restaurants = Restaurant.objects.all()
    categories = Category.objects.all()
    posts = Post.objects.all()
    testimonials = Testimonial.objects.all()
    # cuisines = Cuisine.objects.filter(menu_cuisine__restaurant__in=restaurants).distinct()
    # cuisines = Cuisine.objects.filter(fooditems_cuisine__isnull=False).distinct()
    cuisines = Cuisine.objects.all()
    if request.user.is_authenticated:
        orders = Order.objects.filter(timestamp__date=today.date())
        sum = orders.aggregate(Sum('total'))['total__sum'] or 0
        order_count = len(orders)
        avg = orders.aggregate(Avg('total'))['total__avg'] or 0
        if request.user.role == 'Owner':
            return render(request, 'ui/owner-dashboard.html',{"today_kpi":{'total_amount':sum,'order_count':order_count,'average':avg}})
        

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
                status = 'Inactive'
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
            payment_method = request.POST.get('payment_method', 'Cash') 

            odr = Order.objects.get(id=odrid)
            if not odr.user:
                user = User.objects.filter(username=phone).last()
                print(user)
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
            odr.status = 'Active'
            odr.pmethod = payment_method
            odr.save()
            
            # email send to owner
            message = loader.render_to_string('email/order_owner.html', {
                'restaurant_owner': odr.restaurant.owner,
                'order': odr,
                'cart_items': request.session.get('cart_items', [])
            })
            to_email = odr.restaurant.email
            subject = f"New Order Received from {first_name} {last_name}"
            threading.Thread(
                target=custom_emailmessage,
                args=(subject, message, to_email, True)
            ).start()
            
            # email send to customer
            message = loader.render_to_string('email/order_confirm.html', {
                'first_name': first_name,
                'order': odr,
                'url': request.META.get('HTTP_REFERER'),
                'cart_items': request.session.get('cart_items', [])
            })
            to_email = odr.email
            print(to_email)
            subject = "Order Confirmation"
            threading.Thread(
                target=custom_emailmessage,
                args=(subject, message, email, True)
            ).start()

            # push notification send to owner
            devices = FCMDevice.objects.filter(user=odr.user)
            title = f'Order Received'
            body = f'New Order Received from {first_name} {last_name}. Order id is {odr.orderid}.'
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

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST['username']
        mobile = request.POST['mobile']

        try:
            user = User.objects.get(username=username, mobile=mobile)
            otp = randint(100000, 999999)
            user.otp = otp
            user.otp_sent_at = timezone.now()
            user.save()
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}. It is valid for 10 minutes.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('home:verify_otp', user_id=user.id)
        except User.DoesNotExist:
            messages.error(request, 'No account found with the provided username and mobile number.')
            return redirect('home:forgot_password')

    return render(request, 'ui/forgot_password.html')


def verify_otp(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST['otp']
        time_difference = timezone.now() - user.otp_sent_at
        if user.otp == int(entered_otp) and time_difference <= timedelta(minutes=10):
            return redirect('home:reset_password', user_id=user.id)
        else:
            messages.error(request, 'Invalid or expired OTP.')
            return redirect('home:verify_otp', user_id=user.id)

    return render(request, 'ui/verify_otp.html', {'user': user})

def reset_password(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password == password_confirm:
            user.password = make_password(password)
            user.save()
            messages.success(request, 'Password reset successfully. You can now log in.')
            return redirect('home:login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('home:reset_password', user_id=user.id)

    return render(request, 'ui/reset_password.html', {'user': user})

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
        otype = request.POST.get('otype', 'Delivery')  
        cart_items = request.POST.getlist('cart_items')
        total = sum([item.price * item.quantity for item in cart_items])
        delivery_charge = 5 if otype == 'Delivery' else 0  
        total += delivery_charge
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
        for item in cart_items:
            order.cart.add(item)

        order.save()

        return redirect('home:home-page')

    return render(request, 'ui/restaurant-card.html')

def submit_feedback(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)  
    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in to submit feedback.')
        return redirect(reverse('home:login') + f'?next={request.path}')

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
    
@csrf_exempt
def fcm_token(request):
    if request.method == 'POST' and request.user.is_authenticated:
        token = request.POST.get('token')
        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        device, created = FCMDevice.objects.get_or_create(
            registration_id=token,
            defaults={'user': request.user, 'type': 'web'}
        )
        if not created:
            device.user = request.user
            device.name = f'{request.user.first_name} {request.user.last_name}' if request.user.first_name else request.user.username
            device.type = 'web'
            device.active = True
            device.save()

        return JsonResponse({'token': device.registration_id, 'created': created}, status=201)

    return JsonResponse({'error': 'Invalid request or not authenticated'}, status=200)

@csrf_exempt
def index(request):
    devices = FCMDevice.objects.filter(active=True)
    data = {
        'type': "Alert",
    }

    notification = Notification(title="Test Title", body="This is a test notification", image=settings.EASYLOGO)

    from firebase_admin.messaging import UnregisteredError, SendResponse

    responses = []
    for device in devices:
        try:
            response = device.send_message(
                Message(notification=notification, data=data)
            )
            if isinstance(response, SendResponse) and response.message_id:
                responses.append({
                    'device_id': device.id,
                    'message_id': response.message_id
                })
            else:
                responses.append({
                    'device_id': device.id,
                    'error': f'Error sending to device {device.id}: {response.exception}'
                })
        except UnregisteredError:
            responses.append({
                'device_id': device.id,
                'error': 'Device token unregistered'
            })

    return JsonResponse({'status': 'Notifications sent', 'responses': responses})

def page_detail(request,slug):
    item = Pages.objects.filter(slug=slug,status='Active').last()
    if item:
        return render(request, 'ui/custom-page.html',{"page":"item","item":item})
    else:
        return redirect('/page-not-found/')
    
def profile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ProfileForm(request.POST, request.FILES,instance=request.user)
            if form.is_valid():
                form = form.save(commit=False)
                request.form = request.user
                form.save()
                messages.success(request, "Profile Updated.")
                return redirect('home:profile')
            else:
                messages.error(request, "Error.")
                return redirect('home:profile')
        else:
            form = ProfileForm(instance=request.user)
        return render (request , 'ui/profile.html',{'user':request.user,'form':form})
    else:
       return HttpResponse('you are not authorized to access this page')

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was updated successfully!')
            return redirect('home:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'ui/profile.html', {'form': form})
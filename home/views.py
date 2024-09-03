from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import *
from django.utils import timezone
from restaurant.models import Cart, FoodItem, Restaurant, Category,Cuisine 
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
    user_info = None
    if request.user.is_authenticated:
        user_info = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.mobile,
        }
    
    if request.method == 'POST':
        cart_data = request.POST.get('cart_data')
        order_type = request.POST.get('order_type')
        print(order_type,"this is order type") 
        try:
            cart_items = json.loads(cart_data)
        except json.JSONDecodeError:
            cart_items = []
        request.session['cart'] = cart_items
        request.session['order_type'] = order_type  
        for item in cart_items:
            try:
                food_item = FoodItem.objects.get(id=item['id'])
                cart_item = Cart(
                    fooditem=food_item,
                    quantity=item['quantity'],
                    total=item['quantity'] * item['price']
                )
                cart_item.save()
            except FoodItem.DoesNotExist:
                continue
        
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        
        context = {
            'cart': cart_items,
            'total': total,
            'user_info': user_info,
            'order_type': order_type, 
        }
        return render(request, 'ui/checkout.html', context)

    cart = request.session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    order_type = request.session.get('order_type', 'Delivery')  
    
    context = {
        'cart': cart,
        'total': total,
        'user_info': user_info,
        'order_type': order_type,
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
    

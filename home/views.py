from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.utils import timezone
from restaurant.models import *
from blog.models import *
# Create your views here.

def home(request):
    restaurants = Restaurant.objects.all()
    cat = Category.objects.all()
    posts = Post.objects.all()
    return render(request, 'ui/indexThem.html',{'restaurants':restaurants,'cat':cat,'posts':posts})


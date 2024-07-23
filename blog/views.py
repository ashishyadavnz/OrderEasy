from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
# Create your views here.

def blog(request):
    posts = Post.objects.all() 
    return render(request, 'ui/blog.html',{'posts':posts})

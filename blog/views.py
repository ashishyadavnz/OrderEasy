from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

# Create your views here.

def blog(request):
    posts = Post.objects.all() 
    return render(request, 'ui/blog.html',{'posts':posts})

def blogDetails(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.view += 1
    post.save()
    
    # Get previous and next posts by the same author
    previous_post = Post.objects.filter(author=post.author, timestamp__lt=post.timestamp).order_by('-timestamp').first()
    next_post = Post.objects.filter(author=post.author, timestamp__gt=post.timestamp).order_by('timestamp').first()

    # Fetch comments for the post
    comments = Comment.objects.filter(post=post, parent__isnull=True, status='Active').order_by('-timestamp')

    return render(request, 'ui/single-blog.html', {
        'post': post,
        'previous_post': previous_post,
        'next_post': next_post,
        'comments': comments,
    })

def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == "POST":
        content = request.POST.get('content')
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        Comment.objects.create(
            post=post,
            name=name,
            email=email,
            mobile=mobile,
            content=content,
            status='Active'
        )
        
        return redirect(reverse('blog:blog_detail', args=[slug]))
    
    # Handle GET request
    return render(request, 'ui/single-blog.html', {'post': post})


def services(request):
   
    return render(request, 'ui/service.html',)

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, 'Email is required.')
            return redirect('blog:service')

        Subscribe.objects.create(email=email)

        messages.success(request, 'You have successfully subscribed.')
        return redirect('blog:service')

    return render(request, 'ui/service.html')
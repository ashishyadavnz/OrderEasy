from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .serializers import *
from .models import *

## pagination class

class StandardPagination(PageNumberPagination):
	page_size = 10
	page_size_query_param = 'page_size'
	max_page_size = 1000

## private apis

class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.filter(status='Active').order_by("-id")
	serializer_class = CategorySerializer
	http_method_names = ['get','put','patch']
	filterset_fields = ['title', 'slug','status']
	search_fields=['title','content']
	lookup_field = 'slug'
	
	def get_queryset(self):
		user = self.request.user
		if user.is_staff:
			return self.queryset
		return self.queryset.none()

class TagViewSet(viewsets.ModelViewSet):
	queryset = Tag.objects.filter(status='Active').order_by("-id")
	serializer_class = TagSerializer
	http_method_names = ['get','put','patch']
	filterset_fields = ['title', 'status','slug']
	search_fields=['title','content']
	lookup_field = 'slug'

	def get_queryset(self):
		user = self.request.user
		if user.is_staff:
			return self.queryset
		return self.queryset.none()

class PostViewSet(viewsets.ModelViewSet):
	queryset = Post.objects.filter(status='Active').order_by('-id')
	serializer_class = PostSerializer
	pagination_class = StandardPagination
	http_method_names = ['get','put','patch']
	filterset_fields = ['title', 'slug', 'author', 'category', 'category__slug', 'tag', 'tag__slug', 'status']
	search_fields=['title','content','author__username']
	lookup_field = 'slug'

	def get_queryset(self):
		user = self.request.user
		if user.is_staff:
			return self.queryset
		return self.queryset.none()
	
	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		instance.view += 1
		instance.save()
		serializer = self.get_serializer(instance)
		return Response(serializer.data)

class ActionViewSet(viewsets.ModelViewSet):
	queryset = Action.objects.filter(status='Active').order_by("-id")
	serializer_class = ActionSerializer
	http_method_names = ['get','post','put','patch']
	filterset_fields = ['post', 'user', 'like', 'unlike', 'favourite','status']
	search_fields = ['user__username','post__title']

## public apis 

class CommentViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Comment.objects.filter(status='Active', parent=None).order_by("-id")
	serializer_class = CommentSerializer
	http_method_names = ['get', 'post', 'patch','delete']
	filterset_fields = ['post', 'name', 'post__slug', 'content','status']
	search_fields=['name','email','website','content','user__username','post__title']

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		if request.user == instance.post.author or request.user.is_staff:
			self.perform_destroy(instance)
			return Response(status=status.HTTP_204_NO_CONTENT)
		else:
			return Response(
				{'detail': 'You do not have permission to delete this comment.'},
				status=status.HTTP_403_FORBIDDEN
            )

class CategoryPublicViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Category.objects.filter(status='Active').order_by("-id")
	serializer_class = CategorySerializer
	http_method_names = ['get']
	filterset_fields = ['title', 'slug','status']
	search_fields=['title','content']
	lookup_field = 'slug'

class TagPublicViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Tag.objects.filter(status='Active').order_by("-id")
	serializer_class = TagSerializer
	http_method_names = ['get']
	filterset_fields = ['title', 'status','slug']
	search_fields=['title','content']
	lookup_field = 'slug'

class PostPublicViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Post.objects.filter(status='Active').order_by('-id')
	serializer_class = PostSerializer
	pagination_class = StandardPagination
	http_method_names = ['get']
	filterset_fields = ['title', 'slug', 'author', 'category', 'tag', 'category__slug', 'tag__slug', 'status']
	search_fields=['title','content','author__username']
	lookup_field = 'slug'

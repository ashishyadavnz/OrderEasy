from rest_framework import viewsets
from .serializers import *

## private apis

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.filter(status='Active').order_by("-id")
    serializer_class = RestaurantSerializer
    # filterset_fields = ['title','status']
    # search_fields=['title','description']
    http_method_names = ['get', 'post', 'patch']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(status='Active').order_by("-id")
    serializer_class = CategorySerializer
    # filterset_fields = ['title','status']
    # search_fields=['title','description']
    http_method_names = ['get', 'post', 'patch']

class CuisineViewSet(viewsets.ModelViewSet):
    queryset = Cuisine.objects.filter(status='Active').order_by("-id")
    serializer_class = CuisineSerializer
    # filterset_fields = ['category','title','quantity','price','status']
    # search_fields=['category__title','title','remarks']
    http_method_names = ['get', 'post', 'patch']

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(status='Active').order_by("-id")
    serializer_class = MenuSerializer
    # filterset_fields = ['type','employee','item','quantity','price','tax','status']
    # search_fields=['employee__user__username','item__title','remarks']
    http_method_names = ['get', 'post', 'patch']
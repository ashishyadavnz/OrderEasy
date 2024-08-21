from rest_framework import viewsets
from .serializers import *

## private apis

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.filter(status='Active').order_by("-id")
    serializer_class = RestaurantSerializer
    filterset_fields = ['owner','country','state','timezone','title','slug','status']
    search_fields=['title','phone','email','city','postcode','country__name','state__name']
    http_method_names = ['get', 'post', 'patch']
    lookup_field = 'slug'

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(status='Active').order_by("-id")
    serializer_class = CategorySerializer
    filterset_fields = ['category','title','status']
    search_fields=['title','content']
    http_method_names = ['get', 'post', 'patch']
    lookup_field = 'slug'

class CuisineViewSet(viewsets.ModelViewSet):
    queryset = Cuisine.objects.filter(status='Active').order_by("-id")
    serializer_class = CuisineSerializer
    filterset_fields = ['category','title','status']
    search_fields=['title','content']
    http_method_names = ['get', 'post', 'patch']
    lookup_field = 'slug'

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(status='Active').order_by("-id")
    serializer_class = MenuSerializer
    filterset_fields = ['restaurant','cuisine','available','status']
    search_fields=['restaurant__title','cuisine__title','remarks']
    http_method_names = ['get', 'post', 'patch']

class FoodItemViewSet(viewsets.ModelViewSet):
    queryset = FoodItem.objects.filter(status='Active').order_by("-id")
    serializer_class = FoodItemSerializer
    filterset_fields = ['restaurant','cuisine','category','available','status']
    search_fields=['restaurant__title','cuisine__title','category__title','title']
    http_method_names = ['get', 'post', 'patch']
    lookup_field = 'slug'

class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.filter(status='Active').order_by("-id")
    serializer_class = VoucherSerializer
    filterset_fields = ['name','validity','status']
    search_fields=['name']
    http_method_names = ['get', 'post', 'patch']

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.filter(status='Active').order_by("-id")
    serializer_class = ReservationSerializer
    filterset_fields = ['name','email','phone','status']
    search_fields=['name','email','phone']
    http_method_names = ['get', 'post', 'patch']

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.filter(status='Active').order_by("-id")
    serializer_class = CartSerializer
    filterset_fields = ['fooditem','status']
    search_fields=['fooditem__title']
    http_method_names = ['get', 'post', 'patch']

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.filter(status='Active').order_by("-id")
    serializer_class = OrderSerializer
    filterset_fields = ['voucher','cart','name','email','phone','otype','status']
    search_fields=['voucher__name','cart__fooditem__title','name','email','phone']
    http_method_names = ['get', 'post', 'patch']

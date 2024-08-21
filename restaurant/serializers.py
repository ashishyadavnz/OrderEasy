from rest_framework import serializers
from .models import *
from geolocation.serializers import *

class UserSerializer(serializers.ModelSerializer):
	display = serializers.SerializerMethodField('showname')
	
	class Meta:
		model = User
		exclude = ('track','utrack')

	def showname(self, obj):
		return obj.display()

class RestaurantSerializer(serializers.ModelSerializer):
    owners = UserSerializer(source='owner', read_only = True)
    counties = CountrySerializer(source='country', read_only = True)
    states = StateSerializer(source='state', read_only = True)
    timezones = TimezoneSerializer(source='timezone', read_only = True)
	
    class Meta:
        model = Restaurant
        exclude = ('track','utrack')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('track','utrack')

class CuisineSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(source='category', read_only = True)

    class Meta:
        model = Cuisine
        exclude = ('track','utrack')

class MenuSerializer(serializers.ModelSerializer):
    restaurants = CategorySerializer(source='restaurant', read_only = True)
    cuisines = CategorySerializer(source='cuisine', read_only = True)
	
    class Meta:
        model = Menu
        exclude = ('track','utrack')

class FoodItemSerializer(serializers.ModelSerializer):
    restaurants = CategorySerializer(source='restaurant', read_only = True)
    cuisines = CategorySerializer(source='cuisine', read_only = True)
    categories = CategorySerializer(source='category', read_only = True)
	
    class Meta:
        model = FoodItem
        exclude = ('track','utrack')

class VoucherSerializer(serializers.ModelSerializer):	
    class Meta:
        model = Voucher
        exclude = ('track','utrack')

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        exclude = ('track','utrack')

class CartSerializer(serializers.ModelSerializer):
    fooditems = FoodItemSerializer(source='fooditem', read_only = True)
	
    class Meta:
        model = Cart
        exclude = ('track','utrack')

class OrderSerializer(serializers.ModelSerializer):
    vouchers = VoucherSerializer(source='voucher', read_only = True)
    carts = CartSerializer(source='cart', read_only = True)
	
    class Meta:
        model = Order
        exclude = ('track','utrack')

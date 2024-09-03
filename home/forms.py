from django import forms
from django.forms import ModelForm
from restaurant.models import *

class ReservationForm(ModelForm):
	class Meta:
		model = Reservation
		fields = ('name', 'email', 'phone', 'date', 'member')


class RestaurantForm(ModelForm):
	class Meta:
		model = Restaurant
		fields = ('title', 'logo', 'image', 'phone','email', 'found','city','postcode','address','website','latitude','longitude','facebook','twitter','instagram','linkedin','vip','source')

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super(RestaurantForm, self).__init__(*args, **kwargs)
		if user:
			self.fields['city'].initial = user.city
			self.fields['postcode'].initial = user.postcode
			self.fields['address'].initial = user.address
			self.fields['latitude'].initial = user.latitude
			self.fields['longitude'].initial = user.longitude


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        exclude =['restaurant','status']
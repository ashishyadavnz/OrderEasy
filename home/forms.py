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
		fields = ('title', 'logo', 'image', 'phone','email', 'found','city','postcode','address','website','latitude','longitude','facebook','twitter','instagram','linkedin')

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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields =['first_name','last_name','email','mobile','image','cover','gender','dob','country','state','city','postcode','address']
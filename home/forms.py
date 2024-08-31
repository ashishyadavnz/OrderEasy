from django import forms
from django.forms import ModelForm
from restaurant.models import *

class ReservationForm(ModelForm):
	class Meta:
		model = Reservation
		fields = ('name', 'email', 'phone', 'date', 'member')
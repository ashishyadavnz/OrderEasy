from rest_framework import serializers
from .models import *

class LanguageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Language
		exclude = ('track',)

class ContinentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Continent
		exclude = ('track',)

class CountrySerializer(serializers.ModelSerializer):
	class Meta:
		model = Country
		exclude = ('track',)

class StateSerializer(serializers.ModelSerializer):
	countries = CountrySerializer(source='country', read_only=True)
	class Meta:
		model = State
		exclude = ('track',)

class TimezoneSerializer(serializers.ModelSerializer):
	countries = CountrySerializer(source='country', read_only=True)
	class Meta:
		model = Timezone
		exclude = ('track',)

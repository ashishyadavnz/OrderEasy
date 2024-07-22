from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
	display = serializers.SerializerMethodField('showname')
	
	class Meta:
		model = User
		exclude = ('track','utrack')

	def showname(self, obj):
		return obj.display()

class SupportSerializer(serializers.ModelSerializer):
    users = UserSerializer(source='user', read_only = True)
	
    class Meta:
        model = Support
        exclude = ('track','utrack')

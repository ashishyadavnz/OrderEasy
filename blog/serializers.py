from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
	display = serializers.SerializerMethodField('showname')

	class Meta:
		model = User
		fields = ('id','display','username','first_name','last_name','email','is_active','mobile','gender','image','service','address','latitude','longitude','cover','identifier')

	def showname(self, obj):
		return obj.display()

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		exclude = ('track','utrack')

class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tag
		exclude = ('track','utrack')

class CommentSerializer(serializers.ModelSerializer):
	users = UserSerializer(source = 'user', read_only = True)
	replies = serializers.SerializerMethodField('reply')

	class Meta:
		model = Comment
		exclude = ('track','utrack')
	
	def reply(self, obj):
		return CommentSerializer(Comment.objects.filter(post=obj.post.id, parent=obj).order_by("-utimestamp")[:10],many=True).data

class ActionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Action
		fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
	authors = UserSerializer(source = 'author', read_only = True)
	categories = CategorySerializer(source='category', read_only = True)
	tags = TagSerializer(source='tag', many=True, read_only = True)
	actions = ActionSerializer(source='action_post', many=True, read_only = True)
	comments = serializers.SerializerMethodField('comment')
	likes = serializers.SerializerMethodField('my_like')
	unlikes = serializers.SerializerMethodField('my_unlike')
	favourites = serializers.SerializerMethodField('my_fav')

	class Meta:
		model = Post
		exclude = ('track','utrack')
	
	def my_like(self, obj):
		return Action.objects.filter(post=obj, like=True).count()
	
	def my_unlike(self, obj):
		return Action.objects.filter(post=obj, unlike=True).count()

	def my_fav(self, obj):
		return Action.objects.filter(post=obj, favourite=True).count()
	
	def update(self, instance, validated_data):
		if 'request' in self.context:
			my_fav = self.context['request'].data.get('fav')
			if my_fav is not None:
				if my_fav.lower() == 'false':
					instance.favourite.remove(self.context['request'].user)
				elif my_fav.lower() == 'true':
					instance.favourite.add(self.context['request'].user)
		return super().update(instance, validated_data)

	def comment(self, obj):
		cmmts = Comment.objects.filter(post=obj.id, parent=None).order_by("-id")
		try:
			queryset1 = cmmts.filter(user=self.context['request'].user)
			queryset2 = cmmts.filter(status='Active').exclude(user=self.context['request'].user)[:10]
			queryset = queryset1 | queryset2
		except:
			queryset = cmmts.filter(status='Active')[:10]
		return CommentSerializer(queryset,many=True).data
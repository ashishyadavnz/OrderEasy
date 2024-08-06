from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes,force_str
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from .models import *
from geolocation.serializers import *
import datetime
import random
import string

messages = '''(# otp #) is the OTP to verify students.
        Thanks,
        Ministry of Education.
        Government of Maharashtra.

        Powered by : eMango'''

class UserSerializer(serializers.ModelSerializer):
	token = serializers.SerializerMethodField('get_token')
	fcm = serializers.SerializerMethodField('get_fcm')
	countries = CountrySerializer(source='country', many=False, read_only=True)
	states = StateSerializer(source='state', many=False, read_only=True)
	display = serializers.SerializerMethodField('showname')
	percentage = serializers.SerializerMethodField('get_per')

	class Meta:
		model = User
		exclude = ('user_permissions','groups','password','is_superuser','track', 'utrack')
		read_only_fields = ('identifier','is_staff',)

	def get_token(self, obj):
		token, created = Token.objects.get_or_create(user=obj)
		return token.key

	def get_per(self, obj):
		return percentage(obj)

	def get_fcm(self, obj):
		fcm = FCMDevice.objects.filter(user__username=obj.username,type='web').last()
		return fcm.registration_id if fcm else ''

	def showname(self, obj):
		return obj.display()

	def validate(self, data):
		username = data.get('username')
		dob = data.get('dob')
		if username:
			if contains_specialchars(username):
				raise ValidationError({"username":"You can't use special characters in username."})
		if dob:
			today = date.today()
			five_years_ago = today - timedelta(days=5*365)
			if dob > five_years_ago:
				raise ValidationError({'dob': 'Date of birth must be at least five years ago.'})
		return data

class UserSerializer2(serializers.ModelSerializer):
	display = serializers.SerializerMethodField('showname')
	percentage = serializers.SerializerMethodField('get_per')

	class Meta:
		model = User
		exclude = ('otp','track','utrack','password','date_joined','timestamp','utimestamp','locate','groups','user_permissions')

	def showname(self, obj):
		return obj.display()

	def get_per(self, obj):
		return percentage(obj)

class UserLoginSerializer(serializers.ModelSerializer):
	type_arr = [('web', 'web'),('ios', 'ios'),('android', 'android')]
	fcm_token = serializers.CharField(style={'input_type': 'text'},write_only=True,required=False)
	fcm_type = serializers.ChoiceField(choices=type_arr)

	class Meta:
		model = User
		fields = ('username', 'password', 'fcm_token', 'fcm_type')
		extra_kwargs = {
			'username': {'required': True, 'validators': []},
			'password': {'required': True, 'style': {'input_type': 'password'}},
		}
	
	def to_representation(self, instance):
		request = self.context['request']
		serializer = UserSerializer(instance=instance, context = {'request':request})
		final = serializer.data
		final['percentage'] = percentage(instance)
		token = FCMDevice.objects.filter(user__username=instance.username,type='web').last()
		final['fcm'] = token.registration_id if token else ''
		return final

	def create(self, validated_data):
		try:
			is_user = User.objects.filter(mobile=validated_data['username']).first()
		except:
			is_user = User.objects.filter(username=validated_data['username']).first()
		if is_user is None:
			raise serializers.ValidationError({"detail":"Sorry, we couldn't find an account with this username."})
		if not is_user.check_password(validated_data['password']):
			raise serializers.ValidationError({"detail":"Sorry, your password was incorrect. Please double-check your password."})
		if is_user.dob:
			today = date.today()
			five_years_ago = today - timedelta(days=5*365)
			if is_user.dob > five_years_ago:
				raise serializers.ValidationError({"detail":"Date of birth must be at least five years ago."})
		if is_user and not is_user.is_active:
			otp = ' '.join(random.choice(string.digits[1:]) for _ in range(5))
			is_user.otp = otp.replace(' ', '')
			is_user.save()
			c = {
				'email': is_user.email,
				'domain': self.context['request'].META.get('HTTP_REFERER'),
				'site_name': 'Easy Meal',
				'uid': urlsafe_base64_encode(force_bytes(is_user.pk)),
				'user': is_user,
				'token': default_token_generator.make_token(is_user),
				'protocol': self.context['request'].scheme,
				'otp': otp,
			}
			email_template_name='email/otp.html'
			subject = "OTP Verification"
			custom_mail(subject,email_template_name,is_user,c)
			raise serializers.ValidationError({"notActive":'Account is not activated.','token':Token.objects.filter(user=is_user).last()})
		user = authenticate(username=is_user, password=validated_data['password'],)
		if user is not None:
			user.last_login = datetime.datetime.now()
			user.save()
			if validated_data.get('fcm_token') != '' and validated_data.get('fcm_token') != None:
				device, status = FCMDevice.objects.get_or_create(registration_id=validated_data['fcm_token'])
				device.user=user
				device.type=validated_data['fcm_type']
				device.name=validated_data['username']
				device.save()
			return user
		raise serializers.ValidationError({"detail":"Sorry, your password was incorrect. Please double-check your password."})

class UserCreationSerializer(serializers.ModelSerializer):
	type_arr = [('web', 'web'),('ios', 'ios'),('android', 'android')]
	fcm_token = serializers.CharField(style={'input_type': 'text'},write_only=True,required=False)
	fcm_type = serializers.ChoiceField(choices=type_arr)
	password = serializers.CharField(style={'input_type': 'password'},write_only=True)
	cpassword = serializers.CharField(style={'input_type': 'password'},write_only=True)

	class Meta:
		model = User
		fields = ('country', 'state', 'username','password','cpassword','email','mobile','first_name','last_name', 'fcm_token', 'fcm_type', 'locate')
		extra_kwargs = {
			'country': {'required': True},
			'state': {'required': True},
			'mobile': {'required': True},
			'first_name': {'required': True},
			'last_name': {'required': True},
		}

	def validate(self, data):
		if data['password'] != data['cpassword']:
			raise serializers.ValidationError({"cpassword":['Passwords do not match']})
		return data

	def to_representation(self, instance):
		request = self.context['request']
		serializer = UserSerializer(instance=instance, context = {'request':request})
		return serializer.data

	def create(self, validated_data):
		user = User.objects.create_user(country=validated_data['country'], locate=validated_data['locate'], state=validated_data['state'], username=validated_data['mobile'], email=validated_data['email'], password=validated_data['password'], mobile=validated_data['mobile'], first_name = validated_data['first_name'], last_name = validated_data['last_name'])
		if user:
			user.is_active = False
			otp = ' '.join(random.choice(string.digits[1:]) for _ in range(5))
			user.otp = otp.replace(' ', '')
			user.save()
			c = {
				'email': user.email,
				'domain': self.context['request'].META.get('HTTP_REFERER'),
				'site_name': 'Easy Meal',
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
				'user': user,
				'token': default_token_generator.make_token(user),
				'protocol': self.context['request'].scheme,
				'otp': otp,
			}
			message = messages.replace("(# otp #)",otp.replace(" ", ""))
			send_sms(user.mobile,message)
			email_template_name='email/otp.html'
			subject = "OTP Verification"
			custom_mail(subject,email_template_name,user,c)
			if validated_data.get('fcm_token') != '' and validated_data.get('fcm_token') != None:
				device, status = FCMDevice.objects.get_or_create(registration_id=validated_data['fcm_token'])
				device.user=user
				device.type=validated_data['fcm_type']
				device.name=validated_data['username']
				device.save()
				device.send_message(
					Message(notification=Notification(title="User Created", body="User Created Successfully", image="image_url"))
				)
		return user

class UserResendActivationSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username',)
		extra_kwargs = {
			'username': {'required': False, 'validators': []},
		}

	def to_representation(self, instance):
		return {'detail': 'Acitvation link sent.'}

	def create(self, validated_data):
		username = None
		if 'username' in validated_data and validated_data['username'] != '':
			username = validated_data['username']
		if username is None or username == '':
			raise serializers.ValidationError({"username": ["Invalid input."]})

		user = User.objects.filter(is_active = False).filter(Q(email=username)|Q(username=username)).first()
		
		if user:
			otp = ' '.join(random.choice(string.digits[1:]) for _ in range(5))
			c = {
				'email': user.email,
				'domain': self.context['request'].META.get('HTTP_REFERER'),
				'site_name': 'Easy Meal',
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
				'user': user,
				'token': default_token_generator.make_token(user),
				'protocol': self.context['request'].scheme,
				'otp': otp,
			}
			message = messages.replace("(# otp #)",otp.replace(" ", ""))
			send_sms(user.mobile,message)
			email_template_name='email/otp.html'
			subject = "OTP Verification"
			custom_mail(subject,email_template_name,user,c)
		serializer = UserSerializer(instance=user, context = {'request':self.context['request']})
		return serializer.data
		
class ChangePasswordSerializer(serializers.Serializer):
	model = User
	old_password = serializers.CharField(required=True, style={'input_type': 'password'})
	new_password = serializers.CharField(required=True, style={'input_type': 'password'})

	def to_representation(self, instance):
		return {'detail': 'Password changed successfully.'}

	def create(self, validated_data):
		user = self.context['request'].user
		if not user.check_password(validated_data["old_password"]):
			raise serializers.ValidationError({"old_password": ["Old password is wrong."]})
		samepp =  user.check_password(validated_data['new_password'])
		if samepp == True:
			raise serializers.ValidationError({"detail": "You have already used those password. Please try another."})
		user.set_password(validated_data["new_password"])
		user.save()
		return user

class OtpSendSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username',)
		extra_kwargs = {
			'username': {'required': True, 'validators': []},
		}

	def to_representation(self, instance):
		return {'detail': 'OTP sent successfully on both mobile and email.', 'email':instance.email,'username':instance.username}

	def create(self, validated_data):
		try:
			user = User.objects.filter(mobile=validated_data['username']).first()
		except:
			user = User.objects.filter(username=validated_data['username']).first()
		if user:
			otp = ' '.join(random.choice(string.digits[1:]) for _ in range(5))
			c = {
				'email': user.email,
				'domain': self.context['request'].META.get('HTTP_REFERER'),
				'site_name': 'Easy Meal',
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
				'user': user,
				'token': default_token_generator.make_token(user),
				'protocol': self.context['request'].scheme,
				'otp': otp
			}
			message = messages.replace("(# otp #)",otp.replace(" ", ""))
			send_sms(user.mobile,message)
			email_template_name='email/otp.html'
			subject = "OTP Verification"
			custom_mail(subject,email_template_name,user,c)
			numbers = [int(x) for x in otp.split()]
			joined_numbers = "".join(map(str, numbers))
			user.otp = int(joined_numbers)
			user.save()
			return user
		raise serializers.ValidationError({"detail":'User with this email or mobile does not exist.'})

class ForgotPasswordSerializer(serializers.ModelSerializer):
	otp = serializers.CharField(required=True)
	password = serializers.CharField(required=True, style={'input_type': 'password'})
	cpassword = serializers.CharField(required=True, style={'input_type': 'password'})
	class Meta:
		model = User
		fields = ('username','otp','password','cpassword')
		extra_kwargs = {
			'username': {'required': True, 'validators': []},
		}

	def to_representation(self, instance):
		return {'detail': 'New Password updated successfully.', 'email':instance.email}

	def create(self, validated_data):
		if validated_data['password'] != validated_data['cpassword']:
			raise serializers.ValidationError({"password": ["Both password and confirm password do not match."]})
		try:
			try:
				user = User.objects.filter(mobile=validated_data['username']).first()
			except:
				user = User.objects.filter(email=validated_data['username']).first()
		except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
			raise serializers.ValidationError({"uid": ["Invalid User."]})

		if user:
			if user.otp == int(validated_data['otp']):
				user.set_password(validated_data["password"])
				user.save()
				return user
			else:
				raise serializers.ValidationError({"otp": ["OTP is invalid."]})
		raise serializers.ValidationError({"detail":'User with this email or mobile does not exist.'})
			
class OtpLoginSerializer(serializers.ModelSerializer):
	otp = serializers.CharField(required=True)
	class Meta:
		model = User
		fields = ('username','otp')
		extra_kwargs = {
			'username': {'required': True, 'validators': []},
		}

	def to_representation(self, instance):
		request = self.context['request']
		serializer = UserSerializer(instance=instance, context = {'request':request})
		return {'detail': 'Login successfully using OTP.', **serializer.data}

	def create(self, validated_data):
		try:
			try:
				user = User.objects.filter(mobile=validated_data['username']).first()
			except:
				user = User.objects.filter(username=validated_data['username']).first()
		except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
			raise serializers.ValidationError({"uid": ["Invalid User."]})

		if user:
			if user.otp == int(validated_data['otp']):
				return user
			else:
				raise serializers.ValidationError({"otp": ["OTP is invalid."]})
		raise serializers.ValidationError({"detail":'User with this email or mobile does not exist.'})
			
class VerifyTokenSerializer(serializers.Serializer):
	model = User
	uid = serializers.CharField(required=True)
	token = serializers.CharField(required=True)
	password = serializers.CharField(required=True, style={'input_type': 'password'})
	cpassword = serializers.CharField(required=True, style={'input_type': 'password'})

	def to_representation(self, instance):
		return {'detail': 'Password changed successfully.'}

	def create(self, validated_data):
		if validated_data['password'] != validated_data['cpassword']:
			raise serializers.ValidationError({"password": ["Both password and confirm password do not match."]})
		try:
			uid = force_str(urlsafe_base64_decode(validated_data['uid']))
			user = User.objects.get(pk=uid)
		except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
			raise serializers.ValidationError({"uid": ["Invalid User."]})

		samepp =  user.check_password(validated_data['password'])
		if samepp == True:
			raise serializers.ValidationError({"detail": "You have already used those password. Please try another."})
		if user is not None and default_token_generator.check_token(user, validated_data['token']):
			user.set_password(validated_data["password"])
			user.save()
			return user
		else:
			raise serializers.ValidationError({"token": "Account activation link is invalid."})

class ActiveTokenSerializer(serializers.Serializer):
	model = User
	uid = serializers.CharField(required=True)
	token = serializers.CharField(required=True)

	def to_representation(self, instance):
		return {'detail': 'Activate Your Account.'}

	def create(self, validated_data):
		try:
			uid = force_str(urlsafe_base64_decode(validated_data['uid']))
			user = User.objects.get(pk=uid)
		except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
			raise serializers.ValidationError({"uid": ["Invalid User."]})

		if user is not None and default_token_generator.check_token(user, validated_data['token']):
			user.is_active = True
			user.save()
			return user
		else:
			raise serializers.ValidationError({"token": ["Account activation link is invalid."]})

class ActiveAccountSerializer(serializers.Serializer):
	model = User
	otp = serializers.CharField(required=True)
	token = serializers.CharField(required=False)
	email = serializers.CharField(required=False)

	def to_representation(self, instance):
		request = self.context['request']
		serializer = UserSerializer(instance=instance, context = {'request':request})
		return {'detail': 'Your Account is activated.', **serializer.data}

	def create(self, validated_data):
		token = Token.objects.filter(key=validated_data.get('token')).last()
		if token:
			user = token.user
			if user is not None:
				if str(user.otp) == validated_data.get('otp'):
					user.is_active = True
					user.save()
					return user
				else:
					raise serializers.ValidationError({"otp": ["OTP is invalid."]})
			else:
				raise serializers.ValidationError({"token": ["Token is invalid."]})
		else:
			raise serializers.ValidationError({"token": ["Token is invalid."]})

class Addresserializer(serializers.ModelSerializer):
    users = UserSerializer2(source="user",read_only=True)

    class Meta:
        model = Address
        exclude = ('track','utrack')

class BannerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Banner
		exclude = ('track','utrack')

class FeedbackSerializer(serializers.ModelSerializer):
	users = UserSerializer2(source="user", many=False, read_only=True)
	class Meta:
		model = Feedback
		exclude = ('track','utrack')

class UserDetailSerializer(serializers.ModelSerializer):
	countries = CountrySerializer(source='country', many=False, read_only=True)
	states = StateSerializer(source='state', many=False, read_only=True)
	display = serializers.SerializerMethodField('showname')
	percentage = serializers.SerializerMethodField('get_per')

	class Meta:
		model = User
		exclude = ('user_permissions','groups','password','is_staff','is_superuser', 'track', 'utrack')

	def get_per(self, obj):
		return percentage(obj)

	def showname(self, obj):
		return obj.display()

class FCMDeviceSerializer(serializers.ModelSerializer):
    users = UserSerializer2(source="user",read_only=True)

    class Meta:
        model = FCMDevice
        fields = ['id','users', 'name', 'registration_id', 'device_id', 'active', 'date_created', 'type', 'user']

class NotificationSerializer(serializers.ModelSerializer):
	users = UserSerializer2(source="user", many=False, read_only=True)
	class Meta:
		model = Notifications
		exclude = ('track','utrack')

class ContactSerializer(serializers.ModelSerializer):
	class Meta:
		model = Contact
		exclude = ('track','utrack')

class FaqsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Faqs
		exclude = ('track','utrack')

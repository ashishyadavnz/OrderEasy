from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from django.db.models import Q
from .serializers import *
from .models import *
import threading
import ast

## functions

def notificationread(notifications,read,archive):
	for i in notifications:
		if read:
			i.read = True
		if archive:
			i.archive = True
		i.save()

## private apis

class UsersViewSet(viewsets.ModelViewSet):
	queryset = User.objects.filter(is_active=True).all().order_by("-utimestamp")
	serializer_class = UserSerializer
	filterset_fields = ['email','mobile','gender','dob','country','state','city']
	search_fields=['email','gender','country__name','state__name','city','address','username','first_name','last_name']
	http_method_names = ['get','put','patch']
	
	def get_queryset(self):
		user = self.request.user
		return self.queryset.filter(is_active=True,id=user.id)

class ProfileViewSet(viewsets.ModelViewSet):
	queryset = User.objects.filter(is_active=True).all().order_by("-id")
	serializer_class = UserSerializer
	http_method_names = ['get','post','patch']

	def get_queryset(self):
		user = self.request.user
		return User.objects.filter(is_active=True,id=user.id)

class ChangePasswordView(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = ChangePasswordSerializer
	http_method_names = ['post']

class UserDetailViewSet(viewsets.ModelViewSet):
	queryset = User.objects.filter(is_active=True).all().order_by("-id")
	serializer_class = UserDetailSerializer
	filterset_fields = ['email','mobile','gender','dob','country','state','city']
	search_fields=['email','gender','country__name','state__name','city','address','username','first_name','last_name']
	http_method_names = ['get']
	lookup_field = 'id'

class FCMDeviceViewSet(viewsets.ModelViewSet):
	queryset = FCMDevice.objects.all()
	serializer_class = FCMDeviceSerializer
	http_method_names = ['get','post']

class AddressViewSet(viewsets.ModelViewSet):
	queryset = Address.objects.all().order_by("-id")
	serializer_class = Addresserializer
	http_method_names = ['get', 'patch']
	filterset_fields = ['user','address','status']
	search_fields=['user__username','address']

class NotificationsViewSet(viewsets.ModelViewSet):
	queryset = Notifications.objects.exclude(archive=True).order_by("-id")
	serializer_class = NotificationSerializer
	http_method_names = ['get', 'patch']
	filterset_fields = ['title','ntype','user','read','status']
	search_fields=['title','slug','ntype','body','user__username']

	def get_queryset(self):
		user = self.request.user
		return self.queryset.filter(Q(user__isnull=True) | Q(user=user))

class FeedbackViewSet(viewsets.ModelViewSet):
	queryset = Feedback.objects.filter(status='Active').order_by("-id")
	serializer_class = FeedbackSerializer
	http_method_names = ['get', 'post']
	filterset_fields = ['user','timestamp','utimestamp','status']
	search_fields=['user__username','status']

class AvailabilityViewSet(viewsets.ViewSet):
	def list(self, request):
		username = self.request.GET.get('username', '')
		user = User.objects.filter(username__iexact=username).exists()
		available = True
		if user:
			available = False
		return Response({"available":available}, status=HTTP_200_OK)
	
class BulkNotificationsViewSet(viewsets.ViewSet):
	def create(self, request):
		rd = request.data.get('read')
		av = request.data.get('archive')
		al = request.data.get('all')
		read = str2bool(rd)
		archive = str2bool(av)
		all = str2bool(al)
		if all:
			notifications = Notifications.objects.filter(user=self.request.user).exclude(archive=True)
		else:
			ids = request.data.get('ids')
			if isinstance(ids, str):
				ids = ast.literal_eval(ids)
			notifications = Notifications.objects.filter(id__in=ids).exclude(archive=True)
		t1 = threading.Thread(target=notificationread, args=(notifications,read,archive))
		t1.start()
		return Response({'success': True, 'status': HTTP_200_OK})

## public apis

class UserLoginView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = UserLoginSerializer
	http_method_names = ['post']

class UserCreationView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = UserCreationSerializer
	http_method_names = ['post']

class UserResendActivationView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = UserResendActivationSerializer
	http_method_names = ['post']

class OtpSendView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = OtpSendSerializer
	http_method_names = ['post']

class ForgotPasswordView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = ForgotPasswordSerializer
	http_method_names = ['post']

class OtpLoginView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = User.objects.all()
	serializer_class = OtpLoginSerializer
	http_method_names = ['post']

class VerifyTokenView(viewsets.ModelViewSet):
	permission_classes = (AllowAny, )
	queryset = User.objects.all().order_by('-id')
	serializer_class = VerifyTokenSerializer
	http_method_names = ['post']

class ActiveTokenView(viewsets.ModelViewSet):
	permission_classes = (AllowAny, )
	queryset = User.objects.all().order_by('-id')
	serializer_class = ActiveTokenSerializer
	http_method_names = ['post']

class ActiveAccountView(viewsets.ModelViewSet):
	permission_classes = (AllowAny, )
	queryset = User.objects.all().order_by('-id')
	serializer_class = ActiveAccountSerializer
	http_method_names = ['post']

class BannerViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Banner.objects.filter(status='Active').order_by("-id")
	serializer_class = BannerSerializer
	filterset_fields = ['platform','location','status']
	search_fields=['title','platform','location']
	http_method_names = ['get']

class ContactViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Contact.objects.filter(status='Active').order_by("-id")
	serializer_class = ContactSerializer
	http_method_names = ['get', 'post']
	filterset_fields = ['name','email','mobile','subject','status']
	search_fields=['name','email','mobile','subject','message']

class FaqsViewSet(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Faqs.objects.filter(status='Active').order_by("-id")
	serializer_class = FaqsSerializer
	http_method_names = ['get', 'post']
	filterset_fields = ['question','answer','timestamp','status']
	search_fields=['question','answer','status']

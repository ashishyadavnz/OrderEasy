from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.signing import Signer
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from django_extensions.db.fields import AutoSlugField
from django.core.validators import FileExtensionValidator
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from rest_framework.authtoken.models import Token
from geolocation.models import *
from datetime import timedelta, date
from .functions import *

# Create your models here.

gender = (('Male', 'Male'),('Female', 'Female'),('Other', 'Other'),)
role = (('Customer', 'Customer'),('Owner', 'Owner'))
status = (("Active","Active"),("Inactive","Inactive"),("Delete","Delete"))
source = (('Website', 'Website'),('Android', 'Android'),('iOS', 'iOS'),('AMP', 'AMP'),('PWA', 'PWA'),('Desktop', 'Desktop'))
PLATFORM = (('Android', 'Android'),('IOS', 'IOS'), ('Web', 'Web'))
method = [('GET','GET'),('HEAD','HEAD'),('POST','POST'),('PUT','PUT'),('DELETE','DELETE'),('CONNECT','CONNECT'),('OPTIONS','OPTIONS'),('TRACE','TRACE'),('PATCH','PATCH')]
ntype = (
    ('Blog', 'Blog'),
    ('Invite','Invite'),
    ('Connection', 'Connection'),
    ('Document', 'Document'),
    ('Transfer', 'Transfer'),
    ('Alert', 'Alert'),
    ('AlertReply', 'AlertReply'),
    ('Team', 'Team'),
    ('Work', 'Work'),
    ('WorkTeam', 'WorkTeam'),
    ('WorkTask', 'WorkTask'),
    ('Leave', 'Leave'),
    ('Complaint', 'Complaint'),
    ('SocietyComplaint', 'SocietyComplaint'),
    ('Feed', 'Feed'),
    ('InwardStock', 'InwardStock'),
    ('OutwardStock', 'OutwardStock'),
    ('Channel', 'Channel'),
    ('Chat', 'Chat'),
    ('Job', 'Job'),
    ('Application', 'Application'),
    ('Poll', 'Poll'),
    ('SocietyPoll', 'SocietyPoll'),
    ('Enquiry', 'Enquiry'),
)

class BaseModel(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	locate = models.TextField(blank=True,null=True)
	status = models.CharField(max_length=20, choices=status, default='Active')

	class Meta:
		abstract = True

class User(AbstractUser, BaseModel):
	referrer = models.ForeignKey("self",verbose_name="Referrer", on_delete=models.PROTECT, blank=True, null=True)
	country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
	state = models.ForeignKey(State, on_delete=models.PROTECT, blank=True, null=True)
	identifier = models.CharField(max_length=100,unique=True, null=True, blank=True)
	mobile = models.BigIntegerField(unique=True,)
	gender = models.CharField(max_length=6, choices=gender, default='Male')
	role = models.CharField(max_length=10, choices=role, default='Customer')
	dob = models.DateField(null=True, blank=True)
	image = models.ImageField(upload_to='user/image/', blank=True, null=True, default="default/st-logo.png")
	city = models.CharField(max_length=30, blank=True)
	postcode = models.PositiveIntegerField(blank=True, null=True)
	address = models.TextField(blank=True)
	latitude = models.FloatField(blank=True, null=True) 
	longitude = models.FloatField(blank=True, null=True)
	otp = models.IntegerField(default=0)
	source = models.CharField(max_length=10, choices=source, default='Website')
	notification = models.BooleanField(default=True)
	multilogin = models.BooleanField(default=False)
	guest = models.BooleanField(default=False)  

	class Meta:
		verbose_name = 'Users'
		verbose_name_plural = '01. Users'

	REQUIRED_FIELDS = ['email','mobile']

	def image_tag(self):
		return mark_safe('<img src="/media/%s" width="200" height="200"/>' % (self.image))
	image_tag.short_description = 'Image'
	image_tag.allow_tags = True

	def display(self):
		username= ""
		if self.first_name == '':
			username = self.username
		else:
			username = self.first_name+' '+self.last_name
		return username

	def clean(self):
		super().clean()
		if self.dob:
			today = date.today()
			five_years_ago = today - timedelta(days=5*365)
			if self.dob > five_years_ago:
				raise ValidationError({'dob': 'Date of birth must be at least five years ago.'})
	
	def save(self, *args, **kwargs):
		self.full_clean()
		trackupdate(self)
		self.username = str(self.username).lower().strip()
		super(User, self).save(*args, **kwargs)

class Address(BaseModel):
	user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='address_user')
	address = models.TextField()

	class Meta:
		verbose_name_plural = "02. Address"

	def __str__(self):
		return self.title
	
	def save(self, *args, **kwargs):
		trackupdate(self)
		super(Banner, self).save(*args, **kwargs)

class Banner(BaseModel):
	title = models.CharField(max_length=160)
	image = models.ImageField(upload_to='banner/')
	link = models.URLField(null=True, blank=True)
	platform = models.CharField(max_length=8, choices=PLATFORM, default='Website')
	location = models.CharField(max_length=160)

	class Meta:
		verbose_name_plural = "03. Banner"

	def __str__(self):
		return self.title
	
	def save(self, *args, **kwargs):
		trackupdate(self)
		super(Banner, self).save(*args, **kwargs)

class Track(BaseModel):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='track_user',null=True,blank=True)
	url = models.URLField()
	method = models.CharField(max_length=10, choices=method, default='GET')
	source = models.CharField(max_length=10, choices=source, default='Desktop')
	response = models.TextField()
	rqtoken = models.TextField()
	rstoken = models.TextField()

	class Meta:
		verbose_name_plural = "04. Track"

	def __str__(self):
		return str(self.user)

	def save(self, *args, **kwargs):
		if self.user:
			self.rstoken = str(Token.objects.get(user=self.user))
		else:
			self.rstoken = "token"
		super(Track, self).save(*args, **kwargs)

class Notifications(BaseModel):
	user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
	ntype = models.CharField(max_length=50, choices=ntype, default='Blog')
	title = models.CharField(max_length=200)
	slug = models.CharField(max_length=200, null=True, blank=True)
	body = models.TextField()
	image = models.URLField()
	read = models.BooleanField(default=False)
	archive = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = "05. Notifications"

	def __str__(self):
		return self.title

class Contact(BaseModel):
	name = models.CharField(max_length=160)
	email = models.EmailField()
	mobile = models.PositiveBigIntegerField()
	subject = models.CharField(max_length=250)
	message = models.TextField()

	class Meta:
		verbose_name_plural = "06. Contact Us"

	def __str__(self):
		return str(self.name)

	def save(self, *args, **kwargs):
		trackupdate(self)
		super(Contact, self).save(*args, **kwargs)

class Faqs(BaseModel):
    CATEGORY_CHOICES = [
        ('delivery', 'Delivery'),
        ('technical', 'Technical'),
        ('restaurants', 'Restaurants'),
    ]

    question = models.CharField(max_length=160)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    class Meta:
        verbose_name_plural = "07. Faqs"

    def __str__(self):
        return str(self.question)
	

class Feedback(BaseModel):
	user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='feedback_user')
	rating  = models.FloatField(default=0)
	review = models.TextField(blank=True, null=True)

	class Meta:
		verbose_name_plural = "08. Feedback"

	def __str__(self):
		return str(self.user)
	
	def save(self, *args, **kwargs):
		trackupdate(self)
		super(Feedback, self).save(*args, **kwargs)

class FaqMessage(BaseModel):
	name = models.CharField(max_length=100)
	email = models.EmailField()
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "09. Faq Query"

	def __str__(self):
		return self.name
	
class Testimonial(BaseModel):
	name = models.CharField(max_length = 80)
	image = models.ImageField(upload_to='user/image/', blank=True, null=True, default="default/st-logo.png")
	content = RichTextUploadingField()
	rating  = models.FloatField(default=0.0)

	class Meta:
		verbose_name_plural = "10.Testimonials"

	def __str__(self):
		return self.name
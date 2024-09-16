from django.db import models
from django.forms.models import model_to_dict
from django.db.models.fields.files import ImageFieldFile, FileField
from django.db.models.fields import UUIDField
from django.core.mail import send_mail, EmailMessage
from django.template import loader
from django.conf import settings
from django.apps import apps
import datetime
import json
import requests
import math

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences in coordinates
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    
    return distance

def convert_to_dict(self, data):
	id_value = data.get('id')
	updated_data = {}
	for key, value in data.items():
		field_type = self._meta.get_field(key)
		if isinstance(field_type, (FileField, models.ImageField)):
			if value:
				updated_data[f'{key}'] = value.url
			else:
				updated_data[f'{key}'] = None
		elif isinstance(field_type, UUIDField):
			updated_data[f'{key}'] = str(value)
		elif isinstance(value, datetime.date):
			if value:
				updated_data[f'{key}'] = value.strftime('%Y-%m-%d')
			else:
				updated_data[f'{key}'] = None
		elif isinstance(value, datetime.time):
			if value:
				updated_data[f'{key}'] = value.strftime('%H:%M:%S')
			else:
				updated_data[f'{key}'] = None
		elif isinstance(value, datetime.datetime):
			if value:
				updated_data[f'{key}'] = value.strftime('%Y-%m-%d %H:%M:%S')
			else:
				updated_data[f'{key}'] = None
		elif isinstance(value, ImageFieldFile):
			if value:
				updated_data[f'{key}'] = value.url
			else:
				updated_data[f'{key}'] = None
		elif key == 'track':
			updated_data[f'{key}'] = None
		elif key == 'utrack':
			updated_data[f'{key}'] = None
		elif id_value:
			if hasattr(self, key) and isinstance(getattr(self, key), models.Manager):
				m2m_manager = getattr(self, key)
				related_objects = m2m_manager.values_list("id", flat=True)
				updated_data[f'{key}'] = list(related_objects)
			else:
				updated_data[f'{key}'] = value
		else:
			updated_data[f'{key}'] = value
	return updated_data

def trackupdate(self,count=5):
	data = model_to_dict(self)
	updated_data = convert_to_dict(self, data)
	if self.utimestamp:
		updated_data['utimestamp'] = self.utimestamp.strftime('%Y-%m-%d %H:%M:%S')
	if self.utrack == '' or not self.utrack:
		ulist = []
	else:
		ulist = json.loads(self.utrack)
	if not self.id or not self.track:
		self.track = json.dumps(updated_data)
	else:
		model_name = self.__class__
		old_data = model_name.objects.get(id=self.id)
		obj_dict = model_to_dict(old_data)
		obj_dict_data = convert_to_dict(old_data, obj_dict)
		obj_dict_data['utimestamp'] = old_data.utimestamp.strftime('%Y-%m-%d %H:%M:%S')
		intersection = {k: updated_data[k] for k in updated_data if k in obj_dict_data and updated_data[k] != obj_dict_data[k]}
		ulist.append(intersection)
		if intersection != {}:
			if len(ulist) > count:
				ulist = ulist[1:]
			self.utrack = json.dumps(ulist)

def aws_image_size(image):
	image_path = image.url
	response = requests.get(image_path)
	if response.status_code == 200:
		fsize = len(response.content)
		size = fsize / (1024 * 1024)
		return round(size, 4)
	return 0.0

def save_notifications(title,body,ntype='Blog',slug=None,user=None,image=settings.EASYLOGO):
	Notifications = apps.get_model(app_label='home', model_name='Notifications')
	Notifications.objects.create(title=title,body=body,image=image,user=user,ntype=ntype,slug=slug)

def str2bool(v):
    if type(v) == bool:
        return v
    return v.lower() in ("True", "true")

def send_sms(number,message):
	res = requests.get("https://login.bulksmsgateway.in/sendmessage.php?user=Emango&password=Emango@123&mobile="+str(number)+"&message="+ str(message) +"&sender=EMAGCC&type=3&template_id=1007168733299326066")

def custom_mail(subject,email_template_name,user,c):
	email = loader.render_to_string(email_template_name, c)
	send_mail(subject, email, f'Order Easy <{settings.DEFAULT_FROM_EMAIL}>' , [user.email], html_message=email, fail_silently=False)

def custom_emailmessage(subject,message,to_email,html=False, attach=None, attachment=None):
	email = EmailMessage(subject, message, f'Order Easy <{settings.DEFAULT_FROM_EMAIL}>', to=[to_email])
	if html:
		email.content_subtype = "html"
	if attach:
		email.attach_file(attach)
	if attachment:
		filename, content, mimetype = attachment
		email.attach(filename, content, mimetype)
	email.send()

def percentage(instance):
	per = 0
	if instance.first_name:
		per += 10
	if instance.gender:
		per += 10
	if instance.image:
		per += 20
	if instance.country:
		per += 10
	if instance.state:
		per += 10
	if instance.city:
		per += 10
	if instance.latitude:
		per += 10
	if instance.dob:
		per += 10
	if instance.address:
		per += 10
	return per

def contains_specialchars(s):
    special_characters = '''
		'!"#$%&\'()*+,./:;<=>?@[\\]^`{|}~
	'''
    return any(char in special_characters for char in s)

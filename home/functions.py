from django.db import models
from django.forms.models import model_to_dict
from django.db.models.fields.files import ImageFieldFile, FileField
from django.db.models.fields import UUIDField
from django.conf import settings
from django.apps import apps
import datetime
import json
import requests

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

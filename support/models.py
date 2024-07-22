from django.db import models
from home.models import *

# Create your models here.

class Support(BaseModel):
	user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='support_user')
	title = models.CharField(max_length=160)
	content = models.TextField()

	class Meta:
		verbose_name_plural = "01. Support"

	def __str__(self):
		return str(self.user)
	
	def save(self, *args, **kwargs):
		trackupdate(self)
		super(Support, self).save(*args, **kwargs)
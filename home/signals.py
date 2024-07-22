from django.db.models.signals import post_save
from django.core.signing import Signer
from django.dispatch import receiver
from restaurant.models import *

@receiver(post_save, sender=User)
def user_add(sender, instance=None, created=False, **kwargs):
	if not instance.identifier:
		instance.identifier = Signer().sign(str(instance.id)+str(instance.mobile)+str(instance.country)+str(instance.username)).split(":")[1]
		instance.save()

@receiver(post_save, sender=Restaurant)
def user_add(sender, instance=None, created=False, **kwargs):
	if not instance.identifier:
		instance.identifier = Signer().sign(str(instance.found)+str(instance.id)+str(instance.postcode)+str(instance.owner)+str(instance.state)).split(":")[1]
		instance.save()
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

@receiver(post_save, sender=Order)
def order_add(sender, instance=None, created=False, **kwargs):
	if created:
		instance.orderid = 'ORDER00000' + str(instance.id)
		instance.save()

@receiver(post_save, sender=Cart)
def order_add(sender, instance=None, created=False, **kwargs):
	if created:
		instance.order.total = instance.order.total + instance.total
		instance.order.save()

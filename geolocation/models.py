from django.db import models

# Create your models here.

status = (("Active","Active"), ("Inactive","Inactive"), ("Delete","Delete"))
pattern = (("LR","Left to Right"), ("RL","Right to Left"), ("TB","Top to Bottom"), ("BT","Bottom to Top"))

class Language(models.Model):
	code = models.CharField(max_length=5)
	name = models.CharField(max_length=25)
	pattern = models.CharField(max_length=2, choices=pattern, default='LR')
	track = models.TextField(blank=True, editable=False)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name_plural = '01. Languages'

class Continent(models.Model):
	name = models.CharField(max_length=50)
	area = models.BigIntegerField()
	population = models.BigIntegerField()
	track = models.TextField(blank=True, editable=False)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name_plural = '02. Continents'

class Country(models.Model):
	continent = models.ForeignKey(Continent, on_delete=models.PROTECT)
	name = models.CharField(max_length=50)
	local = models.CharField(max_length=50)
	code = models.IntegerField()
	code2 = models.CharField(max_length=2)
	code3 = models.CharField(max_length=3)
	capital = models.CharField(max_length=50)
	gdp = models.BigIntegerField()
	area = models.BigIntegerField()
	population = models.BigIntegerField()
	latitude = models.FloatField()
	longitude = models.FloatField()
	track = models.TextField(blank=True, editable=False)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	class Meta:
		verbose_name_plural = "03. Countries"

	def __str__(self):
		return self.name

class State(models.Model):
	country = models.ForeignKey(Country, on_delete=models.PROTECT)
	name = models.CharField(max_length=50)
	local = models.CharField(max_length=50)
	capital = models.CharField(max_length=50)
	area = models.BigIntegerField()
	population = models.BigIntegerField()
	latitude = models.FloatField()
	longitude = models.FloatField()
	track = models.TextField(blank=True, editable=False)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return str(self.country.name)+" | "+str(self.name)
	
	class Meta:
		verbose_name_plural = "04. States"

class Timezone(models.Model):
	"""docstring for Timezone"""
	country = models.ForeignKey(Country, on_delete=models.PROTECT)
	time = models.TimeField()
	negative = models.BooleanField(default=False)
	name = models.CharField(max_length=50, blank=True, help_text="IST")
	display = models.CharField(max_length=30, help_text="Asia/Kolkata")
	utc = models.CharField(max_length=10, help_text="UTC+5:30")
	city = models.CharField(max_length=50)
	track = models.TextField(blank=True, editable=False)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.CharField(max_length=10, choices=status, default='Active')

	def __str__(self):
		return str(self.country)+' | '+str(self.utc)
	
	class Meta:
		verbose_name_plural = "05. Timezones"

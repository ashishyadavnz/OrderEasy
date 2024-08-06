from django.db import models
from home.models import *

# Create your models here.

class Restaurant(BaseModel):
	"""docstring for Restaurant"""
	owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owner')
	country = models.ForeignKey(Country, on_delete=models.PROTECT)
	state = models.ForeignKey(State, on_delete=models.PROTECT)
	timezone = models.ForeignKey(Timezone, on_delete=models.PROTECT)
	title = models.CharField(max_length=160)
	slug = AutoSlugField(populate_from=['title'], unique=True, editable=True)
	logo = models.ImageField(upload_to='company/logo/', default="default/easymeal.png")
	image = models.ImageField(upload_to='company/image/', null=True, blank=True)
	identifier = models.CharField(max_length=100,unique=True,null=True,blank=True)
	content = models.TextField(null=True,blank=True)
	found = models.DateField()
	phone = models.CharField(max_length=15)
	email = models.EmailField()
	city = models.CharField(max_length=50)
	postcode = models.CharField(max_length=10)
	address = models.TextField(null=True,blank=True)
	start = models.TimeField()
	end = models.TimeField()
	members = models.PositiveIntegerField(default=0)
	rating = models.FloatField(default=0)
	latitude = models.FloatField(default=26.8513) 
	longitude = models.FloatField(default=75.8064)
	website = models.URLField(max_length=100, blank=True)
	facebook = models.URLField(max_length=100, blank=True)
	twitter = models.URLField(max_length=100, blank=True)
	instagram = models.URLField(max_length=100, blank=True)
	linkedin = models.URLField(max_length=100, blank=True)
	verified = models.BooleanField(default=False)
	source = models.CharField(max_length=10, choices=source, default='Website')

	class Meta:
		verbose_name_plural = "01. Restaurants"

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		trackupdate(self)
		super(Restaurant, self).save(*args, **kwargs)

class Category(BaseModel):
	"""docstring for Category"""
	category = models.ForeignKey("self", on_delete=models.PROTECT, related_name="category_name", blank=True,null=True)
	title = models.CharField(max_length=160)
	slug = AutoSlugField(max_length=160, populate_from=['title'], unique=True, editable=True)
	image = models.ImageField(upload_to='restaurant/category/image', blank=True)	
	content = RichTextUploadingField()
	words = models.PositiveIntegerField(default=0)
	new_words = models.PositiveIntegerField(default=0)
	keyword = models.CharField(max_length=160)
	meta_title = models.CharField(max_length=160)
	meta_description = models.TextField()

	class Meta:
		verbose_name_plural = '02. Categories'
	
	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		trackupdate(self)
		word_count=strip_tags(self.content).replace('&nbsp;',' ').strip().split()
		newwords=len(word_count)
		counts=newwords-self.words
		self.words=newwords
		self.new_words=counts
		return super().save(*args, **kwargs)
	
class Cuisine(BaseModel):
	"""docstring for Cuisine"""
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="cuisine_category", blank=True,null=True)
	title = models.CharField(max_length=160)
	slug = AutoSlugField(max_length=160, populate_from=['title'], unique=True, editable=True)
	image = models.ImageField(upload_to='restaurant/cuisine/image', blank=True)	
	content = RichTextUploadingField()
	words = models.PositiveIntegerField(default=0)
	new_words = models.PositiveIntegerField(default=0)
	keyword = models.CharField(max_length=160)
	meta_title = models.CharField(max_length=160)
	meta_description = models.TextField()

	class Meta:
		verbose_name_plural = '03. Cuisines'
	
	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		trackupdate(self)
		word_count=strip_tags(self.content).replace('&nbsp;',' ').strip().split()
		newwords=len(word_count)
		counts=newwords-self.words
		self.words=newwords
		self.new_words=counts
		return super().save(*args, **kwargs)
	
class Menu(BaseModel):
	"""docstring for Menu"""
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="menu_restaurant")
	cuisine = models.ForeignKey(Cuisine, on_delete=models.PROTECT, related_name="menu_cuisine")
	price = models.PositiveIntegerField(default=1)
	start = models.TimeField()
	end = models.TimeField()
	available = models.BooleanField(default=True)
	keyword = models.CharField(max_length=160)
	meta_title = models.CharField(max_length=160)
	meta_description = models.TextField()

	class Meta:
		verbose_name_plural = '04. Menu'
	
	def __str__(self):
		return str(self.cuisine)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

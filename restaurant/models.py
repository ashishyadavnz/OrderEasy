from django.db import models
from home.models import *

# Create your models here.

otype = (('Delivery', 'Delivery'),('Pickup', 'Pickup'),('Schedule', 'Schedule'))

class Restaurant(BaseModel):
	"""docstring for Restaurant"""
	owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owner')
	country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
	state = models.ForeignKey(State, on_delete=models.PROTECT, blank=True, null=True)
	timezone = models.ForeignKey(Timezone, on_delete=models.PROTECT, blank=True, null=True)
	title = models.CharField(max_length=160)
	slug = AutoSlugField(populate_from=['title'], unique=True, editable=True)
	logo = models.ImageField(upload_to='company/logo/', default="default/easymeal.png")
	image = models.ImageField(upload_to='company/image/', null=True, blank=True)
	identifier = models.CharField(max_length=100,unique=True,null=True,blank=True)
	content = models.TextField(null=True,blank=True)
	found = models.DateField(null=True,blank=True)
	phone = models.CharField(max_length=15,null=True,blank=True)
	email = models.EmailField(null=True,blank=True)
	city = models.CharField(max_length=50,null=True,blank=True)
	postcode = models.CharField(max_length=10,null=True,blank=True)
	address = models.TextField(null=True,blank=True)
	start = models.TimeField(null=True,blank=True)
	end = models.TimeField(null=True,blank=True)
	members = models.PositiveIntegerField(default=0)
	rating = models.FloatField(default=0)
	latitude = models.FloatField() 
	longitude = models.FloatField()
	website = models.URLField(max_length=100,null=True,blank=True)
	facebook = models.URLField(max_length=100, null=True,blank=True)
	twitter = models.URLField(max_length=100, null=True,blank=True)
	instagram = models.URLField(max_length=100, null=True,blank=True)
	linkedin = models.URLField(max_length=100, null=True,blank=True)
	verified = models.BooleanField(default=False)
	vip = models.BooleanField(default=False)
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
	image = models.ImageField(upload_to='restaurant/category/image', null=True,blank=True)	
	content = RichTextUploadingField(null=True,blank=True)
	words = models.PositiveIntegerField(default=0)
	new_words = models.PositiveIntegerField(default=0)
	keyword = models.CharField(max_length=160,null=True,blank=True)
	meta_title = models.CharField(max_length=160,null=True,blank=True)
	meta_description = models.TextField(null=True,blank=True)

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
	# category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="cuisine_category")
	title = models.CharField(max_length=160)
	slug = AutoSlugField(max_length=160, populate_from=['title'], unique=True, editable=True)
	image = models.ImageField(upload_to='restaurant/cuisine/image', null=True,blank=True)	
	content = RichTextUploadingField(null=True,blank=True)
	words = models.PositiveIntegerField(default=0)
	new_words = models.PositiveIntegerField(default=0)
	keyword = models.CharField(max_length=160,null=True,blank=True)
	meta_title = models.CharField(max_length=160,null=True,blank=True)
	meta_description = models.TextField(null=True,blank=True)

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
	price = models.PositiveIntegerField(help_text="IN USD")
	start = models.TimeField(null=True,blank=True)
	end = models.TimeField(null=True,blank=True)
	available = models.BooleanField(default=True)
	keyword = models.CharField(max_length=160,null=True,blank=True)
	meta_title = models.CharField(max_length=160,null=True,blank=True)
	meta_description = models.TextField(null=True,blank=True)

	class Meta:
		verbose_name_plural = '04. Menu'
	
	def __str__(self):
		return str(self.cuisine)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

class FoodItem(BaseModel):
	"""docstring for Food Item"""
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="fooditems_restaurant")
	cuisine = models.ForeignKey(Cuisine, on_delete=models.PROTECT, related_name="fooditems_cuisine", null=True, blank=True)
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="fooditems_category", null=True, blank=True)
	title = models.CharField(max_length=160)
	slug = AutoSlugField(max_length=160, populate_from=['title'], unique=True, editable=True)
	image = models.ImageField(upload_to='restaurant/cuisine/image', null=True,blank=True)
	start = models.TimeField(null=True,blank=True)
	end = models.TimeField(null=True,blank=True)
	price = models.PositiveIntegerField(help_text="IN USD")
	available = models.BooleanField(default=True)
	keyword = models.CharField(max_length=160,null=True,blank=True)
	meta_title = models.CharField(max_length=160,null=True,blank=True)
	meta_description = models.TextField(null=True,blank=True)

	class Meta:
		verbose_name_plural = '05. Food Item'

	def __str__(self):
		return str(self.title)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

class Voucher(BaseModel):
	"""docstring for Voucher"""
	name = models.CharField(max_length=160)
	discount = models.PositiveIntegerField(default=0)
	payment = models.PositiveIntegerField(default=0, verbose_name="Minimum Payment for voucher")
	validity = models.DateTimeField()

	class Meta:
		verbose_name_plural = '06. Voucher'
	
	def __str__(self):
		return str(self.name)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

class Reservation(BaseModel):
	"""docstring for Reservation"""
	user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservation_user')
	name = models.CharField(max_length=160)
	email = models.EmailField()
	phone = models.PositiveIntegerField()
	date = models.DateField()
	time = models.TimeField()
	member = models.PositiveIntegerField(default=1, verbose_name="Number of Members")

	class Meta:
		verbose_name_plural = '07. Reservation'
	
	def __str__(self):
		return str(self.name)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

class Cart(BaseModel):
	menu = models.ForeignKey(Menu, on_delete=models.PROTECT, related_name="cart_menu")
	quantity = models.PositiveIntegerField()
	total = models.PositiveIntegerField(default=0)

	class Meta:
		verbose_name_plural = '08. Cart Items'

	def save(self, *args, **kwargs):
		trackupdate(self)
		self.total = self.quantity * self.menu.price
		return super().save(*args, **kwargs)

class Order(BaseModel):
	"""docstring for Order"""
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="order_restaurant")
	user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='order_user')
	voucher = models.ForeignKey(Voucher, on_delete=models.PROTECT, related_name="order_voucher", null=True, blank=True)
	cart = models.ManyToManyField(Cart, related_name="order_cart")
	orderid = models.CharField(max_length=30)
	name = models.CharField(max_length=160)
	email = models.EmailField()
	phone = models.PositiveIntegerField()
	time = models.TimeField(verbose_name="Pickup/Delivery/Schedule Time")
	address = models.TextField()
	instruction = models.TextField(verbose_name="Delivery Instructions", null=True, blank=True)
	total = models.PositiveIntegerField(help_text="IN USD", default=0)
	charge = models.PositiveIntegerField(default=0, verbose_name="Delivery Charge")
	otype = models.CharField(max_length=20, choices=otype, default='Delivery', verbose_name="Order Type")

	class Meta:
		verbose_name_plural = '09. Order'
	
	def __str__(self):
		return str(self.name)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

class Partner(BaseModel):
	"""docstring for Partner"""
	name = models.CharField(max_length=160)
	email = models.EmailField()
	phone = models.PositiveIntegerField()
	content = RichTextUploadingField()

	class Meta:
		verbose_name_plural = '10. Partner'
	
	def __str__(self):
		return str(self.name)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

class RestaurantOwner(BaseModel):
	"""docstring for Restaurant Owner"""
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="ro_restaurant")
	owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="ro_owner")

	class Meta:
		verbose_name_plural = '11. Restaurant Owner'
	
	def __str__(self):
		return str(self.owner)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

class RestaurantCustomer(BaseModel):
	"""docstring for Restaurant Customer"""
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="rc_restaurant")
	customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="rc_customer")

	class Meta:
		verbose_name_plural = '11. Restaurant Customer'
	
	def __str__(self):
		return str(self.customer)

	def save(self, *args, **kwargs):
		trackupdate(self)
		return super().save(*args, **kwargs)

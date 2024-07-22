from django.db import models
from datetime import timedelta, date
from ckeditor_uploader.fields import RichTextUploadingField
from django_extensions.db.fields import AutoSlugField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.html import strip_tags
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from home.models import User, trackupdate, save_notifications, BaseModel, settings

# Create your models here.

status = (("Draft","Draft"),("Schedule","Schedule"),("Active","Active"),("Inactive","Inactive"),("Delete","Delete"))

class Category(BaseModel):
	"""docstring for Category"""
	category = models.ForeignKey("self", on_delete=models.PROTECT, related_name="category_name", blank=True,null=True)
	title = models.CharField(max_length=160)
	slug = AutoSlugField(max_length=160, populate_from=['title'], unique=True, editable=True)
	content = RichTextUploadingField()
	posts = models.PositiveIntegerField(default=0)
	words = models.PositiveIntegerField(default=0)
	new_words = models.PositiveIntegerField(default=0)
	keyword = models.CharField(max_length=160)
	meta_title = models.CharField(max_length=160)
	meta_description = models.TextField()
	thumbnail = models.ImageField(upload_to='blog/category/thumbnail', blank=True)	
	cover = models.ImageField(upload_to='blog/category/cover', blank=True)

	class Meta:
		verbose_name_plural = '01. Categories'
	
	def __str__(self):
		return (self.title)

	def save(self, *args, **kwargs):
		trackupdate(self)
		word_count=strip_tags(self.content).replace('&nbsp;',' ').strip().split()
		newwords=len(word_count)
		counts=newwords-self.words
		self.words=newwords
		self.new_words=counts
		return super().save(*args, **kwargs)

class Tag(BaseModel):
	"""docstring for Tag"""
	title = models.CharField(max_length=160)
	slug = AutoSlugField(max_length=160, populate_from=['title'], unique=True, editable=True)
	content = RichTextUploadingField()
	posts = models.PositiveIntegerField(default=0)
	words = models.PositiveIntegerField(default=0)
	new_words = models.PositiveIntegerField(default=0)
	keyword = models.CharField(max_length=160)
	meta_title = models.CharField(max_length=160)
	meta_description = models.TextField()

	class Meta:
		verbose_name_plural = '02. Tags'

	def __str__(self):
		return (self.title)

	def save(self, *args, **kwargs):
		trackupdate(self)
		word_count=strip_tags(self.content).replace('&nbsp;',' ').strip().split()
		newwords=len(word_count)
		counts=newwords-self.words
		self.words=newwords
		self.new_words=counts
		return super().save(*args, **kwargs)
		
class Post(models.Model):
	"""docstring for Post"""
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	tag = models.ManyToManyField(Tag)
	# like = models.ManyToManyField(User, related_name='post_like',blank=True)
	# unlike = models.ManyToManyField(User, related_name='post_unlike',blank=True)
	# favourite = models.ManyToManyField(User, related_name='post_favourite')
	title = models.CharField(max_length=160)
	slug = AutoSlugField(max_length=160, populate_from=['title'], unique=True, editable=True)
	content = RichTextUploadingField()
	words = models.PositiveIntegerField(default=0)
	new_words = models.PositiveIntegerField(default=0)
	keyword = models.CharField(max_length=160)
	meta_title = models.CharField(max_length=160)
	meta_description = models.TextField()
	thumbnail = models.ImageField(upload_to='blog/thumbnail')
	featured = models.ImageField(upload_to='blog/image')
	view = models.PositiveIntegerField(default=0)
	bookmark = models.PositiveIntegerField(default=0)
	impression = models.PositiveIntegerField(default=0)
	timestamp = models.DateTimeField(auto_now_add=True, editable=False)
	utimestamp = models.DateTimeField(auto_now=True, editable=False)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	locate = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=status, default='Draft')

	class Meta:
		verbose_name_plural = '03. Posts'

	def __str__(self):
		return (self.title)

	def comments(self):
		yesterday = date.today() + timedelta(days=-1)
		return Comment.objects.filter(post = self.id, parent=None, status='Active').order_by('-id') | Comment.objects.filter(post = self.id, parent=None, timestamp__gte=yesterday).order_by('-id')

	def comment_count(self):
		return Comment.objects.filter(post = self.id).count()

	def save(self, *args, **kwargs):
		trackupdate(self)
		word_count=strip_tags(self.content).replace('&nbsp;',' ').strip().split()
		newwords=len(word_count)
		counts=newwords-self.words
		self.words=newwords
		self.new_words=counts
		super(Post, self).save(*args, **kwargs)
		posts = Post.objects.all()
		cposts = posts.filter(category=self.category).count()
		self.category.posts = cposts
		self.category.save()
		for i in self.tag.all():
			tposts = Post.objects.filter(tag=i).count()
			i.posts = tposts
			i.save()
		data = {'type': "Post",'id':str(self.id), 'slug':str(self.slug)}
		title="New blog post added! Check it out now."
		body="New blog post added! Check it out now."
		users = User.objects.filter(notification=True).exclude(id=self.author.id).values_list("id", flat=True)
		FCMDevice.objects.filter(user__in=users).send_message(
			Message(notification=Notification(title=title, body=body, image=settings.EASYLOGO),data=data)
		)
		save_notifications(title,body,ntype='Post', slug=str(self.slug), user=self.author)

class Action(BaseModel):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='action_post')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_user')
	share = models.PositiveIntegerField(default=0)
	like = models.BooleanField(default=False)
	unlike = models.BooleanField(default=False)
	favourite = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = '04. Actions'

	def __str__(self):
		return str(self.post)
	
	def save(self, *args, **kwargs):
		trackupdate(self)
		if self.like:
			self.unlike = False
		if self.unlike:
			self.like = False
		super(Action, self).save(*args, **kwargs)

class Comment(models.Model):
	"""docstring for Comment"""
	parent = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, null=True)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	name = models.CharField(max_length=30)
	email = models.EmailField(verbose_name='Email')
	website = models.URLField(blank=True)
	mobile 	= models.BigIntegerField(validators=[MinValueValidator(5000000000),MaxValueValidator(999999999999)])
	content = models.TextField()
	notify = models.BooleanField(default=False)
	pin = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True)
	utimestamp = models.DateTimeField(auto_now=True)
	track = models.TextField(blank=True, editable=False)
	utrack = models.TextField(blank=True, editable=False)
	locate = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=status, default='Inactive')

	class Meta:
		verbose_name_plural = '05. Comments'

	def __str__(self):
		return (self.name)

	def reply(self):
		return Comment.objects.filter(parent = self.id, status='Active').all()
	
	def save(self, *args, **kwargs):
		trackupdate(self)
		super(Comment, self).save(*args, **kwargs)

class Badword(BaseModel):
	"""docstring for Badword"""
	title = models.CharField(max_length=20, unique=True)
	count = models.PositiveIntegerField(default=0)

	class Meta:
		verbose_name_plural = '06. Badwords'

	def __str__(self):
		return self.title
	
	def save(self, *args, **kwargs):
		trackupdate(self)
		super(Badword, self).save(*args, **kwargs)
		
class Subscribe(BaseModel):
	"""docstring for Subscribe"""
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	email = models.EmailField(verbose_name='Email')
	mobile = models.CharField(max_length=10)
	name = models.CharField(max_length=100)
	url = models.URLField(max_length=100)

	class Meta:
		verbose_name_plural = '07. Subscribe'

	def save(self, *args, **kwargs):
		trackupdate(self)
		if self.user.notification:
			device = FCMDevice.objects.filter(user=self.user)
			if self.id:
				data = {'type': "Subscribed_Id",'id':str(self.id)}
			else:
				data = {'type': "Subscribed",}
			if device:
				device.send_message(
					Message(notification=Notification(title="Subscribed", body="Subscribed Successfully", image=settings.EASYLOGO),data=data)
				)
		return super().save(*args, **kwargs)

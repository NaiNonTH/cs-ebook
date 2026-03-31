from django.db import models
from django.contrib.auth.models import User

from django.core.validators import FileExtensionValidator, MinValueValidator
from taggit.managers import TaggableManager

# Create your models here.

class EBook(models.Model):
	category = models.CharField(
		max_length=4,
		choices=[
			('COMP', 'คอมพิวเตอร์'),
			('DATA', 'วิทยาศาสตร์ข้อมูล'),
			('CENG', 'วิศวกรรมคอมพิวเตอร์')
		],
	)
	title = models.CharField(max_length=255)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	description = models.TextField()
	cover = models.ImageField(
		upload_to='cover/',
    	validators=[
        	FileExtensionValidator(allowed_extensions=['jpg', 'png'])
        ]
    )
	sample = models.FileField(
		upload_to='sample/',
    	validators=[
         	FileExtensionValidator(allowed_extensions=['pdf'])
        ]
    )
	token = models.IntegerField(validators=[MinValueValidator(0)])
	publish_date = models.DateField()
	page_count = models.IntegerField(validators=[MinValueValidator(1)])
	post_status = models.CharField(
		max_length=1,
		choices=[
			('P', 'Publish'),
			('U', 'Unpublish')
		]
	)
	tags = TaggableManager()

class LogRead(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	ebook = models.ForeignKey(EBook, on_delete=models.CASCADE)
	page_number = models.IntegerField()
	date_time = models.DateTimeField(auto_now_add=True)

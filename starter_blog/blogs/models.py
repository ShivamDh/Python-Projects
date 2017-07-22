from django.db import models

# Create your models here.

class Blog(models.Model):
	title = models.CharField(max_length=150, default="New Blog")
	date = models.DateField()
	body = models.TextField()
	summary = models.TextField()
	imgSrc = models.CharField(max_length=100, default="")
	
	def __str__(self):
		return self.title
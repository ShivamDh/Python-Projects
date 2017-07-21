from django.db import models

# Create your models here.

class Blog(models.Model):
	title = models.CharField(max_length=150)
	date = models.DateField()
	body = models.TextField()
	summary = models.TextField()
	
	def __str__(self):
		return self.title
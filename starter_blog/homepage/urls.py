from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import ListView
from blogs.models import Blog

urlpatterns = [
    url(r'^$',ListView.as_view(queryset=Blog.objects.all().order_by('date'), 
		template_name='home.html'))
]

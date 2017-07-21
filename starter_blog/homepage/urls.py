from django.conf.urls import url, include
from django.contrib import admin
from . import views
from blogs.models import Blog

urlpatterns = [
    url(r'^$', views.index, name='index'),
]

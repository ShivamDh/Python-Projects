from django.shortcuts import render
from django.http import HttpResponse

def blogs(request):
    return render(request, 'blogs.html')
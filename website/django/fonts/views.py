from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    HttpResponse("Hello, world. You're at the polls index.")

def name(request):
    HttpResponse("You should get a fontname here.")

def img(request):
    HttpResponse("You should get an image back here.")

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^img', views.img, name='img'),
    url(r'^name', views.name, name='name'),
]

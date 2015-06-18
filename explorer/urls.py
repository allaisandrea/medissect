from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^test.json$', views.json, name='json'),
    url(r'^$', views.index, name='index')
]
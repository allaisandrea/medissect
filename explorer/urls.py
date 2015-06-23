from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^descriptor_list$', views.descriptor_list, name='descriptor_list'),
    url(r'^map_data$', views.map_data, name='map_data'),
    url(r'^$', views.main, name='main'),
]
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^procedure_list$', views.procedure_list, name='procedure_list'),
    url(r'^map_data$', views.map_data, name='map_data'),
    url(r'^$', views.main, name='main'),
]
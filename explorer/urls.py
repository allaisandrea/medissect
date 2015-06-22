from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^provider_data$', views.provider_data, name='provider_data'),
    url(r'^map_data$', views.map_data, name='map_data'),
    url(r'^map$', views.google_map, name='google_map'),
    url(r'^$', views.procedure_descriptors, name='procedure_descriptors'),
    url(r'^livesearch$', views.livesearch, name='livesearch')
]
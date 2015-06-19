from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^map_data$', views.google_map_data, name='google_map_data'),
    url(r'^map$', views.google_map, name='google_map'),
    url(r'^$', views.procedure_descriptors, name='procedure_descriptors'),
    url(r'^livesearch$', views.livesearch, name='livesearch')
]
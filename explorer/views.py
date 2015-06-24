from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ProcedureDescriptor, Provider, Procedure
import geoip
from geoip import geolite2

def main(request):
  ip=get_client_ip(request)
  # test ip
  # ip='209.6.120.223'
  match = geolite2.lookup(ip)
  # default coordinates, local server is not recognized
  user_coordinates=(42.37, -71.12)
  if match is not None:
    user_coordinates=match.location
  context = {'host': request.get_host(),'Lat': user_coordinates[0],'Lng':user_coordinates[1]}
  return render(request, 'explorer/main.html', context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def map_data(request):
  ne_lat = float(request.GET['ne_lat'])
  ne_lng = float(request.GET['ne_lng'])
  sw_lat = float(request.GET['sw_lat'])
  sw_lng = float(request.GET['sw_lng'])
  code = request.GET['proc_code']
  providers = Provider.objects.all()
    
  providers = providers.filter(latitude__gte = sw_lat)
  providers = providers.filter(latitude__lte = ne_lat)
  providers = providers.filter(longitude__gte = sw_lng)
  providers = providers.filter(longitude__lte = ne_lng)
  if(code != 'all'):
    providers = [p for p in providers if Procedure.objects.filter(provider = p).filter(descriptor__code = code).count() > 0]
  features = [
    {
      "type":"Feature",
      "properties": {
        "npi": p.npi, 
        "last_name": p.last_name, 
        "first_name": p.first_name, 
        "expensiveness": p.expensiveness},
      "geometry": {"type": "Point", "coordinates": [p.longitude, p.latitude]}
    }
  for p in providers]
  
  return JsonResponse({
    "type": "FeatureCollection",
    "features": features
  })

def descriptor_list(request):
  #Todo: make search case insensitive, split string and search for
  # single words, sort result by most common, search for code as well
  # as for description
  
  npi = int(request.GET['npi'])
  string = request.GET['str']
  
  if len(string) > 3:
    descriptors = ProcedureDescriptor.objects.filter(descriptor__contains = string)
  else:
    descriptors = ProcedureDescriptor.objects.all()
  if(npi != 0):
    descriptors = [d for d in descriptors if Procedure.objects.filter(descriptor = d).filter(provider__npi = npi).count() > 0]
    
  return JsonResponse({
    "type": "DescriptorList",
    "descriptors": [[d.code, d.descriptor] for d in descriptors]
  })

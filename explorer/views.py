from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ProcedureDescriptor, Provider

def google_map(request):
  context = {'host': request.get_host()}
  return render(request, 'explorer/google_map.html', context)

def google_map_data(request):
  ne_lat = float(request.GET['ne_lat'])
  ne_lng = float(request.GET['ne_lng'])
  sw_lat = float(request.GET['sw_lat'])
  sw_lng = float(request.GET['sw_lng'])
  
  providers = Provider.objects.all()
  providers = providers.filter(latitude__gte = sw_lat)
  providers = providers.filter(latitude__lte = ne_lat)
  providers = providers.filter(longitude__gte = sw_lng)
  providers = providers.filter(longitude__lte = ne_lng)
  
  coordinates = [[p.longitude, p.latitude] for p in providers]
  
  return JsonResponse(
    {
      "type": "FeatureCollection",
      "features": [
        { 
          "type": "Feature",
          "geometry": {"type": "MultiPoint", "coordinates": coordinates }
        }
      ]
    }
  )

def procedure_descriptors(request):
  context = {
    'host': request.get_host()
    }
  
  return render(request, 'explorer/procedure_descriptors.html', context)

def livesearch(request):
  
  query = request.GET['q']
  if len(query) > 0:
    descriptor_list = ProcedureDescriptor.objects.filter(descriptor__contains = query)
  else:
    descriptor_list = ProcedureDescriptor.objects.all()
  context = {
    'descriptor_list': descriptor_list
    }
  return render(request, 'explorer/search_response.html', context)
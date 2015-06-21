from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ProcedureDescriptor, Provider

def google_map(request):
  context = {'host': request.get_host()}
  return render(request, 'explorer/google_map.html', context)

def google_map_data(request):
  providers = Provider.objects.all();
  coordinates = [[p.longitude, p.latitude] for p in providers];
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
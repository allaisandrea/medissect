from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ProcedureDescriptor

def google_map(request):
  context = {'host': request.get_host()}
  return render(request, 'explorer/google_map.html', context)

def google_map_data(request):
  return JsonResponse(
    {
      "type": "FeatureCollection",
      "features": [
        { 
          "type": "Feature",
          "geometry": {"type": "Point", "coordinates": [-71.11, 42.37]}
        },
        { 
          "type": "Feature",
          "geometry": {"type": "Point", "coordinates": [-71.06, 42.33]}
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
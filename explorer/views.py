from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
def index(request):
  context = {'host': request.get_host()}
  return render(request, 'explorer/index.html', context)
def json(request):
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

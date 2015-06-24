from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ProcedureDescriptor, Provider, Procedure, Location

def main(request):
  context = {'host': request.get_host()}
  return render(request, 'explorer/main.html', context)

def map_data(request):
  ne_lat = float(request.GET['ne_lat'])
  ne_lng = float(request.GET['ne_lng'])
  sw_lat = float(request.GET['sw_lat'])
  sw_lng = float(request.GET['sw_lng'])
  code = request.GET['proc_code']
  locations = Location.objects.all()
    
  locations = locations.filter(latitude__gte = sw_lat)
  locations = locations.filter(latitude__lte = ne_lat)
  locations = locations.filter(longitude__gte = sw_lng)
  locations = locations.filter(longitude__lte = ne_lng)
  locations = locations[:200]
  
  if(code == 'all'):
    providers = Provider.objects.all()
  else:
    providers = Provider.objects.filter(procedure__descriptor__code = code)
  
  features = []
  for loc in locations:
    providers1 = providers.filter(location = loc)
    if(providers1.count() > 0):
      features.append({
        "type":"Feature",
        "properties": {
          "providers": [{
            "npi": p.npi, 
            "last_name": p.last_name, 
            "first_name": p.first_name, 
            "expensiveness": p.expensiveness} for p in providers1]
          },
        "geometry": {"type": "Point", "coordinates": [loc.longitude, loc.latitude]}
      })
  
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
    descriptors = descriptors.filter(procedure__provider__npi = npi)
    
  return JsonResponse({
    "type": "DescriptorList",
    "descriptors": [[d.code, d.descriptor] for d in descriptors]
  })

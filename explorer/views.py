from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ProcedureDescriptor, Provider, Procedure, Location, ProcedureAvgCharges
from django.db.models import Q

def main(request):
  context = {'host': request.get_host()}
  return render(request, 'explorer/main.html', context)

def map_data(request):
  max_n_locations = 50;
  
  ne_lat = float(request.GET['ne_lat'])
  ne_lng = float(request.GET['ne_lng'])
  sw_lat = float(request.GET['sw_lat'])
  sw_lng = float(request.GET['sw_lng'])
  code = request.GET['proc_code']
  lat = 0.5 * ne_lat + 0.5 * sw_lat;
  lng = 0.5 * ne_lng + 0.5 * sw_lng;
  d_lat = ne_lat - sw_lat;
  d_lng = ne_lng - sw_lng;

  locations = Location.objects.raw(
    'SELECT * FROM explorer_location ORDER BY \
        GREATEST(\
          ABS((latitude -  %(lat0)s) / %(dlat)s), \
          ABS((longitude - %(lng0)s) / %(dlng)s)\
          ) asc',
    params = {"lat0": lat, "lng0": lng, "dlat": d_lat, "dlng": d_lng})
  truncated = False;
   
  features = []
  for location in locations[:max_n_locations]:
    providers = location.provider_set.all()
    if(code == "all"):
      unit = ""
      providers = providers.order_by("last_name", "first_name")
      costs = [p.expensiveness for p in providers];
    else:
      unit = "$"
      buf = providers;
      providers = [];
      costs = [];
      for provider in buf:
        procedures = provider.procedure_set.filter(descriptor__code = code)
        avgCharges = ProcedureAvgCharges.objects.get(
          descriptor__code = code,
          year = 2013);
        if(procedures.count() > 0):
          providers.append(provider)
          costs.append(procedures[0].submitted_avg / avgCharges.allowed)
    
    if(len(providers) > 0):
      features.append({
        "type":"Feature",
        "properties": {
          "providers": [{
            "npi": p.npi, 
            "last_name": p.last_name, 
            "first_name": p.first_name, 
            "expensiveness": p.expensiveness} for p in providers],
          "min_expensiveness": min(costs),
          "max_expensiveness": max(costs),
          "unit": unit
          },
        "geometry": {
          "type": "Point", 
          "coordinates": [
            location.longitude, 
            location.latitude
            ]
          }
      })
          
  return JsonResponse({
    "type": "FeatureCollection",
    "features": features,
    "procedure": code
  })

def procedure_list(request):
  
  npi = int(request.GET['npi'])
  string = request.GET['str']
  
  if npi == 0:
    procedures = ProcedureAvgCharges.objects.filter(year = 2013)
    if len(string) > 3:
      tokens = string.split(" ")
      for token in tokens:
        procedures = procedures.filter(Q(descriptor__descriptor__icontains = token)|Q(descriptor__code__icontains = token))
    else:
      procedures = procedures.all()
    procedures = procedures.order_by('-count');
    return JsonResponse({
      "type": "ProcedureList",
      "procedures": [[
        p.descriptor.code, 
        p.descriptor.descriptor, 
        p.count,
        p.allowed,
        p.submitted
        ] for p in procedures[:50]],
      "provider": {"npi": 0}
      
    })
  else:
    procedures = Procedure.objects.filter(provider__npi = npi);
    if len(string) > 3:
      tokens = string.split(" ")
      for token in tokens:
        procedures = procedures.filter(Q(descriptor__descriptor__icontains = token)|Q(descriptor__code__icontains = token))
    procedures = procedures.order_by('-procedure_count')
    if procedures.count() > 0:
      provider = procedures[0].provider
    else:
      provider = Provider.objects.filter(npi = npi)[0]
    return JsonResponse({
      "type": "ProcedureList",
      "procedures": [[
        p.descriptor.code, 
        p.descriptor.descriptor, 
        p.procedure_count,
        p.allowed_avg,
        p.submitted_avg
        ] for p in procedures],
      "provider": {
        "npi": npi, 
        "first_name": provider.first_name,
        "last_name": provider.last_name
      }
    })
      

def provider_list(request):
  
  string = request.GET['str']
  
  providers = Provider.objects.all()
  if len(string) > 3:
    tokens = string.split(" ")
    for token in tokens:
      providers = providers.filter(Q(first_name__icontains = token)|Q(last_name__icontains = token))
  else:
    pass
  return JsonResponse({
    "type": "ProviderList",
    "providers": [{
      "npi": p.npi,
      "first_name": p.first_name,
      "last_name": p.last_name,
      "street1": p.location.street,
      "street2": p.street2,
      "city": p.location.city,
      "state": p.location.state,
      "longitude": p.location.longitude,
      "latitude": p.location.latitude
      } for p in providers[:10]]
  })
  
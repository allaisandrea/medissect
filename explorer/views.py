from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ProcedureDescriptor, Provider, Procedure, Location, ProcedureAvgCharges
from django.db.models import Q

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
  if(locations.count() > 1000):
    return JsonResponse({"type": "TooMuchMapData"})
  
  if(code == 'all'):
    providers = Provider.objects.all()
    
    features = []
    for loc in locations:
      providers1 = providers.filter(location = loc)
      providers1 = providers1.order_by("expensiveness")
      costs = [p.expensiveness for p in providers1];
      if(providers1.count() > 0):
        features.append({
          "type":"Feature",
          "properties": {
            "providers": [{
              "npi": p.npi, 
              "last_name": p.last_name, 
              "first_name": p.first_name, 
              "expensiveness": p.expensiveness} for p in providers1],
            "min_expensiveness": min(costs),
            "max_expensiveness": max(costs),
            "unit": ""
            },
          "geometry": {"type": "Point", "coordinates": [loc.longitude, loc.latitude]}
        })
            
  else:
    procedures = Procedure.objects.filter(descriptor__code = code)
    avg_charges = ProcedureAvgCharges.objects.filter(descriptor__code = code, year = 2013)
    features = []
    for loc in locations:
      procedures1 = procedures.filter(provider__location = loc)
      procedures1 = procedures1.order_by("submitted_avg")
      costs = [p.submitted_avg / avg_charges[0].allowed for p in procedures1]
      if(procedures1.count() > 0):
        features.append({
          "type":"Feature",
          "properties": {
            "providers": [{
              "npi": p.provider.npi, 
              "last_name": p.provider.last_name, 
              "first_name": p.provider.first_name, 
              "expensiveness": p.submitted_avg} for p in procedures1],
            "min_expensiveness": min(costs),
            "max_expensiveness": max(costs),
            "unit": "$"
            },
          "geometry": {"type": "Point", "coordinates": [loc.longitude, loc.latitude]}
        })

  
  return JsonResponse({
    "type": "FeatureCollection",
    "features": features
  })

def procedure_list(request):
  
  npi = int(request.GET['npi'])
  string = request.GET['str']
  
  if npi == 0:
    procedures = ProcedureAvgCharges.objects.filter(year = 2013)
    if len(string) > 3:
      tokens = string.split(" ")
      for token in tokens:
        procedures = procedures.filter(Q(descriptor__descriptor__icontains = token)|Q(descriptor__code = token))
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
      procedures = procedures.filter(procedure__descriptor__icontains = string)
      tokens = string.split(" ")
      for token in tokens:
        procedures = procedures.filter(Q(procedure__descriptor__icontains = token)|Q(procedure__code = token))
    procedures = procedures.order_by('-procedure_count')
    provider = procedures[0].provider;
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
  
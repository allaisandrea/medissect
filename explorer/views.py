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
  locations = locations[:200]
  
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
            "max_expensiveness": max(costs)
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
            "max_expensiveness": max(costs)
            },
          "geometry": {"type": "Point", "coordinates": [loc.longitude, loc.latitude]}
        })

  
  return JsonResponse({
    "type": "FeatureCollection",
    "features": features
  })

def procedure_list(request):
  #Todo: make search case insensitive, split string and search for
  # single words, sort result by most common, search for code as well
  # as for description
  
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
        ] for p in procedures[:20]]
    })
  else:
    procedures = Procedure.objects.filter(provider__npi = npi);
    if len(string) > 3:
      procedures = procedures.filter(procedure__descriptor__icontains = string)
      tokens = string.split(" ")
      for token in tokens:
        procedures = procedures.filter(Q(procedure__descriptor__icontains = token)|Q(procedure__code = token))
    procedures = procedures.order_by('-procedure_count')
    return JsonResponse({
      "type": "ProcedureList",
      "procedures": [[
        p.descriptor.code, 
        p.descriptor.descriptor, 
        p.procedure_count,
        p.allowed_avg,
        p.submitted_avg
        ] for p in procedures[:20]]
    })
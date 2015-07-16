from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ProcedureDescriptor, Provider, Procedure, Location, ProcedureAvgCharges
from django.db.models import Q
import itertools
import sys

def main(request):
  context = {'host': request.get_host()}
  return render(request, 'explorer/main.html', context)

def map_data(request):
  max_n_providers = 500;
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
  
  if(code == 'all'):
    unit = ''
    providers = Provider.objects.raw(
      "select explorer_provider.*\
      from explorer_provider\
        join explorer_location\
          on explorer_provider.location_id = explorer_location.id\
        where\
          greatest(\
            abs((explorer_location.latitude -  %(lat0)s) / %(dlat)s),\
            abs((explorer_location.longitude - %(lng0)s) / %(dlng)s)\
          ) < 0.5\
        order by\
          greatest(\
            abs((explorer_location.latitude -  %(lat0)s) / %(dlat)s),\
            abs((explorer_location.longitude - %(lng0)s) / %(dlng)s)\
          ) asc\
        limit %(limit)s",
      params = {
        "limit": max_n_providers,
        "lat0": lat, 
        "lng0": lng, 
        "dlat": d_lat, 
        "dlng": d_lng
        }
      );
  else:
    unit = '$'
    providers = Provider.objects.raw(
      "select \
        explorer_provider.id as id,\
        explorer_provider.npi as npi,\
        explorer_provider.last_name as last_name,\
        explorer_provider.first_name as first_name,\
        explorer_provider.middle_initial as middle_initial,\
        explorer_provider.credentials as credentials,\
        explorer_provider.gender as gender,\
        explorer_provider.is_organization as is_organization,\
        explorer_provider.street2 as street2,\
        explorer_provider.medicare_participant as medicare_participant,\
        explorer_provider.at_facility as at_facility,\
        explorer_provider.location_id as location_id,\
        explorer_procedure.submitted_avg as expensiveness\
      from explorer_procedure\
        join explorer_proceduredescriptor\
          on explorer_procedure.descriptor_id=explorer_proceduredescriptor.id\
        join explorer_provider\
          on explorer_procedure.provider_id = explorer_provider.id\
        join explorer_location\
          on explorer_provider.location_id = explorer_location.id\
      where\
        explorer_proceduredescriptor.code= %(code)s and\
        greatest(\
            abs((explorer_location.latitude -  %(lat0)s) / %(dlat)s),\
            abs((explorer_location.longitude - %(lng0)s) / %(dlng)s)\
          ) < 0.5\
      order by\
        greatest(\
          abs((explorer_location.latitude -  %(lat0)s) / %(dlat)s),\
          abs((explorer_location.longitude - %(lng0)s) / %(dlng)s)\
        ) asc\
      limit %(limit)s;",
      params = {
        "code": code,
        "limit": max_n_providers,
        "lat0": lat, 
        "lng0": lng, 
        "dlat": d_lat, 
        "dlng": d_lng
        }
      )
  providers = list(providers);
  normalization = min([p.expensiveness for p in providers]);
  locations = [list(i2) for i1, i2 in itertools.groupby(providers, lambda x: x.location_id)]
  
  features = [{
    "type":"Feature",
    "properties": {
      "providers": [{
        "npi": p.npi, 
        "last_name": p.last_name, 
        "first_name": p.first_name,
        "expensiveness": p.expensiveness} for p in loc],
      "min_expensiveness": min([p.expensiveness for p in loc]) / normalization,
      "unit": unit
      },
    "geometry": {
      "type": "Point", 
      "coordinates": [
        loc[0].location.longitude, 
        loc[0].location.latitude
        ]
      }
  } for loc in locations[:max_n_locations]]
  
  response = JsonResponse({
    "type": "FeatureCollection",
    "features": features,
    "procedure": code
  })
   
  return response;

def procedure_list(request):
  npi = int(request.GET['npi'])
  string = request.GET['str']
  
  if npi == 0:
    procedures = ProcedureAvgCharges.objects.filter(year = 2013)
    if len(string) > 2:
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
    if len(string) > 2:
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
        "last_name": provider.last_name,
        "credentials": provider.credentials
      }
    })
      

def provider_list(request):
  
  string = request.GET['str']
  
  providers = Provider.objects.all()
  if len(string) > 2:
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
  
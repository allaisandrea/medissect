# Computing statistics, building dictionaries:

from math import floor

provider_dictionary = dict()
provider_total_submitted = dict()
provider_total_allowed = dict()

infile = open("provider_utilization_2013.txt","r")
line = infile.readline()
line = infile.readline()
#for c in range(10000):
while True:   
    line = infile.readline()
    if(line == ""):
        break
    tokens = line.split("\t")
    
    provider_id = tokens[0]
    
    provider_dictionary[provider_id] = tokens[1:16]
    
    number_of_procedures = int(tokens[21])
    avg_allowed_charge = float(tokens[22])
    avg_submitted_charge = float(tokens[24])
    
    if provider_id not in provider_total_submitted:
        provider_total_submitted[provider_id] = avg_submitted_charge * number_of_procedures
        provider_total_allowed[provider_id] = avg_allowed_charge * number_of_procedures
    else:
        provider_total_submitted[provider_id] += avg_submitted_charge * number_of_procedures
        provider_total_allowed[provider_id] += avg_allowed_charge * number_of_procedures
    
infile.close()

provider_expensiveness = dict()
for provider_id in provider_total_submitted:
    provider_expensiveness[provider_id] = provider_total_submitted[provider_id] / provider_total_allowed[provider_id]


# Find latitude and longitude associated with provider address, fill database

import django
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from random import random
from time import sleep
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medissect.settings")
django.setup()
from explorer.models import Provider
from django.db import IntegrityError

geolocator = Nominatim()
count = 0
fail_count = 0
skip_count = 0
success_count = 0
for code in provider_dictionary:
    if(Provider.objects.filter(npi = code).count()):
        skip_count += 1
    else:
        token = provider_dictionary[code]
        if token[10] != 'MA':
            count += 1
            skip_count += 1
            continue
        
        address = token[6] + ", " + token[8] + ", " + token[10]
        location = None
        sleep(0.1 + 0.2 *random())
        try:
            location = geolocator.geocode(address)
        except GeocoderTimedOut:
            count += 1
            fail_count += 1
            continue
            
        if location:
            provider = Provider(
                npi = int(code),
                last_name = token[0],
                first_name = token[1],
                middle_initial = token[2],
                credentials = token[3],
                gender = token[4],
                is_organization = (token[5] == 'O'),
                street1 = token[6],
                street2 = token[7],
                city = token[8],
                zipcode = token[9],
                state = token[10],
                country = token[11],
                medicare_participant = (token[13] == 'Y'),
                at_facility = (token[14] == 'F'),
                longitude = location.longitude,
                latitude = location.latitude,
                expensiveness = provider_expensiveness[code]
            )
            provider.save()
            success_count += 1
        else:
            fail_count += 1
    count += 1
    print "count: {0:6d}, skip: {1:6d}, success: {2:6d}, fail: {3:6d}".format(count, skip_count, success_count, fail_count)

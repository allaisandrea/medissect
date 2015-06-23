
# coding: utf-8

# In[1]:

column_headers = [
    "Unique identifier",
    "Last name / organization",
    "First name",
    "Middle initial",
    "Credential ('', 'M.D.', 'D.O.', 'MD','DO', 'OTR', 'D.C.', ...)",
    "Gender",
    "Entity ('I' for individual, 'O' for organization)",
    "Address line 1",
    "Address line 2",
    "City",
    "Zip",
    "State",
    "Country",
    "Specialty ('Internal Medicine', 'Pathology', ...)",
    "Participates in medicare ('Y' or 'N')",
    "Place of service ('F' for facility or 'O' for other)",
    "HCPCS code (a procedure code)",
    "HCPCS code description",
    "HCPCS drug indicator ('Y' or 'N')",
    "Line service count (people, hours, miles, ...)",
    "Beneficiary unique count (number of distinct beneficiary, possibly receiving many procedures)",
    "Beneficiary day service count (number of distinct procedures, possibly on the same person)",
    "Average medicare allowed amount",
    "Standard deviation",
    "Average submitted charges amount",
    "Standard deviation",
    "Average medicare payment amount",
    "Standard deviation"
]
for i in range(0, len(column_headers)):
    print str(i) + ": " + column_headers[i]


# In[2]:

# Computing statistics, building dictionaries:

from math import floor

procedure_dictionary = dict()
provider_dictionary = dict()
procedure_count = dict()
procedure_total_submitted = dict()
procedure_total_allowed = dict()
provider_total_submitted = dict()
provider_total_allowed = dict()
max_field_lengths = [0 for i in range(0, 28)]

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
    procedure_id = tokens[16]
    
    procedure_dictionary[procedure_id] = tokens[17]
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
    
    if procedure_id not in procedure_count:
        procedure_count[procedure_id] = number_of_procedures
        procedure_total_submitted[procedure_id] = avg_submitted_charge * number_of_procedures
        procedure_total_allowed[procedure_id] = avg_allowed_charge * number_of_procedures
    else:
        procedure_count[procedure_id] += number_of_procedures
        procedure_total_submitted[procedure_id] += avg_submitted_charge * number_of_procedures
        procedure_total_allowed[procedure_id] += avg_allowed_charge * number_of_procedures
    for i in range(0, 28):
        if len(tokens[i])> max_field_lengths[i]:
            max_field_lengths[i] = len(tokens[i])
infile.close()

provider_expensiveness = dict()
for provider_id in provider_total_submitted:
    provider_expensiveness[provider_id] = provider_total_submitted[provider_id] / provider_total_allowed[provider_id]

procedure_avg_allowed = dict()
procedure_avg_submitted = dict()
for procedure_id in procedure_count:
    procedure_avg_submitted[procedure_id] = procedure_total_submitted[procedure_id] / procedure_count[procedure_id]
    procedure_avg_allowed[procedure_id] = procedure_total_allowed[procedure_id] / procedure_count[procedure_id]

procedure_distribution = dict()

infile = open("provider_utilization_2013.txt","r")
line = infile.readline()
line = infile.readline()
#for c in range(10000):
while True:
    line = infile.readline()
    if(line == ""):
        break
    tokens = line.split("\t")
    
    procedure_id = tokens[16]
    number_of_procedures = int(tokens[21])
    avg_submitted_charge = float(tokens[24])
    state = tokens[11]
    
    bin_size = procedure_avg_allowed[procedure_id]
    
    if (procedure_id, state) not in procedure_distribution:
        procedure_distribution[(procedure_id, state)] = [0 for i in range(8)]
        
    i = int(floor(avg_submitted_charge / bin_size))
    if i > 7:
        i = 7
    procedure_distribution[(procedure_id, state)][i] += number_of_procedures
    
infile.close()


# In[4]:

# Load procedure-related mySQL tables 

year = 2013
reset = True

import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medissect.settings")
django.setup()
from explorer.models import ProcedureDescriptor, ProcedureAvgCharges, ProcedureCounts
from django.db import IntegrityError

if reset:
    ProcedureDescriptor.objects.all().delete()
    ProcedureAvgCharges.objects.all().delete()
    ProcedureCounts.objects.all().delete()

for code in procedure_dictionary:
    descriptor = ProcedureDescriptor(code = code, descriptor = procedure_dictionary[code])
    try:
        descriptor.save()
    except IntegrityError:
        pass
    

# for code in procedure_dictionary:
#     descriptor = ProcedureDescriptor.objects.get(code = code)
#     charges = ProcedureAvgCharges(
#         descriptor = descriptor,
#         year = year,
#         allowed = procedure_avg_allowed[code],
#         submitted = procedure_avg_submitted[code])
#     charges.save()
    

#for pair in procedure_distribution:
#    (code, state) = pair
#    descriptor = ProcedureDescriptor.objects.get(code = code)
#    i = 0
#    for value in procedure_distribution[pair]:
#        counts = ProcedureCounts(
#            descriptor = descriptor, 
#            year = year,
#            state = state,
#            index = i,
#            value = value)
#        counts.save()
#        i += 1


# In[8]:

# Find latitude and longitude associated with provider address

from geopy.geocoders import GoogleV3
from time import sleep
from random import random
geolocator = GoogleV3()
c = 0
for code in provider_dictionary:
    c += 1
    if c > 100:
        break
    tokens = provider_dictionary[code]
    if len(tokens) == 15:
        address = tokens[6].title() + " " + tokens[8].title() + ", " + tokens[10]
        sleep(0.3 * random())
        try:
            location = geolocator.geocode(address)
        except GeocoderQuotaExceeded:
            print "Quota exceeded"
            
        if location:
            provider_dictionary[code] += [location.longitude, location.latitude]
        else:
            print "Failed to locate: " + address


# In[10]:

#Fill provider table

reset = True
from random import random

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medissect.settings")
django.setup()
from explorer.models import Provider
from django.db import IntegrityError

if reset:
    Provider.objects.all().delete()
    
for code in provider_dictionary:
    token = provider_dictionary[code]
    if len(token) == 15:
        provider = Provider(
            npi = int(code),
            last_name = token[0].title(),
            first_name = token[1].title(),
            middle_initial = token[2],
            credentials = token[3],
            gender = token[4],
            is_organization = (token[5] == 'O'),
            street1 = token[6].title(),
            street2 = token[7].title(),
            city = token[8].title(),
            zipcode = token[9],
            state = token[10],
            country = token[11],
            medicare_participant = (token[13] == 'Y'),
            at_facility = (token[14] == 'F'),
            #longitude = token[15],
            #latitude = token[16],
            longitude = 180 * (random() - 0.5),
            latitude = 90 * (random() - 0.5),
            expensiveness = provider_expensiveness[code]
        )
        try:
            provider.save()
        except IntegrityError:
            print "Probably a double entry: " + code
        


# In[15]:

reset = True
year = 2013

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medissect.settings")
django.setup()
from explorer.models import Procedure, ProcedureDescriptor, Provider

if reset:
    Procedure.objects.all().delete()
    
infile = open("provider_utilization_2013.txt","r")
line = infile.readline()
line = infile.readline()
for c in range(10000):
    line = infile.readline()
    if(line == ""):
        break
    tokens = line.split("\t")
    
    procedure_id = tokens[16]
    provider_id = int(tokens[0])
    procedure_count = int(tokens[21])
    avg_submitted_charge = float(tokens[24])
    state = tokens[11]
    
    try:
        descriptor = ProcedureDescriptor.objects.get(code = procedure_id)
    except ProcedureDescriptor.DoesNotExist:
        continue
        
    try:
        provider = Provider.objects.get(npi = provider_id)
    except Provider.DoesNotExist:
        continue
    
    procedure = Procedure(
        descriptor = descriptor,
        provider = provider,
        year = year,
        procedure_count = int(tokens[21]),
        beneficiary_count = int(tokens[20]),
        line_service_count = float(tokens[19]),
        allowed_avg = float(tokens[22]),
        allowed_std = float(tokens[23]),
        submitted_avg = float(tokens[22]),
        submitted_std = float(tokens[23]),
        payed_avg = float(tokens[22]),
        payed_std = float(tokens[23]),
    )
    procedure.save()
infile.close()


# In[7]:




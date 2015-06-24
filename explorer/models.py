from django.db import models

class ProcedureDescriptor(models.Model):
  code = models.CharField(max_length = 5, unique = True)
  descriptor = models.CharField(max_length = 256)
  
class ProcedureAvgCharges(models.Model):
  descriptor = models.ForeignKey(ProcedureDescriptor)
  year = models.IntegerField()
  allowed = models.FloatField()
  submitted  = models.FloatField()
  
class ProcedureCounts(models.Model):
  descriptor = models.ForeignKey(ProcedureDescriptor)
  year = models.IntegerField()
  state = models.CharField(max_length = 2)
  index = models.IntegerField()
  value = models.IntegerField()
  
  
class OldProvider(models.Model):
  npi = models.IntegerField(unique = True)
  last_name = models.CharField(max_length = 70)
  first_name = models.CharField(max_length = 20)
  middle_initial = models.CharField(max_length = 1)
  credentials = models.CharField(max_length = 20)
  gender = models.CharField(max_length = 1)
  is_organization = models.BooleanField()
  street1 = models.CharField(max_length = 55)
  street2 = models.CharField(max_length = 55)
  city = models.CharField(max_length = 27)
  zipcode = models.CharField(max_length = 9)
  state = models.CharField(max_length = 2)
  country = models.CharField(max_length = 2)
  medicare_participant = models.BooleanField()
  at_facility = models.BooleanField()
  latitude = models.FloatField()
  longitude = models.FloatField()
  expensiveness = models.FloatField()

class Location(models.Model):
  street = models.CharField(max_length = 55)
  city = models.CharField(max_length = 27)
  zipcode = models.CharField(max_length = 9)
  state = models.CharField(max_length = 2)
  country = models.CharField(max_length = 2)
  longitude = models.FloatField()
  latitude = models.FloatField()
  class Meta:
    unique_together = ('longitude', 'latitude')
    
class Provider(models.Model):
  npi = models.IntegerField(unique = True)
  last_name = models.CharField(max_length = 70)
  first_name = models.CharField(max_length = 20)
  middle_initial = models.CharField(max_length = 1)
  credentials = models.CharField(max_length = 20)
  gender = models.CharField(max_length = 1)
  is_organization = models.BooleanField()
  location = models.ForeignKey(Location)
  street2 = models.CharField(max_length = 55)
  medicare_participant = models.BooleanField()
  at_facility = models.BooleanField()
  expensiveness = models.FloatField()

class Procedure(models.Model):
  descriptor = models.ForeignKey(ProcedureDescriptor)
  provider = models.ForeignKey(Provider)
  year = models.IntegerField()
  procedure_count = models.IntegerField()
  beneficiary_count = models.IntegerField()
  line_service_count = models.FloatField()
  allowed_avg = models.FloatField()
  allowed_std = models.FloatField()
  submitted_avg = models.FloatField()
  submitted_std = models.FloatField()
  payed_avg = models.FloatField()
  payed_std = models.FloatField()
  class Meta:
    unique_together = ('descriptor', 'provider', 'year')
  
  
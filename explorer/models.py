from django.db import models

class ProcedureDescriptor(models.Model):
  code = models.CharField(max_length = 5, unique = True)
  descriptor = models.CharField(max_length = 256)

class Provider(models.Model):
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
  
#class Procedure(models.Model):
#  allowed_amount = models.FloatField()
#  descriptor = models.ForeignKey(ProcedureDescriptor)
#  provider = models.ForeignKey(Provider)
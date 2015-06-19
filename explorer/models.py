from django.db import models

class ProcedureDescriptor(models.Model):
  code = models.CharField(max_length = 5, unique = True)
  descriptor = models.CharField(max_length = 256)

class Provider(models.Model):
  last_name = models.CharField(max_length = 20)
  first_name = models.CharField(max_length = 20)
  address1 = models.CharField(max_length = 50)
  
class Procedure(models.Model):
  allowed_amount = models.FloatField()
  descriptor = models.ForeignKey(ProcedureDescriptor)
  provider = models.ForeignKey(Provider)
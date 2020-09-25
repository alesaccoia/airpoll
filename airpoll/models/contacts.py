from django.db import models

class Contact(models.Model):
    contact_name = models.CharField(max_length=200)
    contact_surname = models.CharField(max_length=200)
    
    SEX_CHOICES = (
        ('F', 'Female',),
        ('M', 'Male',),
        ('U', 'Unspecified',),
    )
    gender = models.CharField(
      max_length=1,
      choices=SEX_CHOICES,
    )
    
    email = models.CharField(max_length=128)
    phone = models.CharField(max_length=50)
    birth_date = models.DateField('Date of birth')
    tax_code = models.CharField(max_length=16)    
    r_address_is_validated = models.BooleanField('Residence address is validated', default = False)
    r_route = models.CharField(max_length = 200, blank=True, null=True)
    r_street_number = models.CharField(max_length = 200, blank=True, null=True)
    r_locality = models.CharField(max_length = 200, blank=True, null=True)
    r_administrative_area_level_3 = models.CharField(max_length = 200, blank=True, null=True)	
    r_administrative_area_level_2 = models.CharField(max_length = 200, blank=True, null=True)
    r_administrative_area_level_1 = models.CharField(max_length = 200, blank=True, null=True)
    r_country = models.CharField(max_length = 200, blank=True, null=True)
    r_postal_code = models.CharField(max_length = 200, blank=True, null=True)
    r_lat = models.DecimalField(decimal_places = 6, max_digits = 9, blank=True, null=True)
    r_lon = models.DecimalField(decimal_places = 6, max_digits = 9, blank=True, null=True)

class Interviewer(models.Model):
	contact = models.OneToOneField (Contact, on_delete=models.CASCADE, primary_key=True)

class Client(models.Model):
  name = models.CharField(max_length=200)
  contact = models.OneToOneField (Contact, on_delete=models.CASCADE, null=True, blank=True)

  def __str__(self):
    return self.name

class Interviewee(models.Model):
	contact = models.OneToOneField (Contact, on_delete=models.CASCADE, primary_key=True)

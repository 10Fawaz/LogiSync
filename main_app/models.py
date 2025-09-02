from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.
# -------------------------------------------------------------- Profile --------------------------------------------------------------
class Profile(models.Model):
    ROLE=[('supervisor', 'Supervisor'),('driver', 'Driver')]
    # ROLE=[('supervisor', 'driver')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# -------------------------------------------------------------- Container --------------------------------------------------------------
class Container(models.Model):
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    description = models.TextField(max_length=255)
    weight_capacity = models.FloatField(default=0)
    currnt_weight_capacity = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=50)  

    transport = models.ForeignKey('Transport', on_delete=models.SET_NULL, null=True, blank=True)
    inTrancport = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('container_detail', kwargs={'container_id': self.id})
    
    def __str__(self):
        return f"Container {self.code or self.id}"
    

class Package(models.Model):
    code=models.CharField(max_length=20)
    owner=models.CharField(max_length=50)
    description=models.TextField(max_length=250)
    price=models.IntegerField()
    weight=models.FloatField()
    receivedDate=models.DateField()
    container = models.ForeignKey(Container, on_delete=models.SET_NULL, null=True, blank=True)
    inContainer=models.BooleanField(default=False)
    
# -------------------------------------------------------------- TransportType --------------------------------------------------------------
class TransportType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('packages_detail', kwargs={'pk': self.id})  


# -------------------------------------------------------------- Destination --------------------------------------------------------------
class Destination(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, db_index=True, blank=True)

    def __str__(self):
        return self.name


# -------------------------------------------------------------- Source --------------------------------------------------------------
class Source(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, db_index=True, blank=True)

    def __str__(self):
        return self.name


# -------------------------------------------------------------- Transport --------------------------------------------------------------
class Transport(models.Model):
    name = models.CharField(max_length=100)
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.ForeignKey(TransportType, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    currnt_capacity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='main_app/static/uploads/', default="")
    description = models.TextField(max_length=250)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True, db_index=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('transport_detail', kwargs={'transport_id': self.id})
        


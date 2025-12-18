from django.db import models

# Create your models here.

from django.db import models

class Users(models.Model):
    customer_name = models.CharField(max_length=100)
    software_name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    db_name = models.CharField(max_length=100)
    db_username = models.CharField(max_length=100)
    db_pass = models.CharField(max_length=255)

    def __str__(self):
        return self.customer_name

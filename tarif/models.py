from django.db import models

# Create your models here.
class Tarif(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    img = models.ImageField()
    icon = models.ImageField()

    def __str__(self):
        return self.name
from django.db import models
from userconf.models import User
from tarif.models import Subscription

# Create your models here.
class SubRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    

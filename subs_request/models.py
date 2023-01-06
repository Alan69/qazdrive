from django.db import models
from userconf.models import User
from tarif.models import Subscription

# Create your models here.
class SubRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    subscription_name = models.CharField(max_length=255, null=True, blank=True)
    # approve = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return str(self.user.email)
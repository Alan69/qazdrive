from django.db import models

# Create your models here.
class Tarif(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    amount = models.IntegerField(verbose_name="Срок тарифа")
    kaspi_post_url = models.CharField(max_length=100)
    icon_tag = models.CharField(max_length=255, default="<i class='ri-rocket-2-fill'></i>")

    def __str__(self):
        return self.name

class Subscription(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    amout = models.IntegerField(verbose_name="Срок подписки")
    kaspi_post_url = models.CharField(max_length=100)
    user_amount = models.IntegerField(verbose_name="количество пользователей")
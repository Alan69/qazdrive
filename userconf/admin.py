from django.contrib import admin
from .models import User
# Register your models here.

class AccountsUserAdmin(admin.ModelAdmin):
    list_display = ('id','email','first_name', 'last_name','city', 'tarif_name', 'pddtest_pass')

admin.site.register(User, AccountsUserAdmin)
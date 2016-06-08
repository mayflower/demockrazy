from django.contrib import admin

# Register your models here.
from .models import Poll

admin.site.register(Poll)

from django.contrib import admin

from .models import Poll, SingleChoiceQuestion, SingleChoiceChoice

admin.site.register(Poll)
admin.site.register(SingleChoiceQuestion)
admin.site.register(SingleChoiceChoice)
# Register your models here.

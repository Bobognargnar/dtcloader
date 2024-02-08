from django.contrib import admin

# Register your models here.
from .models import Reading,File,Mpan,Meter

admin.site.register([Reading, File, Mpan, Meter])
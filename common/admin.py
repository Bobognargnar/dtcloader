from django.contrib import admin
from django.db.models import QuerySet

# Register your models here.
from .models import Reading,File,Mpan,Meter
import re
from traceback import format_exc

class FilteringAdmin(admin.ModelAdmin):
    list_display = ["reading","date","get_file","get_meter","get_mpan"]
    search_fields  = ["reading"]
    list_filter = ["reading"]
    search_help_text = "Seach here using the following fields in the database: meter, mpan, filename"
    
    @admin.display(ordering='file__filename', description='Filename')
    def get_file(self, obj):
        return obj.file_id.filename

    @admin.display(ordering='meter__serial', description='Meter')
    def get_meter(self, obj):
        return obj.meter_id.serial

    @admin.display(ordering='mpan__core', description='MPAN')
    def get_mpan(self, obj):
        return obj.mpan_id.core

    def get_search_results(self, request, queryset, search_term):
        # I spent too much time trying to make the basic search work.
        # I'm writing my own, with just support for filename, MPAN and meter serial number
        try:
            pattern = r'(\w+)\s*([=><!]+)\s*(?:("[^"]*")|(\w+\.\w+))(?:\s*([&|])|$)'
            regex = re.compile(pattern)
            matches = regex.findall(search_term)
            print(search_term)

            if len(search_term)>0 and len(matches) == 0: 
                return Reading.objects.none(), False

            for match in matches:
                match = [m for m in match if m!='']
                print(match)
                field_name, operator, value = match[0:3]

                if field_name == "meter":
                    new_queryset = queryset.filter(meter_id__serial=value)
                elif field_name == "mpan":
                    new_queryset = queryset.filter(mpan_id__core=value)
                elif field_name == "filename":
                    new_queryset = queryset.filter(file_id__filename=value)
                else:
                    new_queryset = getattr(queryset, 'filter')(**{field_name: value})
                
                queryset = new_queryset

                # TODO: add support for boolean algebra
                # if conjunction == '&':
                #     queryset = queryset.union(new_queryset)
                # if conjunction == '|':
                #     queryset = queryset | new_queryset
        except Exception as e:
            print(format_exc())
            return queryset, False
    
        return queryset, False
    

admin.site.register([File,Mpan, Meter])

admin.site.register([Reading], FilteringAdmin)

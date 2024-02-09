from django.contrib import admin

# Register your models here.
from .models import Reading,File,Mpan,Meter
import re
from traceback import format_exc

class FilteringAdmin(admin.ModelAdmin):
    list_display = ["reading","date","get_file","get_meter","get_mpan"]
    #list_display = ["reading","date","file_id","meter_id","mpan_id"]
    search_fields  = ["reading"]
    list_filter = ["reading"]
    search_help_text = "Seach here using the following fields in the database:"
    for searchField in search_fields:
        search_help_text += Reading._meta.get_field(searchField).verbose_name

    @admin.display(ordering='file__filename', description='File')
    def get_file(self, obj):
        return obj.file_id.filename

    @admin.display(ordering='meter__serial', description='Meter')
    def get_meter(self, obj):
        return obj.meter_id.serial

    @admin.display(ordering='mpan__core', description='Mpan')
    def get_mpan(self, obj):
        return obj.mpan_id.core

    def get_search_results(self, request, queryset, search_term):
        # I spent too much time trying to make the basic search work.
        # I'm writing my own, with just support for MPAN and meter serial number
        try:
            pattern = r'(\w+)\s*([=><!]+)\s*(\w+)(?:\s*([&|])|$)'
            regex = re.compile(pattern)
            matches = regex.findall(search_term)

            for match in matches:
                print(match)
                field_name, operator, value, conjunction = match[0:4]

                if field_name == "meter":
                    new_queryset = queryset.filter(meter_id__serial=value)
                elif field_name == "mpan":
                    new_queryset = queryset.filter(mpan_id__core=value)
                else:
                    new_queryset = getattr(queryset, 'filter')(**{field_name: value})
                
                queryset = new_queryset

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

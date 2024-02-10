from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import File,Meter,Mpan,Reading
from .utils import DataFlowParserFactory
from django.core.files.storage import default_storage
from django.db import IntegrityError
from os import path
import os
from io import BufferedReader
from django.db import models
from traceback import format_exc


@receiver(pre_save, sender=File)
def file_insert_validation(sender, instance, **kwargs):
    # Validate data flow file before insert action
    try:
        if instance.filename == '':
            instance.filename = os.path.basename(instance.file.url)

        if File.objects.filter(filename=instance.filename).exists():
            raise IntegrityError("Duplicated file")

        extension = path.splitext(instance.file.name)[1]
        if extension != ".uff": 
            raise IntegrityError("Unsupported file extension. Aborting save operation.")
        
    except Exception:
        raise
    


@receiver(post_save, sender=File)
def trigger_file_processing(sender, instance, created, **kwargs):
    if created:

        with default_storage.open(instance.file.name, 'rb') as file:
            file_content = file.read().decode().split("\n")

        flow_parser = DataFlowParserFactory().get_parser(file_content)
        readings = flow_parser.process(file_content)

        for reading_dict in readings:
            # Populate table MPAN
            values = {'core': reading_dict["mpan"]}
            mpan, created = Mpan.objects.update_or_create(defaults=values, **values)
            if created: print(f"New MPAN added: {values}")

            # Populate table Meter
            values = {'serial': reading_dict["meter"]}
            meter, created = Meter.objects.update_or_create(defaults=values, **values)
            if created: print(f"New Meter added: {values}")

            # Populate table Readings
            values = {
                'reading': reading_dict["value"],
                'date': reading_dict["date"],
                'file_id': File(id = instance.id),
                'mpan_id': mpan,
                'meter_id': meter,
                }
            reading, created = Reading.objects.update_or_create(defaults=values, **values)
            if created: 
                print(f"New Reading added: {values['reading']} {values['date'].strftime('%Y-%m-%d %H:%M:%S')}")
        

        print()
        
    pass

@receiver(post_delete, sender=File)
def upload_cleanup(sender, instance, **kwargs):
    # Remove file from upload folder after deletion.
    # ! File removal does not work due to file lock. I expect it to work on unix environments.
    try:
        if os.path.exists(instance.file.file.name):
            os.remove(instance.file.file.name)
    except Exception as e:
        print(format_exc())
    pass

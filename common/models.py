from django.db import models

# Shared models for DTC data flows



class File(models.Model):
    """Models data flow files

    Attributes:
        file (file): Uploaded flow file
        filename (str): Filename string with extension
    """
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='uploads/', unique=True)
    filename = models.CharField(max_length=200, blank=True)

class Meter(models.Model):
    serial = models.CharField(max_length=10)

class Mpan(models.Model):
    core = models.IntegerField()

class Reading(models.Model):
    """Models meter readings from any flow source.

    These readings are currently modeled on the D0010 flow
    and are expected to be associated to a specific flow file,
    a specific MPAN and a specific meter.

    Attributes:
        reading (float): Numerical value of the reading
        date (datetime): Date of the reading
        file_id: Reference to File table. The file of origin of this reading.
        mpan_id: Reference to Mpan table. The MPAN associated with this reading.
        meter_id: Reference to Meter table. The meter associated with this reading.
    """
    reading = models.DecimalField(max_digits=9, decimal_places=1)
    date = models.DateTimeField()
    
    # We CASCADE becase we don't want orphaned readings
    file_id = models.ForeignKey(File, on_delete=models.CASCADE,to_field="id")
    mpan_id = models.ForeignKey(Mpan, on_delete=models.CASCADE)
    meter_id = models.ForeignKey(Meter, on_delete=models.CASCADE)

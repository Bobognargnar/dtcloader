# serializers.py
from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    # class Meta:
    #     model = File
    #     fields = ['file']

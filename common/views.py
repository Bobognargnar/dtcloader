from django.http import HttpResponse

# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import File
from .serializers import FileSerializer


def index(request):
    return HttpResponse("The common index.")

class FileUploadAPIView(APIView):
    def post(self, request, format=None):
        # data = request.data
        data = request.read()
        serializer = FileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
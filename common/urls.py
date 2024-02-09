from django.urls import path
from .views import FileUploadAPIView

from . import views

from django.urls import path, include
from rest_framework import routers



urlpatterns = [
        path("", views.index, name="index"),
        path('api/upload/', FileUploadAPIView.as_view(), name='file-upload'),
]

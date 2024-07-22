from rest_framework import viewsets
from .serializers import *

## private apis

class SupportViewSet(viewsets.ModelViewSet):
    serializer_class = SupportSerializer
    queryset = Support.objects.filter(status='Active').order_by("-id")
    filterset_fields = ['title','status']
    search_fields=['title','description']
    http_method_names = ['get', 'post', 'patch']

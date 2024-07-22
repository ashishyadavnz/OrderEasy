from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import *
from .models import *

## public apis 

class LanguageView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Language.objects.filter(status='Active')
	serializer_class = LanguageSerializer
	filterset_fields = ['name','code','status']
	search_fields=['name','code','pattern']
	http_method_names = ['get']

class ContinentView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Continent.objects.filter(status='Active')
	serializer_class = ContinentSerializer
	filterset_fields = ['name','area','population','status']
	search_fields=['name']
	http_method_names = ['get']

class CountryView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Country.objects.filter(status='Active')
	serializer_class = CountrySerializer
	filterset_fields = ['name','code','code2','code3','capital','status']
	search_fields=['name','local','capital','continent__name']
	http_method_names = ['get']

class StateView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = State.objects.filter(status='Active')
	serializer_class = StateSerializer
	filterset_fields = ['name','country','capital','status']
	search_fields=['name','country__name','capital','local']
	http_method_names = ['get']

class TimezoneView(viewsets.ModelViewSet):
	permission_classes = ((AllowAny,))
	queryset = Timezone.objects.filter(status='Active')
	serializer_class = TimezoneSerializer
	filterset_fields = ['name','country','city','utc','status']
	search_fields=['name','country__name','display','city']
	http_method_names = ['get']

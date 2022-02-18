import imp
import django_filters

from .models import Ad

class AdFilter(django_filters.FilterSet):
    class Meta:
        model = Ad
        fields = {
            'gender': ['exact'],
            'service_type': ['exact'],
            'urgency': ['exact'],
            'address__details': ['icontains'],
            'start_time': ['lt', 'gt'],
            'end_time': ['lt', 'gt'],
        }

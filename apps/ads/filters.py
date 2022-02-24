import django_filters

from apps.users.models import Nurse

from .models import Ad

class AdFilter(django_filters.FilterSet):
    class Meta:
        model = Ad  
        fields = {
            'gender': ['exact'],
            'service_type': ['exact'],
            'urgency': ['exact'],
            'address__details': ['icontains'],
            'description': ['icontains'],
            'start_time': ['lt', 'gt'],
            'end_time': ['lt', 'gt'],
        }

class AdFilterForAdmin(AdFilter):
    nursead__nurse = django_filters.ModelChoiceFilter(field_name='nursead__nurse', queryset=Nurse.objects.all(), label="Nurse")

    class Meta:
        model = Ad
        fields = {
            'accepted': ['exact'],
            'nursead__nurse': ['exact'],
            **AdFilter.Meta.fields,
        }

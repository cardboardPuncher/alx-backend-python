from django_filters import rest_framework as filters
import django_filters
from .models import Message

class MessageFilter(filters.FilterSet):
    time_period = django_filters.DateTimeFromToRangeFilter(field_name='sent_at')
    class Meta:
        model = Message
        fields = {
            'sender__username':['iexact'],
            'sender__email':['iexact'],
            # 'sent_at':['exact','year__gt', 'year__lt']
        }
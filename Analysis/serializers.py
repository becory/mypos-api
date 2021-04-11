from collections import OrderedDict

from rest_framework import serializers


# Create your serializers here.
class AnalysisSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.DecimalField(max_digits=8, decimal_places=2)


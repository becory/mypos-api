from rest_framework import serializers
from .models import Customer


# Create your serializers here.
class CustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=10)
    phone = serializers.CharField(max_length=15)
    gender = serializers.CharField()
    age = serializers.IntegerField()


class CustomerCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)
    phone = serializers.CharField(max_length=15)
    passcode = serializers.CharField(max_length=10, required=False)
    genderChoices = (('M', 'Female'), ('F', 'Female'), ('O', 'Other'),)
    gender = serializers.ChoiceField(choices=genderChoices)
    age = serializers.IntegerField()

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Customer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        instance.save()
        return instance

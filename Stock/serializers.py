from rest_framework import serializers
from .models import Label, Unit, Material, Stock


class NamePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def display_value(self, instance):
        return '%s' % (instance.name)


# Create your serializers here.
class LabelSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=10)


class LabelCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Label.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        return instance.save()


class UnitSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=10)
    sign = serializers.CharField(max_length=4)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Unit.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        return instance.save()


class MaterialSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    label = LabelSerializer(many=False)
    name = serializers.CharField(max_length=50)
    brand = serializers.CharField(max_length=50)
    unit = UnitSerializer()


class MaterialCreateSerializer(serializers.Serializer):
    label = NamePrimaryKeyRelatedField(queryset=Label.objects.all(), default=Label(pk=1))
    name = serializers.CharField(max_length=50)
    brand = serializers.CharField(max_length=50)
    unit = NamePrimaryKeyRelatedField(queryset=Unit.objects.all(), default=Unit(pk=1))

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Material.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        return instance.save()


class StockSerializer(serializers.Serializer):
    stockDate = serializers.DateField()
    expiryDate = serializers.DateField()
    material = NamePrimaryKeyRelatedField(queryset=Material.objects.all())
    stock = serializers.DecimalField(decimal_places=2, max_digits=8)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Stock.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        return instance.save()

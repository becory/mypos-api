from collections import OrderedDict

from rest_framework import serializers


# Create your serializers here.
class ColumnsSerializer(serializers.Serializer):
    label = serializers.CharField()
    field = serializers.CharField()
    type = serializers.CharField(required=False)
    inputType = serializers.CharField(required=False)
    dateInputFormat = serializers.CharField(required=False)
    dateOutputFormat = serializers.CharField(required=False)
    formatFn = serializers.CharField(required=False)
    fixed = serializers.CharField(required=False)
    width = serializers.CharField(required=False)


class SubSelectionSerializer(serializers.Serializer):
    value = serializers.IntegerField(source='id')
    label = serializers.CharField(source='name')
    unit = serializers.SerializerMethodField(allow_null=True, read_only=True, required=False)

    def get_unit(self, obj):
        if getattr(obj, 'unit', False):
            return obj.unit.sign
        else:
            return None

    def to_representation(self, instance):
        result = super(SubSelectionSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None])


class SelectionSerializer(serializers.Serializer):
    value = serializers.IntegerField(source='id')
    label = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField(allow_null=True, read_only=True, required=False)

    def get_label(self, obj):
        if "selection" in self.context:
            return getattr(obj, self.context["selection"], None)
        else:
            return None

    def get_children(self, obj):
        if "source" in self.context:
            if len(getattr(obj, self.context["source"]).all()) > 0:
                return SubSelectionSerializer(instance=getattr(obj, self.context["source"]).all(), many=True, read_only=True).data
        else:
            return None
    #
    # def to_representation(self, instance):
    #     result = super(SelectionSerializer, self).to_representation(instance)
    #     return OrderedDict(
    #         [(key, result[key]) for key in result if result[key] is not None])

from rest_framework import serializers

from Setting.models import Setting


class SettingUpdateSerializers(serializers.Serializer):
    key = serializers.CharField(max_length=20)
    value = serializers.JSONField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        return Setting.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            setattr(instance, item, validated_data[item])
        instance.save()
        return instance

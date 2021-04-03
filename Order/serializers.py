import json

from rest_framework import serializers
from Customer.serializers import CustomerSerializer
from Menu.models import MenuItem
from Menu.serializers import MenuItemSerializer, MenuItemDashboardSerializer
from .models import Status, Order, OrderDetail, Cook
from Customer.models import Customer


# Create your serializers here.
class OrderStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=10)
    className = serializers.CharField(max_length=10)
    icon = serializers.CharField(max_length=50)
    orderNo = serializers.IntegerField()
    visible = serializers.BooleanField()

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Status.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        instance.save()
        return instance


class CookSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    label = serializers.CharField(max_length=10, allow_null=True)
    className = serializers.CharField(max_length=10)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return Cook.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        instance.save()
        return instance



class OrderDetailFromOrderSerializer(serializers.Serializer):
    menu = serializers.PrimaryKeyRelatedField(source="menuItem.menu", read_only=True)
    menuItem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    # transactionItem = serializers.CharField(max_length=30, required=False)
    # transactionCost = serializers.CharField(max_length=50, required=False)
    cook = CookSerializer()
    count = serializers.IntegerField()
    remark = serializers.CharField(max_length=100, allow_null=True)


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = OrderStatusSerializer()
    customer = CustomerSerializer()
    checkOut = serializers.BooleanField(default=False)
    orderID = serializers.IntegerField()
    desk = serializers.IntegerField()
    orderFromChoices = (('C', 'Customer'), ('S', 'Store'), ('F', 'FoodPanda'), ('U', 'UberEats'),)
    orderFrom = serializers.ChoiceField(choices=orderFromChoices)
    orderDetails = OrderDetailFromOrderSerializer(many=True)


class TimelineSerializer(serializers.Serializer):
    createDateTime = serializers.DateTimeField(required=False, read_only=True)
    confirmDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    checkoutDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    finishDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    pickupDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)


class OrderCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), default=1, required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), default=1, required=False)
    checkOut = serializers.BooleanField(default=False)
    orderID = serializers.IntegerField()
    desk = serializers.IntegerField(default=0, required=False)
    # createDateTime = serializers.DateTimeField(required=False, read_only=True)
    # confirmDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    # checkoutDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    # finishDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    # pickupDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
    orderFromChoices = (('C', 'Customer'), ('S', 'Store'), ('F', 'FoodPanda'), ('U', 'UberEats'),)
    orderFrom = serializers.ChoiceField(choices=orderFromChoices)
    orderDetails = OrderDetailFromOrderSerializer(many=True)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        if 'orderDetails' in validated_data:
            order_detail = validated_data.pop('orderDetails')
        instance = Order.objects.create(**validated_data)
        if order_detail:
            print([getattr(item['menuItem'], 'name') for item in order_detail])
            order_detail = map(lambda item: OrderDetail(order=instance, **dict(item),
                                                        **{"transactionItem": getattr(item['menuItem'], 'name'),
                                                           "transactionCost": getattr(item['menuItem'], 'price')}),
                               order_detail)
            OrderDetail.objects.bulk_create(order_detail)
            instance.orderDetails.set(order_detail)
        return instance

    def update(self, instance, validated_data):
        if not self.partial:
            if 'orderDetails' in validated_data:
                order_detail = validated_data.pop('orderDetails')
                instance.orderDetails.all().delete()
                order_detail = map(lambda item: OrderDetail(order=instance, **dict(item),
                                                            **{"transactionItem": getattr(item['menuItem'], 'name'),
                                                               "transactionCost": getattr(item['menuItem'], 'price')}),
                                   order_detail)
                OrderDetail.objects.bulk_create(order_detail)
            else:
                instance.orderDetails.all().delete()
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        instance.save()
        return instance


class OrderDetailSerializer(serializers.Serializer):
    menuItem = MenuItemSerializer()
    transactionItem = serializers.CharField(max_length=30)
    transactionCost = serializers.CharField(max_length=50)
    cook = CookSerializer(allow_null=True)
    count = serializers.IntegerField()
    remark = serializers.CharField(max_length=100, allow_null=True)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        return OrderDetail.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for item in validated_data:
            if item not in self.UPDATE_FORBIDDEN:
                setattr(instance, item, validated_data[item])
        instance.save()
        return instance


class OrderRetrieveSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = OrderStatusSerializer()
    customer = CustomerSerializer()
    checkOut = serializers.BooleanField(default=False)
    orderID = serializers.IntegerField()
    desk = serializers.IntegerField()
    orderFromChoices = (('C', 'Customer'), ('S', 'Store'), ('F', 'FoodPanda'), ('U', 'UberEats'),)
    orderFrom = serializers.ChoiceField(choices=orderFromChoices)
    orderDetails = OrderDetailSerializer(many=True)
    timeline = serializers.SerializerMethodField()

    def get_timeline(self, obj):
        dateField = ['createDateTime', 'confirmDateTime', 'checkoutDateTime', 'finishDateTime', 'pickupDateTime']
        return [{'content': item, 'timestamp': getattr(obj, item)} for item in dateField]


class OrderDashboardDetailSerializer(serializers.Serializer):
    menuItem = MenuItemDashboardSerializer()
    transactionItem = serializers.CharField(max_length=30)
    transactionCost = serializers.CharField(max_length=50)
    cook = CookSerializer(allow_null=True)
    count = serializers.IntegerField()
    remark = serializers.CharField(max_length=100, allow_null=True)


class OrderDashboardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    # status = OrderStatusSerializer()
    customer = CustomerSerializer()
    checkOut = serializers.BooleanField(default=False)
    orderID = serializers.IntegerField()
    desk = serializers.IntegerField()
    orderFromChoices = (('C', 'Customer'), ('S', 'Store'), ('F', 'FoodPanda'), ('U', 'UberEats'),)
    orderFrom = serializers.ChoiceField(choices=orderFromChoices)
    orderDetails = OrderDashboardDetailSerializer(many=True)

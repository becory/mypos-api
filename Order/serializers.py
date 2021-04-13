import json
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from Customer.serializers import CustomerSerializer
from Menu.models import MenuItem
from Menu.serializers import MenuItemSerializer, MenuItemDashboardSerializer
from Stock.models import Stock
from .models import Status, Order, OrderDetail, Cook
from Customer.models import Customer
import datetime


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


class OrderCookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField(read_only=True)
    className = serializers.CharField(read_only=True)


class OrderDetailFromOrderSerializer(serializers.Serializer):
    menu = serializers.PrimaryKeyRelatedField(source="menuItem.menu", read_only=True)
    menuItem = MenuItemDashboardSerializer()
    transactionItem = serializers.CharField(max_length=30, required=False)
    transactionCost = serializers.CharField(max_length=50, required=False)
    cook = CookSerializer(allow_null=True, required=False)
    count = serializers.IntegerField()
    remark = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)


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
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(), default=Status.objects.get(id=1),
                                                required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), default=Customer.objects.get(id=1),
                                                  required=False)
    checkOut = serializers.BooleanField(default=False)
    orderID = serializers.IntegerField(required=False)
    desk = serializers.IntegerField(default=0, required=False)
    orderFromChoices = (('C', 'Customer'), ('S', 'Store'), ('F', 'FoodPanda'), ('U', 'UberEats'),)
    orderFrom = serializers.ChoiceField(choices=orderFromChoices, required=False)
    orderDetails = OrderDetailFromOrderSerializer(many=True)

    UPDATE_FORBIDDEN = []

    def create(self, validated_data):
        with transaction.atomic():
            total = 0
            if 'orderDetails' in validated_data:
                order_detail = validated_data.pop('orderDetails')
            instance = Order(**validated_data)
            today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            try:
                last_order_id = Order.objects.filter(createDateTime__range=(today_min, today_max)).latest(
                    'orderID').orderID
                if last_order_id is None:
                    last_order_id = 0
            except Order.DoesNotExist:
                last_order_id = 0
            instance.orderID = last_order_id + 1
            instance.save()
            if order_detail:
                order_list = []
                stock_detail = []
                for item in order_detail:
                    total += item['menuItem']['price'] * item['count']
                    order_list.append(OrderDetail(order=instance,
                                                  menuItem=MenuItem.objects.get(id=item['menuItem']['id']),
                                                  **
                                                  {'cook': Cook.objects.get(label=item['cook']['label'])
                                                  if item['cook'] is not None and 'label' in item['cook'] else None}
                                                  ,
                                                  **{"count": item['count'],
                                                     "transactionItem": item['menuItem']['name'],
                                                     "transactionCost": item['menuItem']['price']}))
                    # 庫存儲存
                    for subItem in MenuItem.objects.get(id=item['menuItem']['id']).recipes.all():
                        stock_detail.append(Stock(material=subItem.material,
                                                  stock=-subItem.count * item['count'],
                                                  stockDate=instance.createDateTime))
                    for menuSet in MenuItem.objects.get(id=item['menuItem']['id']).menuSet.all():
                        for subItem in menuSet.recipes.all():
                            stock_detail.append(Stock(material=subItem.material,
                                                      stock=-subItem.count * item['count'],
                                                      stockDate=instance.createDateTime))
                OrderDetail.objects.bulk_create(order_list)
                Stock.objects.bulk_create(stock_detail)
                instance.orderDetails.set(order_list)
                if 'checkOut' in validated_data and validated_data['checkOut']:
                    instance.checkOutTotal = total
                    instance.checkoutDateTime = timezone.now()
                else:
                    instance.checkOutTotal = None
                    instance.checkoutDateTime = None
                instance.save()
        return instance

    def update(self, instance, validated_data):
        with transaction.atomic():
            if not self.partial:
                # 庫存清除
                for item in instance.orderDetails.all():
                    for subItem in item.menuItem.recipes.all():
                        Stock.objects.filter(material=subItem.material, stock=-subItem.count * item.count,
                                             stockDate=instance.createDateTime).last().delete()
                    for menuItem in item.menuItem.menuSet.all():
                        for subItem in menuItem.recipes.all():
                            Stock.objects.filter(material=subItem.material,
                                                 stock=-subItem.count * item.count,
                                                 stockDate=instance.createDateTime).last().delete()
                instance.orderDetails.all().delete()

                if validated_data['orderDetails']:
                    order_detail = validated_data.pop('orderDetails')
                    order_list = []
                    stock_detail = []
                    total = 0
                    for item in order_detail:
                        total += item['menuItem']['price'] * item['count']
                        order_list.append(OrderDetail(order=instance,
                                                      menuItem=MenuItem.objects.get(id=item['menuItem']['id']),
                                                      **
                                                      {'cook': Cook.objects.get(id=item['cook']['id'])
                                                      if item['cook'] is not None and 'id' in item['cook'] else None}
                                                      ,
                                                      **{"count": item['count'],
                                                         "transactionItem": item['menuItem']['name'],
                                                         "transactionCost": item['menuItem']['price']}))
                        # 庫存儲存
                        for subItem in MenuItem.objects.get(id=item['menuItem']['id']).recipes.all():
                            stock_detail.append(Stock(material=subItem.material,
                                                      stock=-subItem.count * item['count'],
                                                      stockDate=instance.createDateTime))
                        for menuSet in MenuItem.objects.get(id=item['menuItem']['id']).menuSet.all():
                            for subItem in menuSet.recipes.all():
                                stock_detail.append(Stock(material=subItem.material,
                                                          stock=-subItem.count * item['count'],
                                                          stockDate=instance.createDateTime))
                    OrderDetail.objects.bulk_create(order_list)
                    Stock.objects.bulk_create(stock_detail)
                    instance.orderDetails.set(order_list)
                    if 'checkOut' in validated_data and validated_data['checkOut']:
                        instance.checkOutTotal = total
                    else:
                        instance.checkOutTotal = None

            for item in validated_data:
                if item not in self.UPDATE_FORBIDDEN:
                    setattr(instance, item, validated_data[item])
                    # createDateTime = serializers.DateTimeField(required=False, read_only=True)
                    # confirmDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
                    # finishDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
                    # pickupDateTime = serializers.DateTimeField(allow_null=True, required=False, read_only=True)
            if 'checkOut' in validated_data:
                if validated_data['checkOut']:
                    instance.checkoutDateTime = timezone.now()
                else:
                    instance.checkoutDateTime = None

            if validated_data['status'].id == 2:
                instance.confirmDateTime = timezone.now()
            elif validated_data['status'].id < 2:
                instance.confirmDateTime = None

            if validated_data['status'].id == 3:
                instance.finishDateTime = timezone.now()
            elif validated_data['status'].id < 3:
                instance.finishDateTime = None

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
    checkOutTotal = serializers.DecimalField(required=False, decimal_places=2, max_digits=8)


class OrderEditSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    customer = CustomerSerializer()
    checkOut = serializers.BooleanField(default=False)
    orderID = serializers.IntegerField()
    desk = serializers.IntegerField()
    orderFromChoices = (('C', 'Customer'), ('S', 'Store'), ('F', 'FoodPanda'), ('U', 'UberEats'),)
    orderFrom = serializers.ChoiceField(choices=orderFromChoices)
    orderDetails = OrderDetailSerializer(many=True)

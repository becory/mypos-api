import datetime

from django.db import transaction
from rest_framework import permissions
from rest_framework.decorators import action, authentication_classes

from Stock.models import Stock
from .models import Status, Order, Cook, OrderDetail
from .serializers import OrderStatusSerializer, OrderSerializer, OrderCreateSerializer, CookSerializer, \
    OrderDetailSerializer, OrderRetrieveSerializer, OrderDashboardSerializer, OrderEditSerializer
from patches.viewset import BasicViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Create your views here.


class StatusViewSet(BasicViewSet):
    model = Status
    queryset = model.objects.all()
    serializer_class = OrderStatusSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['id', 'name', 'className', 'orderNo', 'visible']
    search_fields = ['id', 'name', 'className', 'orderNo', 'visible']
    modelName = Status.__name__
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @swagger_auto_schema(operation_summary='Get Status List',
                         operation_description='Get Status List',
                         manual_parameters=[
                             openapi.Parameter(
                                 name='columns',
                                 in_=openapi.IN_QUERY,
                                 description='columns',
                                 type=openapi.TYPE_BOOLEAN
                             )
                         ],
                         )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        request_body=serializer_class,
        responses={404: 'not found'}
    )
    def create(self, request):
        return super().create(request)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(instance)
        data = serializer.data
        self.get_queryset()
        return Response(data)


class OrderViewSet(BasicViewSet):
    model = Order
    queryset = model.objects.all()
    serializer_class = OrderSerializer
    retrieve_serializer_class = OrderRetrieveSerializer
    create_serializer_class = OrderCreateSerializer
    update_serializer_class = OrderCreateSerializer
    partial_update_serializer_class = OrderCreateSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['id', 'customer__name', 'status__name', 'checkOutTotal', 'orderID', 'desk', 'orderFrom',
                       'orderDetails__menuItem__name']
    search_fields = ['id', 'customer__name', 'status__name', 'checkOutTotal', 'orderID', 'desk', 'orderFrom',
                     'orderDetails__menuItem__name']
    modelName = Order.__name__
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


    @swagger_auto_schema(operation_summary='Get Order List',
                         operation_description='Get Order List',
                         manual_parameters=[
                             openapi.Parameter(
                                 name='columns',
                                 in_=openapi.IN_QUERY,
                                 description='columns',
                                 type=openapi.TYPE_BOOLEAN
                             )
                         ],
                         )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        request_body=serializer_class,
        responses={404: 'not found'}
    )
    def create(self, request):
        return super().create(request)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def destroy(self, request, pk=None):
        with transaction.atomic():
            instance = get_object_or_404(self.get_queryset(), id=pk)

            # ????????????
            for item in instance.orderDetails.all():
                for subItem in item.menuItem.recipes.all():
                    print(subItem.material, -subItem.count * item.count, instance.createDateTime)
                    Stock.objects.filter(material=subItem.material, stock=-subItem.count * item.count,
                                         stockDate=instance.createDateTime).last().delete()
                for menuItem in item.menuItem.menuSet.all():
                    for subItem in menuItem.recipes.all():
                        Stock.objects.filter(material=subItem.material,
                                             stock=-subItem.count * item.count,
                                             stockDate=instance.createDateTime).last().delete()
            instance.orderDetails.all().delete()
            instance.delete()
            serializer = self.serializer_class(instance)
            data = serializer.data
            self.get_queryset()
        return Response(data)

    @action(detail=False, methods=['get'])
    def Dashboard(self, request):
        result = super().filter_queryset(self.get_queryset().filter(createDateTime__gte=datetime.date.today()))
        if self.request.query_params.get('status', None) == "3":
            result = result.order_by('-orderID')[0:3]
        totalcount = result.count()
        result = super().pagination_class.paginate_queryset(queryset=result, request=request, view=self)
        serializer = OrderDashboardSerializer(result, many=True)
        data = serializer.data
        return Response({"totalCount": totalcount, "result": data})

    @action(detail=True, methods=['get'])
    def Edit(self, request, pk):
        result = get_object_or_404(self.get_queryset(), id=pk)
        serializer = OrderEditSerializer(result)
        data = serializer.data
        return Response(data)


class CookViewSet(BasicViewSet):
    model = Cook
    queryset = model.objects.all()
    serializer_class = CookSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['label', 'className']
    search_fields = ['label', 'className']
    modelName = Cook.__name__
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @swagger_auto_schema(operation_summary='Get Cook List',
                         operation_description='Get Cook List',
                         manual_parameters=[
                             openapi.Parameter(
                                 name='columns',
                                 in_=openapi.IN_QUERY,
                                 description='columns',
                                 type=openapi.TYPE_BOOLEAN
                             )
                         ],
                         )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        request_body=serializer_class,
        responses={404: 'not found'}
    )
    def create(self, request):
        return super().create(request)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(instance)
        data = serializer.data
        self.get_queryset()
        return Response(data)


class OrderDetailViewSet(BasicViewSet):
    model = OrderDetail
    queryset = model.objects.all()
    serializer_class = OrderDetailSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['name', 'customerAction', 'visible']
    search_fields = ['name', 'customerAction', 'visible']
    modelName = OrderDetail.__name__

    @swagger_auto_schema(operation_summary='Get OrderDetail List',
                         operation_description='Get OrderDetail List',
                         manual_parameters=[
                             openapi.Parameter(
                                 name='columns',
                                 in_=openapi.IN_QUERY,
                                 description='columns',
                                 type=openapi.TYPE_BOOLEAN
                             )
                         ],
                         )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        request_body=serializer_class,
        responses={404: 'not found'}
    )
    def create(self, request):
        return super().create(request)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(instance)
        data = serializer.data
        self.get_queryset()
        return Response(data)

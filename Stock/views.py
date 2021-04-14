from .models import Label, Unit, Material, Stock
from .serializers import LabelSerializer, UnitSerializer, MaterialSerializer, MaterialCreateSerializer, StockSerializer, \
    LabelCreateSerializer
from patches.viewset import BasicViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Create your views here.
dateFormatList = ['year', 'month', 'day']
timeFormatList = ['hour', 'minute', 'second']


class LabelViewSet(BasicViewSet):
    model = Label
    queryset = model.objects.all()
    serializer_class = LabelSerializer
    create_serializer_class = LabelCreateSerializer
    update_serializer_class = LabelCreateSerializer
    partial_serializer_class = LabelCreateSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['name']
    search_fields = ['name']
    modelName = Label.__name__

    @swagger_auto_schema(operation_summary='Get Label List',
                         operation_description='Get Label List',
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


class UnitViewSet(BasicViewSet):
    model = Unit
    queryset = model.objects.all()
    serializer_class = UnitSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['name', 'sign']
    search_fields = ['name', 'sign']
    modelName = Unit.__name__

    @swagger_auto_schema(operation_summary='Get Unit List',
                         operation_description='Get Unit List',
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


class MaterialViewSet(BasicViewSet):
    model = Material
    queryset = model.objects.all()
    serializer_class = MaterialSerializer
    create_serializer_class = MaterialCreateSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['name', 'label__name', 'brand', 'unit__name']
    search_fields = ['name', 'label__name', 'brand', 'unit__name']
    modelName = Material.__name__

    @swagger_auto_schema(operation_summary='Get Material List',
                         operation_description='Get Material List',
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
        request_body=create_serializer_class,
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
        request_body=create_serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=create_serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)


class StockViewSet(BasicViewSet):
    model = Stock
    queryset = model.objects.all()
    serializer_class = StockSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['stockDate', 'expiryDate', 'material__name', 'stock']
    search_fields = ['stockDate', 'expiryDate', 'material__name', 'stock']
    modelName = Stock.__name__

    @swagger_auto_schema(operation_summary='Get Stock List',
                         operation_description='Get Stock List',
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
from .models import Customer
from .serializers import CustomerSerializer, CustomerCreateSerializer
from patches.viewset import BasicViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
dateFormatList = ['year', 'month', 'day']
timeFormatList = ['hour', 'minute', 'second']


class CustomerViewSet(BasicViewSet):
    model = Customer
    queryset = model.objects.all()
    serializer_class = CustomerSerializer
    create_serializer_class = CustomerCreateSerializer
    update_serializer_class = CustomerCreateSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['name', 'phone', 'gender']
    search_fields = ['name', 'phone']
    modelName = Customer.__name__

    @swagger_auto_schema(tags=['Customer'],
                         operation_summary='Get Customer List',
                         operation_description='Get Customer List',
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

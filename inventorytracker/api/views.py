from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    SystemSerializer,
    ComponentSerializer,
    PartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PartComponentSerializer,
)

from .models import (
    System,
    Component,
    Part,
    PartComponent,
    Order,
    OrderItem,
)


# Rather than managing all urls and endpoints explicitly we can use a
# router to manage multiple endpoints and urls per class for us.
router = routers.DefaultRouter()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_page_size(self, request):
        if self.page_size_query_param:
            page_size = min(int(request.query_params.get(self.page_size_query_param, self.page_size)), self.max_page_size)
        if page_size > 0:
            return page_size
        elif page_size == 0:
            return None
        else:
            pass
        return self.page_size


class ViewSystem(viewsets.ModelViewSet):
    # pagination_class = StandardResultsSetPagination
    queryset = System.objects.all()
    serializer_class = SystemSerializer

    class SystemFilter(filters.FilterSet):

        class Meta:
            model = System
            fields = ['name', 'description']

    filter_class = SystemFilter


router.register(r'system', ViewSystem, basename='system')


class ViewComponent(viewsets.ModelViewSet):
    # pagination_class = StandardResultsSetPagination
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    class ComponentFilter(filters.FilterSet):
        class Meta:
            model = Component
            fields = {'name': ['contains', 'in'], 'description': ['contains', 'in'], }

    filter_class = ComponentFilter


router.register(r'component', ViewComponent, basename='component')


class ViewPart(viewsets.ModelViewSet):
    # pagination_class = StandardResultsSetPagination
    queryset = Part.objects.all()
    serializer_class = PartSerializer

    class PartFilter(filters.FilterSet):
        class Meta:
            model = Part
            fields = {'name': ['contains', 'in'], 'description': ['contains', 'in'], 'sku': ['contains', 'in']}

    filter_class = PartFilter


router.register(r'part', ViewPart, basename='part')


class ViewOrder(viewsets.ModelViewSet):
    # pagination_class = StandardResultsSetPagination
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    class OrderFilter(filters.FilterSet):

        class Meta:
            model = Order
            fields = ['description']

    filter_class = OrderFilter


router.register(r'order', ViewOrder, basename='order')


class ViewPartComponent(viewsets.ModelViewSet):
    # pagination_class = StandardResultsSetPagination
    queryset = PartComponent.objects.all()
    serializer_class = PartComponentSerializer

    class PartComponentFilter(filters.FilterSet):
        class Meta:
            model = PartComponent
            fields = {'part': ['exact', 'in'], 'component': ['exact', 'in']}

    filter_class = PartComponentFilter


router.register(r'partcomponent', ViewPartComponent, basename='partcomponent')


class ViewOrderItem(viewsets.ModelViewSet):
    # pagination_class = StandardResultsSetPagination
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    class OrderItemFilter(filters.FilterSet):

        class Meta:
            model = OrderItem
            fields = '__all__'

    filter_class = OrderItemFilter


router.register(r'orderitem', ViewOrderItem, basename='orderitem')

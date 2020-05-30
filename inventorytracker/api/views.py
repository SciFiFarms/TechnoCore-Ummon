from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import routers
from rest_framework.decorators import action
from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    SystemSerializer,
    ComponentSerializer,
    PartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PartComponentSerializer,
    SensorSerializer
)
from .models import (
    System,
    Component,
    Part,
    PartComponent,
    Order,
    OrderItem,
    Seedship,
    Sensor,
)
from api.forms import *

import influxdb
import influxalchemy
import os
import pandas
import re
from pathlib import Path
from sklearn import linear_model 
import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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

class ViewSensor(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

    @staticmethod
    def send_mqtt(topic, message, qos=1, retain=True):
        layer = get_channel_layer()
        msg = {
            "topic": topic,
            "payload": message,
        }
        async_to_sync(layer.send)('mqtt', {
            'type': 'mqtt.pub',
            'text': json.dumps(msg),
            'content': 'triggered'
        })    

    @action(detail=True, methods=['get', 'post'])
    def calibrate(self, request, pk=None):
        if request.method == "POST":
            form = SensorModelForm(request.POST)
            ## TODO: Add validation. Currently problematic because there are issues with the models.
            #if form.is_valid():
            raw_sensors = form.data["raw_sensors"]
            calibration_entity = form.data["calibration_entity"]
            time_range_start = form.data["time_range_start"]
            time_range_end = form.data["time_range_end"]
            measurement = form.data["measurement"]

            db = influxdb.DataFrameClient(database="home_assistant", host="influxdb", username=os.environ['INFLUXDB_USER'], password=Path('/run/secrets/influxdb_password').read_text().strip("\n"))

            for sensor in raw_sensors.split(","):
                # TODO: Move this to flux so that I can maybe use bind_params. It works for queries, but not sub queries. 
                results = db.query(f"SELECT first(\"value\") AS \"value\", first(\"calibrated_value\") AS \"calibrated_value\" \
                    FROM (SELECT \"value\" FROM \"raw\" WHERE (entity_id =~ /({ sensor })/) AND time >= { time_range_start }ms and time <= { time_range_end }ms), \
                    (SELECT \"value\" AS \"calibrated_value\" FROM \"{ measurement }\" WHERE entity_id =~ /({ calibration_entity })/ AND time >= { time_range_start }ms and time <= { time_range_end }ms) \
                    GROUP BY time(10s)")

                # Clean up results
                results = pandas.concat(results, keys=[measurement, "raw"], axis=1)
                results = results.dropna(axis=0)
                X = results["raw"]
                Y = results[measurement]

                model = linear_model.LinearRegression().fit(X.values.reshape(-1, 1), Y.values.reshape(-1, 1))
                expression = re.compile(r'(?P<seedship>seedship)_(?P<device>.*\d+)_(?P<subsystem>.*)_(?P<sensor>{}.*)'.format(measurement.lower()))
                s = expression.search( sensor )
                if s:
                    topic = f"{ s.group('seedship') }/{ s.group('device') }/{ s.group('subsystem') }/{ s.group('sensor').replace('_raw', '_calibration') }"
                    print(f"Linear calibration for { topic }: Slope({ model.coef_[0] }) Intercept({ model.intercept_[0]})")
                    ViewSensor.send_mqtt(topic, { "slope": model.coef_[0][0], "bias": model.intercept_[0] } )

            return HttpResponse(status=204)

        form = SensorModelForm(initial={
            "calibration_entity": pk,
            "raw_sensors": request.GET.get("raw_sensors"),
            "time_range_start": request.GET.get("time_range_start"),
            "time_range_end": request.GET.get("time_range_end"),
            "measurement": request.GET.get("measurement"),
        })
        context = {
            'title': "Calibrate Linear Filter",
            'form': form,
        }
        return render(request, 'seedship_gui/gf-form.html', context)
router.register(r'sensor', ViewSensor, basename='sensor')

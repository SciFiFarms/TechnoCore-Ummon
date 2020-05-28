from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from api.forms import *

class ViewMqtt(viewsets.ModelViewSet):

    def send_mqtt(request, topic="no_topic_set", *args, **kwargs):
        if request.method == "POST":
            seedships = topic.replace("seedship/", "").split("/")[0]
            layer = get_channel_layer()
            for seedship in seedships.split(","):
                msg = {
                    "topic": topic,
                    "payload": request.POST["message"],
                }
                async_to_sync(layer.send)('mqtt', {
                    'type': 'mqtt.pub',
                    'text': msg,
                    'content': 'triggered'
                })

            return HttpResponse(status=204)

        form = SeedshipMQTTForm(initial={
            "topic": topic,
            "message": request.GET.get("message"),
            "retain": request.GET.get("retain", False),
            "qos": request.GET.get("qos", 1),
        })
        context = {
            'title': "MQTT Publish",
            'form': form,
        }
        return render(request, "seedship_gui/gf-form.html", context)

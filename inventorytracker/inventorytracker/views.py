from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from api.forms import *

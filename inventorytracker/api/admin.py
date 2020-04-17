from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Part)
admin.site.register(Component)
admin.site.register(System)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PartComponent)
from django.forms import ModelForm, TextInput, TimeInput, Form, CharField, BooleanField, ChoiceField, CheckboxInput, Select, HiddenInput
from django.core import validators
from api.models import *

## This is a reference/experiment for how to add css classes to the label fields. 
#class BaseForm(ModelForm):
#    def __init__(self, *args, **kwargs):
#        super(BaseForm, self).__init__(*args, **kwargs)
#        #print(self.as_table())
#        for field in self: 
#            field.label_classes = ("lc")
#            print(field.label_tag(attrs={"class": "woot"}))

class SensorModelForm(ModelForm):
    class Meta:
        model = Sensor
        fields = '__all__'
        validators={
            "calibration_entity": [],
            "sensors": [],
            "time_range_start": [],
            "time_range_end": [],
            "measurements": [],
            }
        widgets={
            "calibration_entity": TextInput(attrs={ "readonly": True }),
            "raw_sensors": TextInput(attrs={ "readonly": True }),
            "time_range_start": TimeInput(attrs={ "readonly": True }, format='%s'),
            "time_range_end": TimeInput(attrs={ "readonly": True }, format='%s'),
            "measurement": HiddenInput(attrs={"hidden": True}),
            }

class SeedshipMQTTForm(Form):
    #validators = {[validators.DecimalValidator(20, 10)]}
    topic = CharField(widget=TextInput(attrs={"disabled": True}))
    message = CharField()
    retain = BooleanField(widget=HiddenInput())
    qos = ChoiceField(widget=HiddenInput(attrs={"hidden": True}), choices=[("0", "0"), ("1", "1"), ("2", "2")])

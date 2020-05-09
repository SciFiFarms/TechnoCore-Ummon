from django.forms import ModelForm, TextInput, TimeInput
from api.models import *

class SensorModelForm(ModelForm):
    class Meta:
        model = Sensor
        fields = '__all__'
        widgets={
            "calibration_entity": TextInput(attrs={ "disabled": True }),
            "seedship_id": TextInput(attrs={ "disabled": True }),
            "time_range_start": TimeInput(attrs={ "disabled": True }, format='%s'),
            "time_range_end": TimeInput(format='%s'),
            }

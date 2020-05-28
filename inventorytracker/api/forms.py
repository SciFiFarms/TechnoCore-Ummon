from django.forms import ModelForm, TextInput, TimeInput
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
        widgets={
            "calibration_entity": TextInput(attrs={ "disabled": True }),
            "seedship_id": TextInput(attrs={ "disabled": True }),
            "time_range_start": TimeInput(attrs={ "disabled": True }, format='%s'),
            "time_range_end": TimeInput(format='%s'),
            }

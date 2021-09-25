from django.forms import ModelForm
from admin_panel.models import Chartconfig
from django.core.exceptions import ValidationError

class ChartconfigForm(ModelForm):
    class Meta:
        model = Chartconfig
        fields = '__all__'
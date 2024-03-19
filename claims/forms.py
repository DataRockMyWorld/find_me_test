from django import forms
from .models import Claim

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['description', 'lost_location', 'last_seen']
        widgets = {
            'last_seen': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        
    
    def __init__(self, *args, **kwargs):
        super(ClaimForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

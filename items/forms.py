from django import forms
from .models import Item, Category

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'status', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(choices=Item.STATUS_CHOICES, attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].label_from_instance = lambda obj: "%s" % obj.name
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class ItemSearchForm(forms.Form):
    query = forms.CharField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    status = forms.ChoiceField(choices=Item.STATUS_CHOICES, required=False)
    location = forms.CharField(required=False)
    sort_by = forms.ChoiceField(choices=[('newest', 'Newest'), ('oldest', 'Oldest')], required=False)
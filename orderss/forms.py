from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','email','phone_number','state','city','address_line_1','address_line_2','order_note']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'state', 'city', 'address_line_1', 'address_line_2', 'order_note']
        widgets = {
            'address_line_2': forms.TextInput(attrs={'required': False}),
            'order_note': forms.Textarea(attrs={'required': False}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and (len(phone_number) != 10):
            raise forms.ValidationError('Phone number must be 10 digits.')
        return phone_number


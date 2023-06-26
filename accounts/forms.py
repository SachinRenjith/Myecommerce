from django import forms
from .models import Account
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import get_user_model


class RegistrationForm(forms.ModelForm):
    
    profile_picture = forms.ImageField(widget=forms.ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class' : 'form-control',

    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter Phone Number',
        'class': 'form-control',
    }), validators=[
        MinLengthValidator(10, message='Phone number must have at least 10 digits.'),
        MaxLengthValidator(10, message='Phone number can have at most 10 digits.')
    ])

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }),
         validators=[
            MinLengthValidator(8, message="Password should be at least 8 characters long."),
            MaxLengthValidator(20, message="Password should not exceed 20 characters."),
        ]
    
    )
     
     
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number','username', 'email', 'password']

    

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name' 
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        # self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email address'
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'

        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')


        if password != confirm_password:
            raise forms.ValidationError(
                "Passwords does not match"
            )


 


User = get_user_model()

 
class EditUserForm(UserChangeForm):
    phone_number = forms.CharField(validators=[
        MinLengthValidator(10, message='Phone number must be at least 10 digits.'),
        MaxLengthValidator(10, message='Phone number must be at most 10 digits.')
    ])
    

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username','phone_number')

    def __init__(self, *args, **kwargs):
     super().__init__(*args, **kwargs)
     self.fields.pop('password')

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})



     
     


    
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Plan

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    mobile_no = forms.CharField(max_length=10, required=True)
    sponsor_username = forms.CharField(max_length=150, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})

class PlanSelectionForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.all(),
        widget=forms.RadioSelect,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plan'].widget.attrs.update({'class': 'mr-2'})

class MobileRechargeForm(forms.Form):
    COMPANY_CHOICES = [
        ('jio', 'Jio'),
        ('airtel', 'Airtel'),
        ('vi', 'Vodafone Idea'),
        ('bsnl', 'BSNL'),
    ]
    
    mobile_no = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter mobile number'
        })
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter amount'
        })
    )
    company_name = forms.ChoiceField(
        choices=COMPANY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    is_stv = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        })
    )

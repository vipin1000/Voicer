from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *



class SignUpForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    role = forms.ChoiceField(choices=UserProfile.USER_ROLES)
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    avatar = forms.ImageField(required=False)
    audio_file = forms.FileField(required=False)
    rate = forms.IntegerField(required=False, initial=123, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class EmailVerificationForm(forms.Form):
    email = forms.EmailField(
        label="",widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Enter your email address'})
    )

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        label="",max_length=6,min_length=6,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter 6-digit OTP'})
    )



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'role','audio_file','rate']

class PlaceOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['service', 'requirements']  # Add other fields as needed
        widgets = {
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your requirements'}),
        }
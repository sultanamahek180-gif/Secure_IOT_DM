from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from captcha.fields import CaptchaField
from .models import User
from.models import Organization,Device,DeviceData,Alert,DeviceAccess

class DeviceAccessForm(forms.ModelForm):
	class Meta:
		model = DeviceAccess
		fields = ("user", "device", "can_read", "can_write")

class AlertForm(forms.ModelForm):
	class Meta:
		model = Alert
		fields = ("device", "alert_type", "message", "severity")

class DeviceDataForm(forms.ModelForm):
	class Meta:
		model = DeviceData
		fields = ( "device", "data")
    

class DeviceForm(forms.ModelForm):
	class Meta:
		model = Device
		fields = ("device_name", "device_type", "status")
		
class OrganizationForm(forms.ModelForm):
	class Meta:
		model = Organization
		fields = ("org_name", "contact_email")
		

# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	captcha = CaptchaField()
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2", "organization", "captcha")


	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user
	
class UserLoginForm(forms.Form):
	username =forms.CharField()
	password =forms.CharField(widget=forms.PasswordInput)
	captcha = CaptchaField()  
	
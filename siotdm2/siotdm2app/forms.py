from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from captcha.fields import CaptchaField, ValidationError
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
	import re
	from django.core.exceptions import ValidationError
class UserLoginForm(forms.Form):
	username =forms.CharField()
	password =forms.CharField(widget=forms.PasswordInput)
	captcha = CaptchaField()  
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2", "organization", "captcha")
		def clean_password2(self):
			password1 = self.cleaned_data.get("password1")
			password2 = self.cleaned_data.get("password2")
			if password1 and password2 and password1 != password2:
				raise ValidationError("Passwords don't match")
			if password1 and (len(password1) < 8 or not re.search(r'[A-Za-z]', password1) or not re.search(r'[0-9]', password1)):
				raise ValidationError("Password must be at least 8 characters long and contain both letters and numbers")
			return password2
	
# forms.py ke bilkul neeche add karo
from django.core.validators import RegexValidator

class PhoneForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': '+911234567890'})
    )

class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        label="OTP",
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'placeholder': '6-digit OTP'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message="OTP sirf 6 digits ka hona chahiye"
            )
        ]
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit():
            raise forms.ValidationError("OTP mein sirf numbers hone chahiye")
        return otp
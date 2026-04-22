from django.shortcuts import render, redirect
from .forms import NewUserForm, UserLoginForm, OrganizationForm, DeviceForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Organization, Device, DeviceData, Alert, DeviceAccess
from .forms import DeviceDataForm
import json
from .forms import AlertForm
from .forms import DeviceAccessForm
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import DeviceData
from .serializers import DeviceDataSerializer
from django.conf import settings
from twilio.rest import Client
from django.shortcuts import get_object_or_404

# ✅ Naye imports
from django.contrib import messages
from .models import OTPVerification, User
from .forms import OTPForm
from .utils import send_otp
from cryptography.fernet import Fernet

# generate key once and store it
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(data):
    json_data = json.dumps(data)   # 🔥 convert dict → string
    return cipher.encrypt(json_data.encode()).decode()

def decrypt_data(encrypted_data):
    json_data = cipher.decrypt(encrypted_data.encode()).decode()
    return json.loads(json_data)

@api_view(['GET', 'POST'])
def devicedata_api(request):
    """Get all device data or create new device data"""
    if request.method == 'GET':
        devicedata = DeviceData.objects.all()
        serializer = DeviceDataSerializer(devicedata, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = DeviceDataSerializer(data=request.data)
        if serializer.is_valid():
            #add the logic to encrypt the data before saving
            print("Original Data:", serializer.validated_data)
  

            serializer.save()
            #add the logic to decrypt the data before sending the response

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   


@login_required
def deviceaccess_list(request):
    accesses = DeviceAccess.objects.all()
    return render(request, 'deviceaccess/list.html', {'accesses': accesses})

@login_required
def deviceaccess_create(request):
    if request.method == "POST":
        form = DeviceAccessForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("deviceaccess_list")
    else:
        form = DeviceAccessForm()
    return render(request, 'deviceaccess/form.html', {'form': form})

@login_required
def deviceaccess_update(request, access_id):
    access = DeviceAccess.objects.get(access_id=access_id)
    if request.method == "POST":
        form = DeviceAccessForm(request.POST, instance=access)
        if form.is_valid():
            form.save()
            return redirect("deviceaccess_list")
    else:
        form = DeviceAccessForm(instance=access)
    return render(request, 'deviceaccess/form.html', {'form': form})

@login_required
def deviceaccess_delete(request, access_id):
    access = DeviceAccess.objects.get(access_id=access_id)
    if request.method == "POST":
        access.delete()
        return redirect("deviceaccess_list")
    return render(request, 'deviceaccess/confirm_delete.html', {'access': access})

@login_required
def alert_list(request):
    alerts = Alert.objects.all()
    return render(request, 'alert/list.html', {'alerts': alerts})

@login_required
def alert_create(request):
    if request.method == "POST":
        form = AlertForm(request.POST)
        if form.is_valid()  :
            form.save()
            return redirect("alert_list")
    else:
        form = AlertForm()
    return render(request, 'alert/form.html', {'form': form})

@login_required
def alert_update(request, alert_id):
    alert = Alert.objects.get(alert_id=alert_id)
    if request.method == "POST":
        form = AlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            return redirect("alert_list")
    else:
        form = AlertForm(instance=alert)
    return render(request, 'alert/form.html', {'form': form})

@login_required
def alert_delete(request, alert_id):
    alert = Alert.objects.get(alert_id=alert_id)
    if request.method == "POST":
        alert.delete()
        return redirect("alert_list")
    return render(request, 'alert/confirm_delete.html', {'alert': alert})


@login_required
def devicedata_list(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)
    data_entries = DeviceData.objects.filter(device=device).order_by('timestamp')

    temperatures = []
    humidities = []
    timestamps = []

    for entry in data_entries:
        if isinstance(entry.data, str):
            entry.data = decrypt_data(entry.data)

        temp = float(entry.data.get('temperature', 0))
        hum = float(entry.data.get('humidity', 0))

# overwrite so template gets correct value
        entry.data['temperature'] = temp
        entry.data['humidity'] = hum

        temperatures.append(temp)
        humidities.append(hum)
        timestamps.append(entry.timestamp.strftime("%H:%M:%S"))

    latest_data = data_entries.last()

    context = {
        'data_entries': data_entries,
        'device': device,
        'temperatures': temperatures,
        'humidities': humidities,
        'timestamps': timestamps,
        'latest_data': latest_data
    }

    return render(request, 'devicedata/list.html', context)

@login_required
def devicedata_create(request, device_id):
    device = Device.objects.get(device_id=device_id)
    if request.method == "POST":
        form = DeviceDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("devicedata_list", device_id=device_id)
        else:
            print(form.errors)
    else:
        form = DeviceDataForm(initial={'device': device})
    return render(request, 'devicedata/form.html', {'form': form, 'device': device})

@login_required
def devicedata_update(request, data_id):
    data_entry = DeviceData.objects.get(data_id=data_id)
    if request.method == "POST":
        form = DeviceDataForm(request.POST, instance=data_entry)
        if form.is_valid():
            data = form.save(commit=False)
            data.device = form.cleaned_data['device']  
            data.save()
            form.save()
            return redirect("devicedata_list", device_id=data_entry.device.device_id)
    else:
        form = DeviceDataForm(instance=data_entry)
    return render(request, 'devicedata/form.html', {'form': form, 'device': data_entry.device})

@login_required
def devicedata_delete(request, data_id):
    data_entry = DeviceData.objects.get(data_id=data_id)
    if request.method == "POST":
        device_id = data_entry.device.device_id
        data_entry.delete()
        return redirect("devicedata_list", device_id=device_id)
    return render(request, 'devicedata/confirm_delete.html', {'data_entry': data_entry})


@login_required
def device_list(request):
    devices = Device.objects.all()
    return render(request, 'device/list.html', {'devices': devices})

@login_required
def device_create(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.owner = request.user
            device.organization = request.user.organization
            device.save()
            return redirect("device_list")
    else:
        form = DeviceForm()
    return render(request, 'device/form.html', {'form': form})

@login_required
def device_update(request, device_id):
    device = Device.objects.get(device_id=device_id)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect("device_list")
    else:
        form = DeviceForm(instance=device)
    return render(request, 'device/form.html', {'form': form})

@login_required
def device_delete(request, device_id):
    device = Device.objects.get(device_id=device_id)
    if request.method == "POST":
        device.delete()
        return redirect("device_list")
    return render(request, 'device/confirm_delete.html', {'device': device})


def organization_create(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("organization_list")
    else:
        form = OrganizationForm()
    return render(request, 'org/form.html', {'form': form})


def organization_update(request, org_id):
    org = Organization.objects.get(org_id=org_id)
    if request.method == "POST":
        form = OrganizationForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            return redirect("organization_list")
    else:
        form = OrganizationForm(instance=org)
    return render(request, 'org/form.html', {'form': form})


def organization_delete(request, org_id):
    org = Organization.objects.get(org_id=org_id)
    if request.method == "POST":
        org.delete()
        return redirect("organization_list")
    return render(request, 'org/confirm_delete.html', {'org': org})


def organization_list(request):
    orgs = Organization.objects.all()
    return render(request, 'org/list.html', {'orgs': orgs})


def home(request):
    devices = Device.objects.all()
    return render(request, 'home.html', {'devices': devices})


def confirm_create(request):
    return render(request, 'org/confirm_create.html')


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            print(form.errors)
    else:
        form = NewUserForm()
    return render(request, "register.html", {"form": form})


def login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                request.session['pre_auth_user_id'] = user.id
                phone_number = user.phone_number
                request.session['otp_phone'] = phone_number
                send_otp(phone_number)
                return redirect("verify_otp")
            else:
                print("Invalid credentials")
        else:
            print(form.errors)
    else:
        form = UserLoginForm()
    return render(request, "login.html", {"form": form})


# ✅ TWILIO VERIFY SE OTP CHECK
def verify_otp(request):
    phone_number = request.session.get('otp_phone')
    user_id = request.session.get('pre_auth_user_id')

    if not phone_number or not user_id:
        return redirect('login')

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            try:
                verification_check = client.verify.v2.services(
                    settings.TWILIO_VERIFY_SID
                ).verification_checks.create(
                    to=phone_number,
                    code=entered_otp
                )

                if verification_check.status == 'approved':
                    user = User.objects.get(id=user_id)
                    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    del request.session['pre_auth_user_id']
                    del request.session['otp_phone']
                    return redirect('organization_list')
                else:
                    messages.error(request, 'Incorrect OTP, please try again')

            except Exception as e:
                messages.error(request, 'OTP verify failed, please try again')
    else:
        form = OTPForm()

    return render(request, "verify_otp.html", {'form': form, 'phone': phone_number})


def resend_otp(request):
    phone_number = request.session.get('otp_phone')
    if phone_number:
        send_otp(phone_number)
        messages.success(request, "A new OTP has been sent!")
    return redirect('verify_otp')


def logout(request):
    auth_logout(request)
    return redirect("home")

@login_required
def devicedata_dashboard(request, device_id):
    device = get_object_or_404(Device, device_id=device_id)
    data_entries = DeviceData.objects.filter(device=device).order_by('timestamp')

    temperatures = []
    humidities = []
    timestamps = []

    for entry in data_entries:
        if isinstance(entry.data, str):
            entry.data = decrypt_data(entry.data)

        temperatures.append(entry.data.get('temperature'))
        humidities.append(entry.data.get('humidity'))
        timestamps.append(entry.timestamp.strftime("%H:%M:%S"))

    latest_data = data_entries.last()

    return render(request, 'devicedata/dashboard.html', {
        'device': device,
        'data_entries': data_entries,
        'temperatures': temperatures,
        'humidities': humidities,
        'timestamps': timestamps,
        'latest_data': latest_data
    })
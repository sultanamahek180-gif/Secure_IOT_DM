from django.shortcuts import render, redirect
from .forms import NewUserForm, UserLoginForm, OrganizationForm, DeviceForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Organization, Device, DeviceData, Alert,DeviceAccess
from .forms import DeviceDataForm
import json
from .forms import AlertForm
from .forms import DeviceAccessForm

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
        if form.is_valid():
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
    device = Device.objects.get(device_id=device_id)
    data_entries = DeviceData.objects.filter(device=device)
    # ✅ Convert JSON strings to Python dicts so template can access keys
    for entry in data_entries:
        if isinstance(entry.data, str):  # only if JSON stored as string
            entry.data = json.loads(entry.data)
    return render(request, 'devicedata/list.html', {'data_entries': data_entries, 'device': device})

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
    return render(request, 'home.html')


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
                auth_login(request, user)
                return redirect("organization_list")
            else:
                print("Invalid credentials")
        else:
            print(form.errors)
    else:
        form = UserLoginForm()

    return render(request, "login.html", {"form": form})


def logout(request):
    auth_logout(request)
    return redirect("home")
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# ==============================
# 1️⃣ Organization Model
# ==============================
class Organization(models.Model):
    org_id = models.AutoField(primary_key=True)
    org_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.org_name


# ==============================
# 2️⃣ Custom User Model (Secure)
# ==============================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    )

    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='admin'
    )

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# ==============================
# 3️⃣ IoT Device Model
# ==============================
class Device(models.Model):
    DEVICE_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
    )

    device_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=DEVICE_STATUS)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.device_name


# ==============================
# 4️⃣ Device Data Logs
# ==============================
class DeviceData(models.Model):
    data_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.device_name} - {self.timestamp}"



# ==============================
# 5️⃣ Alerts / Security Events
# ==============================
import uuid

class Alert(models.Model):
    ALERT_TYPES = (
        ('intrusion', 'Intrusion'),
        ('malfunction', 'Malfunction'),
        ('unauthorized', 'Unauthorized Access'),
    )

    SEVERITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
        (5, 'Emergency'),
    ]

    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey('Device', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=1)  # 1 to 5 with labels
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alert_type} - {self.device.device_name}"


# ==============================
# 6️⃣ Access Control / Permissions
# ==============================
class DeviceAccess(models.Model):
    access_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    granted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.device.device_name}"  
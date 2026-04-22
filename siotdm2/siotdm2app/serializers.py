from rest_framework import serializers
from .models import DeviceData  # Assuming DeviceData model exists in models.py

class DeviceDataSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(write_only=True)

    class Meta:
        model = DeviceData
        fields = ['device_id', 'data', 'timestamp']

    def create(self, validated_data):
        device_id = validated_data.pop('device_id')

        from .models import Device  # import here to avoid circular import

        device = Device.objects.get(device_id=device_id)  # 🔥 get actual object

        return DeviceData.objects.create(
            device=device,
            **validated_data
        )
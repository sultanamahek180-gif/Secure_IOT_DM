import random
from django.utils import timezone
from datetime import timedelta
from .models import OTPVerification
from twilio.rest import Client
from django.conf import settings

def send_otp(phone_number):
    otp_code = str(random.randint(100000, 999999))
    expires_at = timezone.now() + timedelta(minutes=5)

    # Purane OTP expire karo
    OTPVerification.objects.filter(
        phone_number=phone_number,
        is_expired=False
    ).update(is_expired=True)

    # Naya OTP save karo
    OTPVerification.objects.create(
        phone_number=phone_number,
        otp_code=otp_code,
        expires_at=expires_at
    )

    # Twilio Verify se OTP bhejo
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.verify.v2.services(
        settings.TWILIO_VERIFY_SID
    ).verifications.create(
        to=phone_number,
        channel='sms'
    )
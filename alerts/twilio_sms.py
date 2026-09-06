from twilio.rest import Client

from config.secrets import (
    TWILIO_ACCOUNT_SID,
    TWILIO_API_KEY,
    TWILIO_API_SECRET,
    TWILIO_PHONE_NUMBER,
    RESPONDER_PHONE_NUMBER,
)


def send_sms():
    try:
        client = Client(
            TWILIO_API_KEY,
            TWILIO_API_SECRET,
            account_sid=TWILIO_ACCOUNT_SID
        )

        sms = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            to=RESPONDER_PHONE_NUMBER,
            body="sms_internal_alerts"
        )

        print(f"[SMS] Alert sent successfully: {sms.sid}")
        return True

    except Exception as e:
        print(f"[SMS] Failed to send alert: {e}")
        return False
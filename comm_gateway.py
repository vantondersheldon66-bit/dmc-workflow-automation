"""
DMC Communication Gateway
Supports Twilio WhatsApp, Meta WhatsApp Cloud API, and SMTP/IMAP Email.
Provides fallback simulation mode when live API keys are not provided.
"""

import os
import json
import urllib.request
import urllib.parse
import base64

class CommunicationGateway:
    def __init__(self):
        self.twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.twilio_from = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        
        self.smtp_host = os.environ.get("SMTP_HOST", "")
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_pass = os.environ.get("SMTP_PASS", "")

    def send_whatsapp(self, to_phone: str, message_body: str) -> dict:
        """Sends a WhatsApp message via Twilio or falls back to simulation mode."""
        clean_phone = to_phone.strip()
        if not clean_phone.startswith("whatsapp:"):
            clean_phone = f"whatsapp:{clean_phone}"

        # If live Twilio credentials provided, call Twilio API
        if self.twilio_sid and self.twilio_token:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
            data = urllib.parse.urlencode({
                "From": self.twilio_from,
                "To": clean_phone,
                "Body": message_body
            }).encode("utf-8")

            req = urllib.request.Request(url, data=data, method="POST")
            auth_str = f"{self.twilio_sid}:{self.twilio_token}"
            auth_b64 = base64.b64encode(auth_str.encode()).decode()
            req.add_header("Authorization", f"Basic {auth_b64}")

            try:
                with urllib.request.urlopen(req) as response:
                    res_body = json.loads(response.read().decode())
                    return {"status": "sent", "provider": "twilio", "sid": res_body.get("sid")}
            except Exception as e:
                return {"status": "error", "error": str(e), "fallback": "simulated"}

        # Simulation Mode
        return {
            "status": "simulated_sent",
            "provider": "simulator",
            "recipient": clean_phone,
            "preview": message_body[:120] + "..." if len(message_body) > 120 else message_body
        }

    def send_email(self, to_email: str, subject: str, html_body: str) -> dict:
        """Sends an email via SMTP or simulation mode."""
        if self.smtp_host and self.smtp_user:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to_email
            msg.attach(MIMEText(html_body, "html"))

            try:
                with smtplib.SMTP(self.smtp_host, 587) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_pass)
                    server.sendmail(self.smtp_user, to_email, msg.as_string())
                return {"status": "sent", "provider": "smtp", "recipient": to_email}
            except Exception as e:
                return {"status": "error", "error": str(e), "fallback": "simulated"}

        return {
            "status": "simulated_sent",
            "provider": "simulator",
            "recipient": to_email,
            "subject": subject
        }

gateway = CommunicationGateway()

if __name__ == "__main__":
    res = gateway.send_whatsapp("+39333444555", "Test DMC WhatsApp ping to chauffeur Antonio.")
    print("Gateway test output:", res)

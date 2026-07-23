import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import SENDER_EMAIL, APP_PASSWORD

def send_email(to_email, subject, body_html):
    if not SENDER_EMAIL or not APP_PASSWORD:
        msg = "SENDER_EMAIL or APP_PASSWORD not set in .env"
        print(f"❌ Error: {msg}")
        return False, "Env Error", msg
        
    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
        return True, "Success", "Email successfully dispatched via SMTP."
    except smtplib.SMTPAuthenticationError as e:
        msg = f"Google App Password or Email is incorrect: {e}"
        print(f"❌ {msg}")
        return False, "Auth Error", msg
    except smtplib.SMTPException as e:
        msg = f"SMTP protocol rejected the email: {e}"
        print(f"❌ {msg}")
        return False, "Mail Error", msg
    except Exception as e:
        msg = f"System encountered an unexpected crash: {e}"
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False, "System Error", msg

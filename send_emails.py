import smtplib
import logging
import os
import sys
from email.message import EmailMessage
from attach_cv import attach_file
from email_body import subject, body, html_body

def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(_app_dir(), "email_sending.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SMTP_SERVERS = {
    "gmail.com":   ("smtp.gmail.com", 587),
    "outlook.com": ("smtp-mail.outlook.com", 587),
    "hotmail.com": ("smtp-mail.outlook.com", 587),
    "yahoo.com":   ("smtp.mail.yahoo.com", 587),
    "icloud.com":  ("smtp.mail.me.com", 587),
    "me.com":      ("smtp.mail.me.com", 587),
    "yandex.com":  ("smtp.yandex.com", 587),
    "mail.com":    ("smtp.mail.com", 587),
}

def get_smtp_settings(email):
    domain = email.split("@")[1]
    if domain not in SMTP_SERVERS:
        raise ValueError(f"Unsupported email domain: {domain}")
    return SMTP_SERVERS[domain]

def get_email_list(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logging.error(f"Error reading email list: {e}")
        raise

def send_email(recipient, smtp_server, smtp_port, sender_email, sender_password, file_path=None):
    try:
        msg = EmailMessage()
        msg["From"]    = sender_email
        msg["To"]      = recipient
        msg["Subject"] = subject
        msg.set_content(body)
        msg.add_alternative(html_body, subtype="html")

        if file_path:
            attach_file(msg, file_path)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            logging.info(f"Sent: {recipient}")
            return True

    except smtplib.SMTPAuthenticationError:
        logging.error(f"Auth failed: {recipient}")
    except Exception as e:
        logging.error(f"Failed: {recipient} — {e}")
    return False

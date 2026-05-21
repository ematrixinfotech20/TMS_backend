import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader

import logging
logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "webzoidsolution@gmail.com"
SENDER_PASSWORD = "fdeetasvdsoprzwr"

# Setup Jinja2 environment
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
try:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
except Exception as e:
    logger.info(f"Error loading template directory: {e}")
    env = None

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, template_name: str, context: dict):
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        if env:
            try:
                template = env.get_template(template_name)
                html_body = template.render(context)
                msg.attach(MIMEText(html_body, 'html'))
            except Exception as e:
                logger.info(f"Error rendering template: {e}")
                # Fallback to plain text if rendering fails
                msg.attach(MIMEText(str(context), 'plain'))
        else:
            # Fallback to plain text
            msg.attach(MIMEText(str(context), 'plain'))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
            server.quit()
            logger.info(f"Email successfully sent to {to_email}")
        except Exception as e:
            logger.info(f"Failed to send email to {to_email}: {e}")

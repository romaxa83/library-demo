from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib
from src.config import Config

config = Config()

async def send_email(
        to: str,
        subject: str,
        content_text: str,
        content_html: str = "",
):
    msg = MIMEMultipart("alternative")
    msg["From"] = config.mail.from_address
    msg["To"] = to
    msg["Subject"] = subject

    plain_text = MIMEText(content_text, "plain", "utf-8")
    msg.attach(plain_text)
    if content_html:
        html_text = MIMEText(content_html, "html", "utf-8")
        msg.attach(html_text)

    await aiosmtplib.send(
        msg,
        hostname=config.mail.host,
        port=config.mail.port,
        # username=config.mail.username,
        # password=config.mail.password
    )

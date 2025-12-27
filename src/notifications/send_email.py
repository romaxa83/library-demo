from textwrap import dedent

from src.templates import templates
from src.users.models import User
from src.utils.send_email import send_email
from src.notifications.utils import (
    email_verify_link,
    reset_password_link
)

async def send_verification_email(
        user: User,
        verify_token: str,
)-> None:
    verification_link = email_verify_link(verify_token)

    to = user.email
    subject = "Verify your email to site.com"

    content_text = dedent(
        f"""\
        Dear {user.username}
        
        Please verify your email address to site.com and click the link below:
        {verification_link}
        """
    )

    template = templates.get_template("mail/email-verify/verification-request.html")
    context = {
        "user": user,
        "verification_link": verification_link,
    }
    content_html = template.render(context)
    await send_email(to, subject, content_text, content_html)

async def send_email_verified(user: User)-> None:

    to = user.email
    subject = "Email confirmed"

    content_text = dedent(
        f"""\
        Dear {user.username}

        Email confirmed. Your email address has been verified.
        """
    )

    template = templates.get_template("mail/email-verify/email-verified.html")
    context = {
        "user": user,
    }
    content_html = template.render(context)
    await send_email(to, subject, content_text, content_html)

async def send_email_forgot_password(user: User, reset_password_token: str)-> None:
    link = reset_password_link(reset_password_token)
    to = user.email
    subject = "Password reset"

    content_text = dedent(
        f"""\
        Dear {user.username}

        There was a request to change your password!.
        If you did not make this request then please ignore this email.
        Otherwise, please click this link to change your password: {link}
        """
    )

    template = templates.get_template("mail/reset-password/forgot-password.html")
    context = {
        "user": user,
        "link": link,
    }
    content_html = template.render(context)
    await send_email(to, subject, content_text, content_html)

async def send_email_reset_password(user: User, password: str)-> None:

    to = user.email
    subject = "New password"

    content_text = dedent(
        f"""\
        Dear {user.username}

        Your new password: {password}.
        Use the specified password to log into your account.
        After entering your personal account, we strongly recommend that you change the password to a more understandable and reliable one.
        """
    )

    template = templates.get_template("mail/reset-password/reset-password.html")
    context = {
        "user": user,
        "password": password,
    }
    content_html = template.render(context)
    await send_email(to, subject, content_text, content_html)
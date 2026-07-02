"""Transactional email — SMTP when configured, log-only in development."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger("untold")


class EmailService:
    @staticmethod
    def is_configured() -> bool:
        settings = get_settings()
        return bool(settings.smtp_host and settings.smtp_from_email)

    @staticmethod
    def send_email(*, to: str, subject: str, body: str) -> None:
        settings = get_settings()
        if not EmailService.is_configured():
            logger.info("Email (not sent — SMTP not configured) to=%s subject=%s", to, subject)
            if settings.is_development:
                logger.debug("Email body: %s", body)
            return

        msg = EmailMessage()
        msg["From"] = settings.smtp_from_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(msg)

        logger.info("Email sent to=%s subject=%s", to, subject)

    @staticmethod
    def send_password_reset(to: str, reset_url: str) -> None:
        EmailService.send_email(
            to=to,
            subject="Reset your UNTOLD password",
            body=(
                "You requested a password reset for your UNTOLD account.\n\n"
                f"Reset your password: {reset_url}\n\n"
                "This link expires in 1 hour. If you did not request this, ignore this email."
            ),
        )

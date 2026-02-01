"""Notification system - email and desktop alerts."""
import logging
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger('leviathan.notify')


class Notifier:
    """Send trade notifications via email and desktop."""

    def __init__(self, smtp_email: str = '', smtp_password: str = ''):
        self.email = smtp_email
        self.password = smtp_password

    def send_trade_notification(self, trade: dict):
        msg = f"Trade: {trade.get('side', '')} {trade.get('symbol', '')} - {trade.get('reasoning', '')}"
        self._desktop_notify("Leviathan Trade", msg)
        if self.email:
            self._send_email("Leviathan Trade", msg)

    def send_alert(self, title: str, message: str):
        self._desktop_notify(title, message)
        logger.info(f"Alert: {title} - {message}")

    def send_daily_summary(self, summary: dict):
        body = f"P&L: ${summary.get('pnl', 0):.2f} | Trades: {summary.get('trades', 0)} | WR: {summary.get('win_rate', 0):.0%}"
        self.send_alert("Leviathan Daily Summary", body)

    def _desktop_notify(self, title, msg):
        try:
            from win10toast import ToastNotifier
            ToastNotifier().show_toast(title, msg[:256], duration=5, threaded=True)
        except Exception:
            logger.debug(f"Desktop notification unavailable: {title}")

    def _send_email(self, subject, body):
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.email
            msg['To'] = self.email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                s.login(self.email, self.password)
                s.send_message(msg)
        except Exception as e:
            logger.error(f"Email failed: {e}")

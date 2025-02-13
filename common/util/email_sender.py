import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailSender:
    def __init__(
            self,
            smtp_host: str,
            smtp_port: int,
            smtp_username: str,
            smtp_password: str,
            smtp_from_email_for_administrators: str
    ):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_username = smtp_username
        self._smtp_password = smtp_password
        self._from_email_for_administrators = smtp_from_email_for_administrators

    async def send_email_to_administrator(
            self,
            to_email: str,
            subject: str,
            html_content: str,
            text_content: Optional[str] = None
    ) -> None:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self._from_email_for_administrators
        msg['To'] = to_email

        if text_content is None:
            text_content = html_content.replace('<br>', '\n').replace('</p>', '\n\n')
            import re
            text_content = re.sub('<[^<]+?>', '', text_content)

        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                server.starttls()
                server.login(self._smtp_username, self._smtp_password)
                server.send_message(msg)
        except Exception as e:
            raise RuntimeError(f"Failed to send email: {str(e)}")
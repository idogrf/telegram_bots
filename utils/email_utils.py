import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailHandler:
    def __init__(self, email, password):
        self._email = email
        self._password = password
        self._smtp = None

    @property
    def smtp(self):
        if self._smtp is None:
            self._login_to_smtp()
        return self._s

    def _login_to_smtp(self):
        self._s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        self._s.starttls()
        self._s.login(self._email, self._password)

    def send_password(self, password):
        msg = MIMEMultipart()
        msg['from'] = self._email
        msg['to'] = self._email
        msg['Subject'] = "Your PI Bot token"

        msg.attach(MIMEText(password, 'plain'))

        self.smtp.send_message(msg)
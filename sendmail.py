import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()


def send_email(to_email, subject, body):

    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    msg = MIMEMultipart()

    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(sender_email, sender_password)

    server.sendmail(
        sender_email,
        to_email,
        msg.as_string()
    )

    server.quit()

    return f"Email sent to {to_email} successfully"


# if __name__ == "__main__":
#     result = send_email(
#         "muhammad.qasim.dev07@gmail.com",
#         "Test Email",
#         "Ye ek test email hai LangChain agent task ke liye."
#     )

#     print(result)
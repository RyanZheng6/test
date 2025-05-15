import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(file_path, recipients):
    msg = MIMEMultipart()
    msg['Subject'] = "Demo email"
    msg['From'] = "earlycareer-cnnm2@nomura.com"
    msg['To'] = ", ".join(recipients)  # Join all recipients with a comma

    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>News Monitoring Report</title>
        </head>
        <body>
             <p>Hi this is a Demo email</p>
            <p>PFA</p>
        </body>
    </html>
    """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with open(file_path, 'rb') as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(file_path)}")
            msg.attach(part)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    try:
        with smtplib.SMTP('mailhub.nomura.com', 25) as s:
            s.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
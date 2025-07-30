from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(to_email, blood_group, location_url, address, call_number):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Emergency Blood Request</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600&display=swap" rel="stylesheet">
    </head>
    <body style="background-color: #fff3f3; font-family: 'Inter', sans-serif; color: #000; text-align: center; padding: 40px;">
        <div style="background-color: #ffffff; border: 2px solid #f44336; padding: 30px; border-radius: 12px; max-width: 600px; margin: auto;">
            <h1 style="color: #f44336;">🚨 Emergency Blood Needed 🚨</h1>
            <p style="font-size: 18px;">We urgently need <strong>{blood_group}</strong> blood.</p>
            <p><strong>Location:</strong> {address}</p>
            <p><a href="{location_url}" style="color: #f44336; font-weight: bold;">View Location</a></p>
            <p>Please contact <strong>{call_number}</strong> if you can help.</p>
            <p style="font-size: 14px; color: #777;">Sent on: {now}</p>
            <p style="font-size: 14px; color: #999;">— Blood Bridge</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['Subject'] = f'URGENT: Blood Request for {blood_group}'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Emergency email sent to {to_email}")
    except Exception as e:
        print(f"❌ Error sending emergency email: {e}")

# send_email(
#     to_email="prathamb1501@gmail.com",
#     blood_group="O+",
#     location_url="https://maps.google.com/?q=13.3521,74.7917",
#     address="KMC Hospital, Ambedkar Circle, Manipal",
#     call_number="9988776655"
# )

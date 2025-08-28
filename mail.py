from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import smtplib
import os
from dotenv import load_dotenv

# INSERT INTO donors VALUES(132,'Evan lewis','jakobroshan@gmail.com','9743323436','2009-03-19','A+','','Bramavara','Karnataka','',NULL,NULL,1,'','');
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
        return True
    except Exception as e:
        print(f"❌ Error sending emergency email: {e}")
        return False

def happy_mail(details):
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
            <h1 style="color: #f44336;">{details['name']}</h1>
            
            <p style="font-size: 14px;"><strong>Mail: {details['email']}</strong></p>
            <p style="font-size: 14px;"><strong>Blood Group: {details['blood_group']}</strong></p>
            <p style="font-size: 14px;"><strong>Phone: {details['phone']}</strong></p>
            <p style="font-size: 14px; color: #777;">{details}</p>
            <p style="font-size: 14px; color: #777;">Sent on: {now}</p>
            <p style="font-size: 14px; color: #999;">— Blood Bridge</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['Subject'] = f'🎫💥New User Registered in Blood Bridge '
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = "prathamb1501@gmail.com"

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"🦕Mail sent to {details['email']}")
    except Exception as e:
        print(f"❌ Error sending emergency email: {e}")

def happy_mail_2(details):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You for Registering</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600&display=swap" rel="stylesheet">
    </head>
    <body style="background-color: #fff8f8; font-family: 'Inter', sans-serif; color: #000; text-align: center; padding: 40px;">
        <div style="background-color: #ffffff; border: 2px solid #f44336; padding: 30px; border-radius: 12px; max-width: 600px; margin: auto; box-shadow: 0px 4px 12px rgba(0,0,0,0.1);">
            <h1 style="color: #f44336; margin-bottom: 10px;">Registration Complete ✅</h1>
            <h2 style="color: #333; margin-top: 0;">Thank You for Your Lifesaving Decision ❤️</h2>
            
            <p style="font-size: 14px; margin: 8px 0;"><strong></strong>Here are your credentials to login anytime in future</p>
            <p style="font-size: 14px; margin: 8px 0;"><strong>Name:</strong> {details['name']}</p>
            <p style="font-size: 14px; margin: 8px 0;"><strong>Email:</strong> {details['email']}</p>

            <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">

            <p style="font-size: 14px; color: #777;">Sent on: {now}</p>
            <p style="font-size: 14px; color: #999; margin-top: 20px;">— Team Blood Bridge</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['Subject'] = f'Registration Complete'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = details['email']

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"🦕Mail sent to {details['email']}")
    except Exception as e:
        print(f"❌ Error sending emergency email: {e}")

# send_email(
#     to_email="prathamb1501@gmail.com",
#     blood_group="O+",
#     location_url="https://maps.google.com/?q=13.3521,74.7917",
#     address="KMC Hospital, Ambedkar Circle, Manipal",
#     call_number="9988776655"
# # )
# happy_mail_2({'name':'Pratham',
#             'email':'prathamb1501@gmail.com',
#             'phone':123,
#             'blood_group':"A+"})
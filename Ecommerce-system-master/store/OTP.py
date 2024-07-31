import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint, randrange
from .models import UserOTP

sender_email = 'uvthemonster147@gmail.com'
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = sender_email
smtp_password = 'ugpveoccoqjjbqfn'


def sendOTPToUserForSignUp(email):
    subject = 'Email Verification'
    otp = randrange(10000, 99999)
    body = "Your one time password is:" + str(otp)

    # Create a multipart message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = subject

    # Add body to the email
    message.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP(smtp_server, smtp_port)
    try:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, email, message.as_string())
        otp = UserOTP(email=email, otp=otp, is_signup=True)
        otp.save()
        print('Email sent successfully!')

    except Exception as e:
        print('An error occurred while sending the email:', str(e))
    finally:
        server.quit()


def sendOTPToUserForForgotPassword(email):
    subject = 'Reset Password'
    otp = randrange(10000, 99999)
    body = "Did you forgot your password? Enter the following one time password to reset your password. OTP :" + str(otp)

    # Create a multipart message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = subject

    # Add body to the email
    message.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP(smtp_server, smtp_port)
    try:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, email, message.as_string())
        otp = UserOTP(email=email, otp=otp, is_forgot_password=True)
        otp.save()
        print('Email sent successfully!')

    except Exception as e:
        print('An error occurred while sending the email:', str(e))
    finally:
        server.quit()

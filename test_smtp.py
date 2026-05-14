import smtplib
from email.mime.text import MIMEText

RESEND_API_KEY = "re_M7r6A8kp_GvUidfnwPs87TA6uRwB1HDTR"  # তোমার key

msg = MIMEText("Test email from Ottomax")
msg['Subject'] = "SMTP Test"
msg['From'] = "onboarding@resend.dev"
msg['To'] = "mdabdullatifdelta@gmail.com"

try:
    with smtplib.SMTP_SSL('smtp.resend.com', 465) as server:
        server.login('resend', RESEND_API_KEY)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print("Email sent!")
except Exception as e:
    print(f"Failed: {e}")
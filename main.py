import smtplib
import random
import time
import os
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()

# Global counters  
emails_sent = 0
retry_count = 0

# Validate Credentials
# if not EMAIL_USER or not EMAIL_PASSWORD:
#     logging.error("Email credentials not set in environment variables.")
#     exit(1)

SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

#MY_NUMBER = os.getenv('MY_NUMBER')

RECIPIENT_EMAIL = os.getenv('TO_EMAIL')
MIN_INTERVAL = 60
MAX_INTERVAL = 120

ACCOUNT_DETAILS = {
    'name': os.getenv('NAME'),
    'id_number': os.getenv('ID_NUMBER'),
    'billing_number': os.getenv('BILLING_NUMBER'),
    'phone_number': os.getenv('MY_NUMBER'),
    'email': os.getenv('EMAIL_USER')
}

VARIANTS = {
    'greetings': [
        "Dear MTN CIM Legal",
        "Dear MTN Legal Team",
        "Dear MTN Acounts Department",
        "Dear MTN Customer Care"
    ],
    'opening': [
        "I hope this email finds you well.",
        "I trust you are doing well.",
        "I hope you are well.",
        "I trust this email finds you well."
    ],
    'request': [
        "I am writing to formally request for a paid-up letter for my MTN account.",
        "Kindly provide me with a paid-up letter for my MTN account.",
        "Please issue me with a paid-up letter for my MTN account."
    ],
    'confirmation': [
        "I can confirm that the account is fully paid up.",
        "The account is fully paid up through the SSDA legal team that you handed over to.",
        "The account is fully paid up in 2024 through the legal team that you handed over to.",
        "I can confirm that the account is fully paid up through the legal team that you handed over to."
    ],
    'urgency': [
        "This is now a matter of urgency as it is affecting my credit score badly.",
        "I would appreciate it if you could expedite this request.",
        "This is an urgent request and I would appreciate your prompt attention to it.",
    ],
    'closing': [
        "I am looking forward to hearing from you soon.",
        "I am looking forward to hearing from you.",
        "I would appreciate your prompt attention to this matter.",
    ]

}

def generate_body():
    """Generate the email body using the VARIANTS dictionary."""
    body = {
        'greetings': random.choice(VARIANTS['greetings']),
        'opening': random.choice(VARIANTS['opening']),
        'request': random.choice(VARIANTS['request']),
        'confirmation': random.choice(VARIANTS['confirmation']),
        'urgency': random.choice(VARIANTS['urgency']),
        'closing': random.choice(VARIANTS['closing'])
    }

    return f"""
{body['greetings']}

{body['opening']}

{body['request']}

My account number is {ACCOUNT_DETAILS['billing_number']}.
My ID number is {ACCOUNT_DETAILS['id_number']}.
My phone number is {ACCOUNT_DETAILS['phone_number']}.
My email is {ACCOUNT_DETAILS['email']}.

{body['confirmation']}

Please send the official paid-up letter to my email address: {ACCOUNT_DETAILS['email']}.

{body['urgency']}

{body['closing']}

Best regards,
{ACCOUNT_DETAILS['name']}
"""

def create_email():
    """Create the email message."""
    msg = MIMEMultipart()
    msg['From'] = ACCOUNT_DETAILS['email']
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"Request for Paid-Up Letter - {ACCOUNT_DETAILS['billing_number']} ({random.randint(1000, 9999)})"
    msg.attach(MIMEText(generate_body(), 'plain'))

    return msg

def send_email():
    """Send email with randomized timing patterns and enhance status checks."""
    global retry_count
    try:
        msg = create_email()
        recepient = [email.strip() for email in RECIPIENT_EMAIL.split(',')]
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            time.sleep(random.uniform(0.5, 2.5))
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            time.sleep(random.uniform(1.0, 5.0))
            print(RECIPIENT_EMAIL)
            server.sendmail(EMAIL_USER, recepient, msg.as_string())
        
        email_id = msg['Subject'].split()[-1]
        timestamp = time.ctime()
        print(f"{timestamp} - Email send successfully to {RECIPIENT_EMAIL} with ID: {email_id}")

        logging.info(f"Email sent successfully to {RECIPIENT_EMAIL} with ID: {email_id}")
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        print(f"Authentication failed for {EMAIL_USER}.")
        logging.error(f"Authentication failed for {EMAIL_USER}.")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        logging.error(f"SMTP error occurred: {e}")
        retry_count += 1
        if retry_count > 3:
            print("Maximum retry attempts reached. Exiting.")
            logging.error("Maximum retry attempts reached. Exiting.")
            exit(1)
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")
        return False
    finally:
        retry_count += 1
        return False

def main_loop():
    """Main loop to send emails at random intervals."""
    global emails_sent
    attempt = 0

    while True:
        success = send_email()
        if 1:
            emails_sent += 1
            attempt = 0
            base_interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            interval = base_interval * (1 + random())
            print(f"Waiting for {interval} seconds before sending the next email.")
            time.sleep(interval)
        else:
            attempt = min(attempt + 1, 5)
            backoff = (2 ** attempt) + random.random()*30
            print(f"Waiting for {backoff:.1f} seconds before retrying.")
            time.sleep(backoff)

if __name__ == "__main__":
    print("Starting email sending process.")
    print("Press Ctrl+C to stop the process.")
    try:
        main_loop()
    except KeyboardInterrupt:
        print(f"\n{'='*40}")
        print(f"{'Email process Summary':^40}")
        print(f"{'='*40}")
        print(f"Total emails sent: {emails_sent}")
        print(f"Total delivery attempts made: {retry_count + emails_sent}")
        print(f"Total failed attempts: {retry_count}")
        print(f"{'='*40}")
        exit(0)


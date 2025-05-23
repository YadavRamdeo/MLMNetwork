import random
import requests
import string
import smtplib
from email.message import EmailMessage
from django.contrib.auth.models import User
import os

def generate_random_password(length: int):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def send_gmail(receiver_gmail: str, subject: str, message: str):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(
            os.environ.get('EMAIL_HOST_USER', 'ewebusinessewe@gmail.com'),
            os.environ.get('EMAIL_HOST_PASSWORD', 'qkyjfpyvwgokiwsl')
        )
        email = EmailMessage()
        email['From'] = "Easy Way Earn"
        email['To'] = receiver_gmail
        email['Subject'] = subject
        email.set_content(message)
        server.send_message(email)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.quit()

def generate_username():
    """ Generates a unique username starting with 'EWE' followed by random digits. """
    while True:
        username = f"EWE{''.join(random.choices(string.digits, k=6))}"
        if not User.objects.filter(username=username).exists():
            return username

def create_otp(digits: int):
    return random.randint(10**(digits - 1), 10**digits - 1)

API_URL = "https://mrobotics.in/api/recharge"
API_TOKEN = os.environ.get('RECHARGE_API_TOKEN', '0c5b76e1-c06b-4a8f-a5cb-c7102d9ca11b')

def create_order_id(digits: int):
    return random.randint(10**(digits - 1), 10**digits - 1)

def recharge_mobile(mobile_no, amount, company_name, order_id, is_stv=False):
    company_ids = {
        "vi": 1,
        "airtel": 2,
        "bsnl": 4,
        "jio": 5
    }
    company_id = company_ids.get(company_name.lower(), None)
    
    data = {
        "api_token": API_TOKEN,
        "mobile_no": mobile_no,
        "amount": amount,
        "company_id": company_id,
        "order_id": order_id,
        "is_stv": str(is_stv).lower()
    }
    
    try:
        response = requests.post(API_URL, data=data)
        return response.json()
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def check_recharge_status(mobile_no, amount, company_name, order_id, is_stv=False):
    company_ids = {
        "Vodafone": 1,
        "Airtel": 2,
        "Idea": 3,
        "Bsnl": 4,
        "Jio": 5
    }
    
    company_id = company_ids.get(company_name)
    if company_id is None:
        return {"error": "Invalid company name"}
    
    url = (f"https://mrobotics.in/api/recharge_get?api_token={API_TOKEN}"
           f"&mobile_no={mobile_no}&amount={amount}&company_id={company_id}"
           f"&order_id={order_id}&is_stv={str(bool(is_stv)).lower()}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": "API request failed", "details": str(e)}

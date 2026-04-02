import re

def validate_name(name):
    return re.match(r'^[A-Za-z ]{2,}$', name)

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def validate_phone(phone):
    return re.match(r'^\d{10}$', phone)

def validate_password(password):
    return re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password)

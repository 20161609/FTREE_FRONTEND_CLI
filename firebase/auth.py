import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASIC_URL = os.getenv('BASIC_URL')

# sign in the user
def signin(email: str, password: str):
    # Request to the server to get the user data
    url = f"{BASIC_URL}/auth/signin/"
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(url, json=payload)
    response_data = response.json()

    # Check the response status and return the user data
    try:
        if response.status_code == 200:
            if response_data['status'] == True:
                return {
                    "status":True,
                    "id_token": response_data['id_token'],
                    "email": response_data['email'],
                    "name": response_data['name']
                }
            else:
                return {"status": False, "message": response_data['message']}
        else:
            return {"status": False, "message": response_data['message']}
    except Exception as e:
        return {"status": False, "message": str(e)}

# sign up the user
def signup(email: str, password: str, name: str, code: str):
    try:
        # Request to the server to create a new user
        userSignUp = {
            "email":email, 
            "password":password, 
            "name":name, 
            "code":code # verification for the email
        }
        url = f"{BASIC_URL}/auth/signup/"
        response = requests.post(url, json=userSignUp)
        response_data = response.json()

        # Check the response status
        if response.status_code == 200:
            return {"status":True, "message":"success"}
        else:
            return {"status":False, "message": response_data['detail']}
    except Exception as e:
        return {"status":False, "message":str(e)}

# send the verification email
def send_vefication_email(email):
    try:
        # Request to the server to send the verification email
        url = f"{BASIC_URL}/auth/send-code/?email={email}"
        response = requests.post(url)
        response_data = response.json()
        if response.status_code == 200:
            return {"status":True, "message":response_data['message']}
        else:
            return {"status":False, "message":response_data['message']}
    except Exception as e:
        return {"status":False, "message":str(e)}

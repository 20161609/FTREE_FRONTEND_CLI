import requests
import mimetypes
from datetime import datetime
import os
from dotenv import load_dotenv
from PIL import Image, ImageTk
from tkinter import filedialog

load_dotenv()
BASIC_URL = os.getenv('BASIC_URL')

# get the tree with ID token
def upload_transaction(
        id_token, t_date, branch, cashflow, description, file_path=None):

    # Get Image file indicating receipt
    if not file_path:
        print("...[INFO] No file selected")
        file = None
    else:
        print("...[INFO] File selected:", file_path)
        file = open(file_path, 'rb')

    files = {'receipt': file} if file else None
    data = {
        't_date': t_date, 'branch': branch, 'cashflow': cashflow,
        'id_token': id_token, 'description': description
    }

    # Send the transaction data to the server
    url = f"{BASIC_URL}/transaction/upload-transaction/"
    response = requests.post(url, data=data, files=files)
    response_data = response.json()

    # Check the response
    if response.status_code == 200:
        if response_data['status'] == False:
            print("...[ERROR]", response_data['message'])
        else:
            print("...[SUCCESS]", response_data['message'])
    else:
        print("[ERROR] Upload failed")
        print(response_data)
        return None

def upload_transaction2(id_token, branch):
    # Get Image file indicating receipt
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
    )
    if not file_path:
        print("...[INFO] No file selected")
        file = None
    else:
        print("...[INFO] File selected:", file_path)
        file = open(file_path, 'rb')

    files = {'receipt': file} if file else None
    t_date = input("Enter the date of the transaction (YYYY-MM-DD): ")
    cashflow = int(input("Enter the cashflow of the transaction: "))
    description = input("Enter the description of the transaction: ")
    data = {
        't_date': t_date, 'branch': branch, 'cashflow': cashflow,
        'id_token': id_token, 'description': description
    }

    # Send the transaction data to the server
    url = f"{BASIC_URL}/transaction/upload-transaction/"
    response = requests.post(url, data=data, files=files)
    response_data = response.json()

    # Check the response
    if response.status_code == 200:
        if response_data['status'] == False:
            print("...[ERROR]", response_data['message'])
        else:
            print("...[SUCCESS]", response_data['message'])
    else:
        print("[ERROR] Upload failed")
        print(response_data)
        return None


import requests
import mimetypes
from lib_box.santizer import*
from prettytable import PrettyTable
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

def refer_transaction_daily(id_token, branch="00000000Home", begin_date='0001-01-01', end_date='9999-12-31'):
    response = get_transaction_daily(id_token, branch, begin_date, end_date)

    if response.status_code == 200:
        if response.json()['status'] == False:
            print("...[ERROR]", response.json()['message'])
            return None
        else:
            # Get Transaction from the response
            history = response.json()['message']
            if len(history) == 0:  # No data
                print("...[INFO] No Transaction data")
                return response.json()

            # Print the Transaction data
            print("...[SUCCESS]", "Successfully referred")            
            table = PrettyTable()
            table.field_names = ['T-id', 'When', 'Branch', 'Income', 'Expenditure', 'Balance','Description', 'Receipt', 'Date-created']
            total_in, total_out, balance = 0, 0, 0

            # Iterate the history and print table row
            for record in history:
                tid = record['tid']
                when = record['t_date']
                branch = '/'.join([b[8::] for b in record['branch'].split('/')])
                income = record['cashflow'] if record['cashflow'] > 0 else 0
                expenditure = -record['cashflow'] if record['cashflow'] < 0 else 0

                total_in += record['cashflow'] if record['cashflow'] > 0 else 0
                total_out += -record['cashflow'] if record['cashflow'] < 0 else 0
                balance += record['cashflow']
                description = record['description']
                receipt = 'Yes' if record['receipt'] else 'No'
                c_date = record['c_date']

                row = [tid, when, branch, 
                       format_cost(income), 
                       format_cost(expenditure), 
                       format_cost(balance), 
                       description, receipt, c_date]
                
                table.add_row(row)
                continue

            # Print the summary
            print(table)
            print("\n*** Summary ***")
            print("- Branch: {}".format(branch))
            print("- Period: {} ~ {}".format(begin_date, end_date))
            print("- Count: {}".format(len(history)))
            print("- Total In: {}".format(format_cost(total_in)))
            print("- Total Out: {}".format(format_cost(total_out)))
            print("- Balance: {}".format(format_cost(balance)))
            print()
            
                
            return response.json()
    else:
        print("...[ERROR] Upload failed")
        print(response.json())
        return None

def get_transaction_daily(id_token, branch="00000000Home", begin_date='0001-01-01', end_date='9999-12-31'):
    url = f"{BASIC_URL}/transaction/refer-daily/"
    return requests.get(url, data={
        'id_token': id_token, 
        'branch': branch,
        'begin_date': begin_date, 'end_date': end_date
    })

def refer_transaction_monthly(id_token, branch="00000000Home", begin_date='0001-01-01', end_date='9999-12-31'):
    data = {
        'id_token': id_token, 
        'branch': branch,
        'begin_date': begin_date, 'end_date': end_date
    }
    url = f"{BASIC_URL}/transaction/refer-monthly/"
    response = requests.get(url, data=data)
    response_data = response.json()
    if response.status_code == 200:
        if response_data['status'] == False:
            print("...[ERROR]", response_data['message'])
            return None
        else:
            # Get Transaction from the response
            history = response_data['message']
            if len(history) == 0:  # No data
                print("...[INFO] No Transaction data")
                return response_data

            # Print the Transaction data
            print("...[SUCCESS]", "Successfully referred")            
            table = PrettyTable()
            table.field_names = ['Monthly', 'Branch', 'Income', 'Expenditure', 'Balance']
            total_in, total_out, balance = 0, 0, 0

            branch = './'.join([b[8::] for b in branch.split('/')])
            # Iterate the history and print table row
            for record in history:
                monthly = (record['monthly'])
                income = record['income']
                expenditure = record['expenditure']
                
                total_in += record['income']
                total_out += record['expenditure']
                balance += income - expenditure

                row = [monthly, branch, 
                       format_cost(income), 
                       format_cost(expenditure), 
                       format_cost(balance)
                       ]
                
                table.add_row(row)
                continue

            # Print the summary
            print(table)
            print("\n*** Summary ***")
            print("- Branch: {}".format(branch))
            print("- Period: {} ~ {}".format(begin_date, end_date))
            print("- Total In: {}".format(format_cost(total_in)))
            print("- Total Out: {}".format(format_cost(total_out)))
            print("- Balance: {}".format(format_cost(balance)))
            print()
            
                
            return response_data
    else:
        print("...[ERROR] Upload failed")
        print(response_data)
        return None

def delete_transaction(id_token:str, tid:int):
    url = f"{BASIC_URL}/transaction/delete-transaction/"
    response = requests.delete(url, data={'id_token':id_token,'tid': tid})
    response_data = response.json()
    
    if response.status_code == 200:
        if response_data['status'] == False:
            print("...[ERROR]", response_data['message'])
            return None
        else:
            print("...[SUCCESS]", response_data['message'])
            return response_data
    else:
        print("...[ERROR] Upload failed")
        print(response_data)
        return None

{'status': True, 
 'message': [{
     'tid': 7, 
     't_date': '2024-01-12', 
     'branch': '00000000Home/00000001manage/00000001CM_ACTIVITY', 
     'cashflow': -123049, 
     'description': 
     'fmekk', 
     'receipt': 'sIzCjnPBWrY3aHr9bV5t1OT8TVs1_1726158229_6e6ea4.jpeg', 
     'c_date': '2024-09-13T01:23:49.488787', 
     'uid': 'sIzCjnPBWrY3aHr9bV5t1OT8TVs1'}, {'tid': 8, 't_date': '2024-01-14', 'branch': '00000000Home/00000001manage/00000001CM_ACTIVITY', 'cashflow': -4800, 'description': 'knkfle', 'receipt': 'sIzCjnPBWrY3aHr9bV5t1OT8TVs1_1726158258_06aa16.jpeg', 'c_date': '2024-09-13T01:24:18.964483', 'uid': 'sIzCjnPBWrY3aHr9bV5t1OT8TVs1'}, {'tid': 9, 't_date': '2024-01-21', 'branch': '00000000Home/00000001manage/00000001CM_ACTIVITY', 'cashflow': -4090, 'description': 'mlmlwe', 'receipt': 'sIzCjnPBWrY3aHr9bV5t1OT8TVs1_1726158279_6885a2.jpeg', 'c_date': '2024-09-13T01:24:39.686991', 'uid': 'sIzCjnPBWrY3aHr9bV5t1OT8TVs1'}]}
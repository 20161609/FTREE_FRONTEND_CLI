import getpass
import tkinter as tk
from transaction.upload_window import TransactionUploader
from firebase.auth import signin, signup, send_vefication_email
from firebase.tree import get_tree, update_tree, make_children_list, get_absolute_path, get_path_list
from firebase.tree import get_firebase_path

class Shell:
    def __init__(self):
        print("\"Welcome to F-tree\"")
        self.id_token = None
        self.email = None
        self.name = None
        self.branch = None
        self.mode = 'Viewer'
        self.tree = None
        self.prompt = f"\n[{self.mode}] ~ #{self.branch}\n{self.email}:~$ "
        self.renew_prompt()

    def renew_prompt(self):
        if self.email == None:
            email = 'Guest'
        else:
            email = self.email

        if self.branch != None:
            branch = self.branch[::]
        else:
            branch = 'None'
        self.prompt = f'\n[{self.mode}] ~ {email} #{branch}/\n$ '

    def fetch(self, command):
        try:
            list_cmd = command.split()
            if len(list_cmd) == 1: # 1 words command
                if list_cmd[0] in ['signin', 'login']:
                    self.signin()
                elif list_cmd[0] in ['signout', 'logout']:
                    self.signout()
                elif list_cmd[0] in ['signup', 'join', 'register']:
                    self.signup()
                elif list_cmd[0] == 'user':
                    self.user_info()
                elif list_cmd[0] == 'mode':
                    self.modify_mode()
                elif list_cmd[0] == 'test':
                    self.test()
                elif list_cmd[0] in ['insert', 'in']:
                    self.insert()
            elif len(list_cmd) == 2: # 2 words command
                if list_cmd[0] == 'mkdir':
                    self.mkdir(list_cmd[1])
                elif list_cmd[0] in ['cd', 'chdir']:
                    self.chdir(list_cmd[1])
                elif list_cmd[0] in ['list', 'ls']:
                    if list_cmd[1] in ['-dir', '-directory']:
                        self.list_children()
                    elif list_cmd[1] in ['-cf', '-cashflow']:
                        self.list_cashflow()
                        pass

        except Exception as e:
            error_message = f'on fetch,\n{e}'
            print('...[ERROR]:', error_message)
            pass

        self.renew_prompt()

    def signin(self):
        if self.id_token != None:
            print("...[ERROR] You are already logged in.")
            return
        email = input("...[INPUT] Email: ")
        password = getpass.getpass("...[INPUT] Password: ")
        res = signin(email, password)
        if res['status']:
            self.id_token = res['id_token']
            self.email = res['email']
            self.name = res['name']
            self.branch = 'Home'
            self.mode = "Viewer"
            self.tree = get_tree(self.id_token)
            print(f"Successfully signin has been complete ({self.name})!")
        else:
            error_message = f"on signin, {res['message']}"
            print(f"...[ERROR]", error_message)

    def signout(self):
        self.id_token = None
        self.email = None
        self.name = None
        self.branch = None
        self.mode = 'Viewer'
        self.tree = None
        self.prompt = f"\n[{self.mode}] ~ #{self.branch}\n{self.email}:~$ "
        print("Logged out")

    def signup(self):
        if self.id_token == None:
            print("==========")
            print("Sign up")
            print("==========")
            email = input("...[INPUT] Email: ")
            name = input("...[INPUT] Name: ")
            password = getpass.getpass("...[INPUT] Password: ")
            res_sendemail = send_vefication_email(email)
            if res_sendemail['status'] == False:
                print("...[ERROR]", res_sendemail['message'])
                return
            
            code = input("...[INPUT] Enter the verification code sent to your email: ")

            res = signup(email, password, name, code)
            if res['status'] == True:
                print(res['message'])
                res_signin = signin(email, password)

                self.id_token = res_signin['id_token']
                self.email = res_signin['email']
                self.name = res_signin['name']

                self.branch, self.mode = 'Home', "Viewer"

                self.tree = get_tree(self.id_token)
        else:
            print("...[ERROR] You are already logged in.")
        
    def user_info(self):
        print('.')
        print(f"Name: {self.name}")
        print(f"Email: {self.email}")
        print('.')

    def modify_mode(self):
        if self.id_token:
            if self.mode == 'Viewer':
                self.mode = 'Editor'
            else:
                self.mode = 'Viewer'
        else:
            print("...[ERROR] You are not logged in.")

    def mkdir(self, new_branch):
        # Make child directory on the current branch
        if self.id_token == None:
            print("...[ERROR] You are not logged in.")
        elif self.mode == "Viewer":
            print("...[ERROR] You are not in the Editor mode.")
        elif self.mode == "Editor":
            firebase_path = get_firebase_path(self.tree, self.branch)
            update_tree(self.id_token, firebase_path, new_branch)
            self.tree = get_tree(self.id_token)
        return

    def list_children(self):
        make_children_list(self.tree, self.branch)

    def chdir(self, branch):
        # Check login status
        if self.id_token == None:
            print("...[ERROR] You are not logged in.")
            return

        # make path
        branch_depth = len(self.branch.split('/'))
        back_motion_count = 0
        for node in branch.split('/'):
            if node == '..':
                back_motion_count += 1
            else:
                break
        base_path_depth = max(branch_depth - back_motion_count, 1)
        base_path = '/'.join(self.branch.split('/')[:base_path_depth:])
        base_path += ''.join([f'/{node}' for node in branch.split('/')[back_motion_count:]])
        base_path = base_path[:-1] if base_path[-1] == '/' else base_path
        path = get_absolute_path(tree=self.tree, path=base_path)

        if path:
            self.branch = path
        else:
            print("...[ERROR] Invalid path")

    def insert(self):
        if not self.id_token:
            print("...[ERROR] You are not logged in.")
            return
        if self.mode == "Viewer":
            print("...[ERROR] You are not in the Editor mode.")
            return
        
        path_list = get_path_list(self.tree, self.branch)
        TransactionUploader(
            branch_options=path_list, 
            branch_path=self.branch, 
            id_token=self.id_token
        )

    def delete(self):
        pass

    def test(self):
        print("...[TEST]")
        path_list = get_path_list(self.tree, self.branch)
        TransactionUploader(
            branch_options=path_list, 
            branch_path=self.branch, 
            id_token=self.id_token
        )

        # upload_transaction(self.id_token, self.branch)

    def list_cashflow(self):
        print(self.branch)
        d = get_firebase_path(self.tree, self.branch)
        print(d)

        pass

{
    'Children': {
        '00000001manage': {'Children': 'None', 'MaxIndex': 0}, 
        '00000002event': {'Children': 'None', 'MaxIndex': 0}, 
        '00000003overhead': {'Children': 'None', 'MaxIndex': 0}
    },
    'MaxIndex': 3
}
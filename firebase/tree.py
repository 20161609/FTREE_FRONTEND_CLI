from collections import deque
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASIC_URL = os.getenv('BASIC_URL')

# get the tree with ID token
def get_tree(id_token):
    try:
        # Request to the server to get the tree
        token_box = {"id_token":id_token}
        url = f"{BASIC_URL}/tree/get-tree/"
        response = requests.post(url, json=token_box)
        response_data = response.json()

        # Check the response status and return the tree
        if response.status_code == 200:
            tree = response_data['message']
            return tree
        else:
            return None
    except Exception as e:
        print(e)
        return None

# create child branch on current branch
def update_tree(id_token, branch, new_branch):
    try:
        # Request to the server to update the tree
        url = f"{BASIC_URL}/tree/update-tree/"
        update_tree_req = {
            "branch": branch,
            "new_branch": new_branch,
            "id_token": id_token,
        }
        response = requests.post(url, json=update_tree_req)
        response_data = response.json()

        # Check the response status
        if response.status_code == 200:
            if response_data['status'] == True:
                print("...[SUCCESS] Branch created")
                return True
            else:
                print("...[ERROR] Branch creation failed\n",response_data['message'])
                return False
        else:
            print("...[ERROR] Fault..\n", response_data['message'])
            return False
    except Exception as e:
        print("...[ERROR] Unexpected->", e)
        return False
    
# Show the children list of the current branch
def make_children_list(tree, branch):
    # Check the children list of the current branch
    try:
        node = tree
        for node_name in branch.split('/')[1::]:
            IS_VALID = False
            for s in node['Children']:
                if node_name == s[8::]:
                    node = node['Children'][s]
                    IS_VALID = True
                    break
                
            if not IS_VALID:
                print('...[ERROR] No such branch')
                return
    except Exception as e:
        print(f"...[ERROR] {e}")
        return

    # Print the children list
    if node['Children'] != "None":
        children_list = list(node['Children'].keys())
        children_list.sort()
        print("...[INFO] child branches from the current branch")
        for i, child in enumerate(children_list):
            if len(child) > 8:
                print(f"{i+1}. {child[8::]}")
    else:
        print("...[INFO] No children branch")
    return

# Check the validity of the path and Return absolute path to use in firebase
def get_absolute_path(tree, path):
    absolute_path = 'Home'
    node = tree
    for node_name in path.strip().split('/')[1::]:
        if node_name.isdigit():
            index = int(node_name)
            if index > len(node['Children']) or index < 1:
                # Invalid Path: Index out of range
                print('...[ERROR] Index out of range')
                return None
            node_name = list(node['Children'].keys())[index-1][8::]

        IS_VALID = False
        for s in node['Children']:
            if node_name == s[8::]:
                absolute_path += '/' + node_name
                node = node['Children'][s]
                IS_VALID = True
                break
        if not IS_VALID:
            # Invalid Path: No such branch
            return
        
    return absolute_path

# Get the firebase path from the tree and the path
def get_firebase_path(tree, path):
    firebase_path = '00000000Home'
    node = tree
    for node_name in path.strip().split('/')[1::]:
        print("BLOCK", node_name)
        IS_VALID = False
        for s in node['Children']:
            if node_name == s[8::]:
                firebase_path += '/' + s
                node = node['Children'][s]
                IS_VALID = True
                break
        if not IS_VALID:
            return None  
    return firebase_path

# Get the path list from the tree
def get_path_list(node, path='Home'):
    path_list = []
    box = [path, node]
    queue = deque([box])

    while queue:
        path, node = queue.pop()
        if node['Children'] != "None":
            for child in list(node['Children'])[::-1]:
                new_path = path + '/' + child[8::]
                new_node = node['Children'][child]
                queue.append([new_path, new_node])
        path_list.append(path)
    return path_list
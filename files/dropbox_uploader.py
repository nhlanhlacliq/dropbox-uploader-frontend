"""Upload all contents and structure of this folder(that this script is in) to Dropbox."""

# Module Imports
from dropbox import Dropbox
from dropbox import dropbox_client
from dropbox import exceptions
from dropbox import files
from getpass import getpass             #Used to hide password(API key) input
from time import sleep                  #Terminal 'typography'
import sys                              
import os                               #Used to retreive current directory

# Add files to ignore here (this script is added on in the main method)
IGNORE_LIST = ['example.txt']


"""Handles user token(api key), dropbox account, and uploading to the dropbox account"""
class DropboxInterface():
    # User app access token and Dropbox api object
    TOKEN = None
    DBX = None

    # On construction, get user token and initialize dropbox object
    def __init__(self):
        print("================================\nThis will upload the current folder to your dropbox account.")
        print("Please be wary of your storage limit.\n================================")
        self.get_user_token()
        self.DBX = Dropbox(self.TOKEN, timeout=None)
    
    # Retrive user token(API key) token from user
    def get_user_token(self): 
        print("Paste (Ctrl+V / Ctrl+Shift+V) your api token key here (hidden)")
        TOKEN = getpass(stream=sys.stderr)
        self.TOKEN = TOKEN
        if len(TOKEN) < 1:
            return access_error("\nNo input received. Please ensure your token is copied, then try again.\n")

    # Reurns user name from dropbox acount
    def get_user_name(self):
        user_account = self.DBX.users_get_current_account()
        return user_account.name.familiar_name
    
    # Upload file to dropbox account(to dropbox_path. User is asked to confirm this). Overwrites existing files.
    def upload(self, file, dropbox_path, mode = files.WriteMode.overwrite):
        with open(file, 'rb') as f:
            self.DBX.files_upload(f.read(), dropbox_path, mode, mute=True)

"""Handles local directory(containing content to be uploaded), and
Dropbox directory name where content is uploaded to
"""
class Directory():
    dropbox_directory = ''
    local_directory = ''

    # On construction, initialize local directory and dropbox directory
    def __init__(self):
        local_directory = os.path.dirname(os.path.abspath(__file__))
        local_directory = local_directory.replace("\\","/")
        
        dropbox_directory = local_directory.split('/')[-1]
        
        self.set_dropbox_directory(dropbox_directory)
        self.set_local_directory(local_directory)

    def get_dropbox_directory(self):
        return self.dropbox_directory
    
    def set_dropbox_directory(self, dropbox_directory):
        self.dropbox_directory = dropbox_directory

    # Called if user chooses to rename upload folder
    def update_dropbox_directory(self):
        while True:
            dropbox_directory = input("Dropbox directory name:\n> ")
            if len(dropbox_directory) > 0:
                break
            else:
                print("\nNo input detected. Please try again")
        return self.set_dropbox_directory(dropbox_directory)

    def get_local_directory(self):
        return self.local_directory
    
    def set_local_directory(self, local_directory):
        self.local_directory = local_directory

"""Displays error if token is invalid,
otherwise greet user and resume."""
def verify_account(dropbox_interface):
    try:
        print(f"\nHello, {dropbox_interface.get_user_name()}!\n")
    except (exceptions.BadInputError, dropbox_client.BadInputException, exceptions.AuthError) as err :
        return access_error(
            f"\nPlease ensure you have copied your api token and that it hasn't expired.\nERROR: {err.message}\n")
    sleep(1)

"""Displays access error message and restarts script if access token is invalid"""
def access_error(message):
    print(message)
    sleep(2)
    return main()

"""Confirms dropbox directory (before upload)"""
def confirm_dropbox_directory(directories):
    print(f"Current directory: \"{directories.get_dropbox_directory()}\"\n")
    sleep(1)

    # keep dbx directory name...
    print("The Dropbox directory will have the same name. Is that alright?")
    while True:
        option = input("1: yes\n2: no\n> ")
        if option.isdigit() and 0 < int(option) <= 2:
            break
        else:
            print("Invalid input. Please try again (1 / 2)")
    # ... or rename
    if int(option) == 2:
        directories.update_dropbox_directory()
    sleep(1)

"""Uploads files"""
def start_upload(dropbox_interface, directory, ignore_list):
    print(f"\n...Uploading to {directory.get_dropbox_directory()}...\n")
    
    # get local and dropbox directories.
    dropbox_dir = f'/{directory.get_dropbox_directory()}'
    local_dir = directory.get_local_directory()

    # Iterate though files in local directory
    for subdir, dirs, files in os.walk(local_dir):
        for file in files:
            # skip files in ignore list
            if file in ignore_list:
                print(f"Skipping this file({file})\n")
                continue

            # construct local file path
            local_file_path = os.path.join(subdir, file)
            local_file_path = local_file_path.replace('\\','/')

            # construct dropbox path using local relative path
            local_rel_path = os.path.relpath(local_file_path, local_dir)
            local_rel_path = local_rel_path.replace('\\','/')
            dropbox_path = os.path.join(dropbox_dir, local_rel_path)
            dropbox_path = dropbox_path.replace('\\','/')

            # print file details(name, size, locations)
            print(f"File : {file}")
            print(f"Size : {os.path.getsize(local_file_path)} bytes")
            print(f"From : {(local_file_path[:75]+'..') if len(local_file_path)>75 else local_file_path}")
            print(f"To   : {(dropbox_path[:75]+'..') if len(dropbox_path)>75 else dropbox_path}\n")
            
            # Upload file using dropbox interface
            dropbox_interface.upload(local_file_path, dropbox_path)

    print("Upload complete.\n")
    sleep(1)

"""Main method"""
def main():
    # Access dropbox account
    dropbox_interface = DropboxInterface()
    verify_account(dropbox_interface)
    
    # Construct and confirm directory
    directories = Directory()
    confirm_dropbox_directory(directories)

    # Add this script to ignore list
    script_name = __file__.split('\\')[-1]
    IGNORE_LIST.append(script_name)
    
    # Upload files
    start_upload(dropbox_interface, directories, IGNORE_LIST)
    sys.exit(0)

if __name__ == '__main__':
    main()
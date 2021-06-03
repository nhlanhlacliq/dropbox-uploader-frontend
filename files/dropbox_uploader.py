"""Upload all contents and structure of this folder(that this script is in) to Dropbox."""

from dropbox import Dropbox
from dropbox import dropbox_client
from dropbox import exceptions
from dropbox import files
from getpass import getpass
from time import sleep
import sys
import os

# files to ignore(this script is added)
IGNORE_LIST = ['example.txt']


"""Handles user token, dropbox account and uploading to the dropbox account"""
class DropboxInterface():
    # User app access token and Dropbox api object
    TOKEN = None
    DBX = None

    # On construction, get user token, initialize dropbox object
    def __init__(self, token):
        # print("================================\nThis will upload the current folder to your dropbox account.")
        # print("Please be wary of your storage limit.\n================================")
        self.TOKEN = token
        self.DBX = Dropbox(self.TOKEN, timeout=None)
    
    # Deprecated
    def get_user_token(self): 
        print("Paste (Shift + Ctrl + V) your api token key here (hidden)")
        TOKEN = getpass(stream=sys.stderr)
        self.TOKEN = TOKEN
        if len(TOKEN) < 1:
            return access_error("\nNo input received. Please ensure your token is copied, then try again.\n")

    def get_user_name(self):
        user_account = self.DBX.users_get_current_account()
        return user_account.name.familiar_name
    
    # Upload file to dropbox account. Overwriting if neccessary
    def upload(self, file, dropbox_path, mode = files.WriteMode.overwrite):
        with open(file, 'rb') as f:
            self.DBX.files_upload(f.read(), dropbox_path, mode, mute=True)

"""Handles current directory(of content to be uploaded).
Also handles upload folder name where content is uploaded to
"""
class Folder():
    name = ''
    directory = ''

    # On construction, initializes currect directory and name of upload folder
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = current_directory.replace("\\","/")
        folder_name = current_directory.split('/')[-1]
        self.set_name(folder_name)
        self.set_directory(current_directory)

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    # Called if user chooses to rename upload folder
    def update_name(self):
        while True:
            name = input("Folder name(in Dropbox):\n> ")
            if len(name) > 0:
                break
            else:
                print("\nNo input detected. Please try again")
        return self.set_name(name)

    def get_directory(self):
        return self.directory
    
    def set_directory(self, directory):
        self.directory = directory

"""Displays error if token is invalid,
otherwise greet user and resume."""
def verify_account(dropbox_interface):
    try:
        print(f"\nHello, {dropbox_interface.get_user_name()}!\n")
    except (exceptions.BadInputError, dropbox_client.BadInputException, exceptions.AuthError) as err :
        return access_error(
            f"\nPlease ensure you have copied your api token and that it hasn't expired.\nERROR: {err.message}\n")
    sleep(1)

"""Displays error message and restart script if access token is invalid"""
def access_error(message):
    print(message)
    sleep(2)
    return main()

"""Confirms upload folder before upload"""
def confirm_upload_folder(folder):
    print(f"Current folder: \"{folder.get_name()}\"\n")
    sleep(1)

    # keep upload folder name...
    print("Your Dropbox folder shall have the same name. Is that alright?")
    while True:
        option = input("1: yes\n2: no\n> ")
        if option.isdigit() and 0 < int(option) <= 2:
            break
        else:
            print("Invalid input. Please try again")
    # ... or rename upload folder
    if int(option) == 2:
        folder.update_name()
    sleep(1)

def start_upload(dropbox_interface, folder, ignore_list):
    print(f"\n...Uploading to {folder.get_name()}...\n")
    # initialize current and upload directiory.
    upload_dir = f'/{folder.get_name()}'
    currentdir = folder.get_directory()

    # Iterate though files in current directory
    for subdir, dirs, files in os.walk(currentdir):
        for file in files:
            # skip files in ignore list
            if file in ignore_list:
                print(f"Skipping this file({file})\n")
                continue
            # construct file path
            file_path = os.path.join(subdir, file)
            file_path = file_path.replace('\\','/')
            # construct full upload(Dropbox) path using current path
            relative_path = os.path.relpath(file_path, currentdir)
            relative_path = relative_path.replace('\\','/')
            dropbox_path = os.path.join(upload_dir, relative_path)
            dropbox_path = dropbox_path.replace('\\','/')
            # print file details(name, size, locations) and call upload method from dropbox interface
            print(f"File : {file}")
            print(f"Size : {os.path.getsize(file_path)} bytes")
            print(f"From : {(file_path[:75]+'..') if len(file_path)>75 else file_path}")
            print(f"To   : {(dropbox_path[:75]+'..') if len(dropbox_path)>75 else dropbox_path}\n")
            dropbox_interface.upload(file_path, dropbox_path)

    print("Upload complete.\n")
    sleep(1)

# Main method
def main():
    dropbox_interface = DropboxInterface()
    verify_account(dropbox_interface)
    
    folder = Folder()
    confirm_upload_folder(folder)

    # Add this script to ignore list
    script_name = __file__.split('\\')[-1]
    IGNORE_LIST.append(script_name)
    
    start_upload(dropbox_interface, folder, IGNORE_LIST)
    sys.exit(0)

if __name__ == '__main__':
    main()
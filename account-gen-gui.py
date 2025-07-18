import os
import sys
import webbrowser
import random
import binascii
import requests
import hashlib
import customtkinter as ctk
import base64
import logging
import json
from CTkMessagebox import CTkMessagebox
from CTkScrollableDropdown import CTkScrollableDropdown
from array import array
from struct import pack, unpack

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Helper functions
def swap_endian_u16(value):
    try:
        return unpack("<H", pack(">H", value))[0]
    except Exception as e:
        logging.error(f"Error in swap_endian_u16: {e}")
        raise

def swap_endian_u32(value):
    try:
        return unpack("<I", pack(">I", value))[0]
    except Exception as e:
        logging.error(f"Error in swap_endian_u32: {e}")
        raise

def calculate_crc16(data):
    try:
        crc = 0
        for c in data:
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
            crc ^= c
        return crc & 0xFFFF
    except Exception as e:
        logging.error(f"Error in calculate_crc16: {e}")
        raise

class Account:
    def __init__(self):
        try:
            self.m_persistent_id = 0x80000001

            # Generate a UUID
            self.m_uuid = [random.randint(0, 255) for _ in range(16)]

            # Calculate TransferableIdBase
            self.m_transferable_id_base = (0x2000004 << 32) | \
                                          (self.m_uuid[12] << 24) | \
                                          (self.m_uuid[13] << 16) | \
                                          (self.m_uuid[14] << 8) | \
                                          self.m_uuid[15]

            # Initialize MiiData with default values
            self.m_mii_data = array('B', [0] * 96)

            self.m_mii_data[0x00] = 0x01
            self.m_mii_data[0x01] = 0x00
            self.m_mii_data[0x02] = 0x01
            self.m_mii_data[0x03] = 0x10
            self.m_mii_data[0x04] = 0x00
            self.m_mii_data[0x05] = 0x00
            self.m_mii_data[0x06] = 0xC7
            self.m_mii_data[0x07] = 0xCD
            self.m_mii_data[0x08] = 0x03
            self.m_mii_data[0x09] = 0x00
            self.m_mii_data[0x0A] = 0x34
            self.m_mii_data[0x0B] = 0x33

            self.m_account_id = ""
            self.m_birth_year = 0
            self.m_birth_month = 0
            self.m_birth_day = 0
            self.m_gender = 0
            self.m_email = ""
            self.m_country = 0
            self.m_simple_address_id = 0
            self.m_principal_id = 0
            self.m_password_cache_enabled = 0
            self.m_account_password_cache = array('B', [0] * 32)
            self.m_mii_name = ""
        except Exception as e:
            logging.error(f"Error initializing Account: {e}")
            raise

    def set_mii_name(self, mii_name: str):
        try:
            logging.debug(f"Setting MiiName: {mii_name}")
            self.m_mii_name = mii_name
            # Encode the name as UTF-16BE (big-endian)
            mii_name_utf16 = mii_name.encode('utf-16be')
            # Ensure the name is exactly 20 bytes long, padded with null bytes if needed
            mii_name_padded = mii_name_utf16[:20] + b'\x00' * (22 - len(mii_name_utf16))
            # Convert to the correct endian format
            logging.debug(f"MiiName UTF-16BE: {mii_name_utf16.hex()}")
            logging.debug(f"MiiName padded: {mii_name_padded.hex()}")
            self.m_mii_data[0x1A:0x1A + 20] = array('B', mii_name_padded)
            # Set the final two bytes to 0x0000
            self.m_mii_data[0x2A:0x2C] = array('B', [0x00, 0x00])
        except Exception as e:
            logging.error(f"Error in set_mii_name: {e}")
            raise

    def set_principal_id(self, principal_id: int):
        try:
            logging.debug(f"Setting PrincipalID: {principal_id}")
            self.m_principal_id = principal_id
        except Exception as e:
            logging.error(f"Error in set_principal_id: {e}")
            raise

    def set_account_id(self, account_id: str):
        try:
            logging.debug(f"Setting AccountID: {account_id}")
            self.m_account_id = account_id
        except Exception as e:
            logging.error(f"Error in set_account_id: {e}")
            raise

    def set_email(self, email: str):
        try:
            logging.debug(f"Setting Email: {email}")
            self.m_email = email
        except Exception as e:
            logging.error(f"Error in set_email: {e}")
            raise

    def set_birth_date(self, year: int, month: int, day: int):
        try:
            logging.debug(f"Setting Birth Date: {year}-{month:02d}-{day:02d}")
            self.m_birth_year = year
            self.m_birth_month = month
            self.m_birth_day = day
        except Exception as e:
            logging.error(f"Error in set_birth_date: {e}")
            raise

    def set_gender(self, gender: int):
        try:
            logging.debug(f"Setting Gender: {gender}")
            self.m_gender = gender
        except Exception as e:
            logging.error(f"Error in set_gender: {e}")
            raise

    def set_country(self, country: dict):
        try:
            logging.debug(f"Setting Country: {country}")
            # Extract country ID as a string
            country_id = country.get("id", "0")
            self.m_country = int(country_id, 16)  # Convert to integer from hex
        except Exception as e:
            logging.error(f"Error in set_country: {e}")
            raise

    def set_region(self, region_code: str):
        try:
            logging.debug(f"Setting Region: {region_code}")
            self.m_simple_address_id = int(region_code, 16)
        except Exception as e:
            logging.error(f"Error in set_region: {e}")
            raise

    def set_password_cache_enabled(self, enabled: bool):
        try:
            logging.debug(f"Setting Password Cache Enabled: {enabled}")
            self.m_password_cache_enabled = 1 if enabled else 0
        except Exception as e:
            logging.error(f"Error in set_password_cache_enabled: {e}")
            raise

    def set_password_hash(self, password_hash: str):
        try:
            logging.debug(f"Setting Password Hash: {password_hash}")
            self.m_account_password_cache = array('B', bytes.fromhex(password_hash))
        except Exception as e:
            logging.error(f"Error in set_password_hash: {e}")
            raise

    def get_mii_data_hex(self):
        try:
            mii_data_hex = binascii.hexlify(self.m_mii_data).decode('utf-8')
            logging.debug(f"MiiData HEX: {mii_data_hex}")
            return mii_data_hex
        except Exception as e:
            logging.error(f"Error in get_mii_data_hex: {e}")
            raise
    
    def get_mii_name_hex(self):
        try:
            mii_name_utf16 = self.m_mii_name.encode('utf-16be')
            mii_name_padded = mii_name_utf16[:20] + b'\x00' * (22 - len(mii_name_utf16))
            mii_name_hex = binascii.hexlify(mii_name_padded).decode('utf-8')
            logging.debug(f"MiiName HEX: {mii_name_hex}")
            return mii_name_hex
        except Exception as e:
            logging.error(f"Error in get_mii_name_hex: {e}")
            raise
    
    def fetch_pid_from_pnid(self, pnid: str):
        try:
            url = f"https://pnidlt.gab.net.eu.org/api/v1/pnid/{pnid}"
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    logging.debug(f"API Response: {data}")
                    if isinstance(data, dict) and 'pid' in data and 'name' in data and 'data' in data:
                        return {'pid': data['pid'], 'mii_name': data['name'], 'mii_data': data['data']}
                    else:
                        raise ValueError("Unexpected response format")
                except ValueError:
                    raise ValueError("Invalid JSON response")
            else:
                raise ValueError(f"Failed to fetch PID from PNID. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error in fetch_pid_from_pnid: {e}")
            raise

    def set_mii_data(self, mii_data_base64: str):
        try:
            logging.debug(f"Setting MiiData: {mii_data_base64}")
            self.m_mii_data = array('B', base64.b64decode(mii_data_base64))
        except Exception as e:
            logging.error(f"Error in set_mii_data: {e}")
            raise

    def calculate_password_hash(self, pid: int, password: str) -> str:
        try:
            pid_bytes = pid.to_bytes(4, byteorder='little')
            static_bytes = bytes([2, 101, 67, 70])
            password_bytes = password.encode('utf-8')
            data = pid_bytes + static_bytes + password_bytes
            hash_bytes = hashlib.sha256(data).digest()
            password_hash = hash_bytes.hex()
            logging.debug(f"Calculated Password Hash: {password_hash}")
            return password_hash
        except Exception as e:
            logging.error(f"Error in calculate_password_hash: {e}")
            raise

    def generate_account_data(self):
        try:
            account_data = (
                f"AccountInstance_20120705\n"
                f"PersistentId={self.m_persistent_id:08x}\n"
                f"TransferableIdBase={self.m_transferable_id_base:x}\n"
                f"Uuid={''.join(f'{byte:02x}' for byte in self.m_uuid)}\n"
                f"MiiData={self.get_mii_data_hex()}\n"
                f"MiiName={self.get_mii_name_hex()}\n"
                f"AccountId={self.m_account_id}\n"
                f"BirthYear={self.m_birth_year:x}\n"
                f"BirthMonth={self.m_birth_month:x}\n"
                f"BirthDay={self.m_birth_day:x}\n"
                f"Gender={self.m_gender}\n"
                f"EmailAddress={self.m_email}\n"
                f"Country={self.m_country:x}\n"
                f"SimpleAddressId={self.m_simple_address_id:x}\n"
                f"PrincipalId={self.m_principal_id:08x}\n"
                f"IsPasswordCacheEnabled={self.m_password_cache_enabled}\n"
                f"AccountPasswordCache={binascii.hexlify(self.m_account_password_cache).decode('utf-8')}\n"
            )
            logging.debug(f"Generated Account Data: {account_data}")
            return account_data
        except Exception as e:
            logging.error(f"Error in generate_account_data: {e}")
            raise
    
    def save_to_file(self, filename: str):
        try:
            with open(filename, "w") as file:
                file.write(self.generate_account_data())
        except Exception as e:
            logging.error(f"Error in save_to_file: {e}")
            raise

# Load countries from the JSON file
json_path = resource_path("countries.json")

try:
    with open(json_path, "r", encoding="utf-8") as f:
        countries = json.load(f)
except Exception as e:
    logging.error(f"Failed to load country data: {e}")
    countries = {"None": {"id": "0", "regions": {"None": "0000000"}}}

def update_country_selection(selected_value):
    country_combobox.set(selected_value)
    update_region_dropdown(selected_value)

def update_region_dropdown(selected_country):
    # This function is automatically called with the selected country.
    if selected_country in countries:
        regions = list(countries[selected_country]['regions'].keys())
        # Update the values for the region dropdown.
        region_combobox.configure(values=regions)
        # Re-create the CTkScrollableDropdown with the new values
        region_dropdown = CTkScrollableDropdown(region_combobox, values=regions, justify="left", button_color="transparent")
        # Reset the selection
        if regions:
            region_combobox.set(regions[0])
        else:
            region_combobox.set("None")
    else:
        # If no valid country, set the region to "None".
        region_combobox.configure(values=["None"])
        # Re-create the CTkScrollableDropdown with the new "None" values
        region_dropdown = CTkScrollableDropdown(region_combobox, values=["None"], justify="left", button_color="transparent")
        region_combobox.set("None")

# Function to generate account data using the GUI inputs
def generate_account():
    try:
        pnid = pnid_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        birth_year = birth_year_entry.get()
        birth_month = birth_month_entry.get()
        birth_day = birth_day_entry.get()
        gender_text = gender_combobox.get()
        country_name = country_combobox.get()
        region_name = region_combobox.get()

        # Map the selected text to the corresponding gender value
        gender_mapping = {"None": 0, "Male": 1, "Female": 2}
        gender = gender_mapping[gender_text]

        # Map the selected country name to its dictionary
        country_code = countries[country_name]

        # Compute region_code from the country data and selected region name
        region_code = country_code['regions'].get(region_name, "0")

        # Validate the birth date
        if not (birth_year.isdigit() and birth_month.isdigit() and birth_day.isdigit()):
            raise ValueError("Birth year, month, and day must be numeric.")
        year = int(birth_year)
        month = int(birth_month)
        day = int(birth_day)
        if len(birth_month) != 2 or not (1 <= month <= 12):
            raise ValueError("Month must be between 01 and 12.")
        if not (1 <= day <= 31):
            raise ValueError("Day must be between 01 and 31.")
        
        # Create a new account
        account = Account()

        # Set account details
        account.set_account_id(pnid)
        account.set_email(email)
        account.set_birth_date(year, month, day)
        account.set_gender(gender)
        account.set_country(country_code)     # Sets the country value
        account.set_region(region_code)         # Sets the region value

        # Fetch PID, MiiName, and MiiData from PNID
        data = account.fetch_pid_from_pnid(pnid)
        if data is not None:
            account.set_principal_id(data['pid'])
            account.set_mii_name(data['mii_name'])
            account.set_mii_data(data['mii_data'])
            password_hash = account.calculate_password_hash(data['pid'], password)
            account.set_password_hash(password_hash)
            account.set_password_cache_enabled(True)
        else:
            msg = CTkMessagebox(title="Error", message="Failed to fetch a valid PID from the API.", option_1="Ok", sound=True, icon="warning", justify="right", corner_radius=10, button_width=5)
            return

        # Create mlc01 path
        base_dir = "mlc01/usr/save/system/act"
        start_id = 0x80000001

        while True:
            folder_name = f"{start_id:08x}"
            folder_path = os.path.join(base_dir, folder_name)
            account_file = os.path.join(folder_path, "account.dat")
            if not os.path.exists(account_file):
                break
            start_id += 1

        # Use the available PersistentId
        mlcpath = folder_path
        os.makedirs(mlcpath, exist_ok=True)

        # Set the new PersistentId on the account object
        account.m_persistent_id = start_id

        # Save account data to account.dat
        account.save_to_file(mlcpath + "/account.dat")
        msg = CTkMessagebox(title="Success", message="Account data saved to:\n" + mlcpath + "/account.dat\n\nMerge the mlc01 folder with your existing one.", option_1="Ok", sound=True, icon="check", justify="right", corner_radius=10, button_width=5)
    except ValueError as e:
        msg = CTkMessagebox(title="Error", message=str(e), option_1="Ok", sound=True, icon="warning", justify="right", corner_radius=10, button_width=5)
    except Exception as e:
        logging.error(f"Error in generate_account: {e}")
        msg = CTkMessagebox(title="Error", message="An unexpected error occurred.", option_1="Ok", sound=True, icon="warning", justify="right", corner_radius=10, button_width=5)


# icon filepath
script_dir = os.path.dirname(__file__)
icon_path = os.path.join(script_dir, 'pretendo.ico')

# Create the main application window
root = ctk.CTk()
root.iconbitmap(icon_path)
root.title("Pretendo Account Generator")
root.geometry("660x340")
root.resizable(False, False)

# Setting customtkinter Theme to dark and default color to blue
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create and place labels and entry widgets for the inputs
ctk.CTkLabel(root, text="PretendoNetworkID (PNID):").place(x=20, y=20)
pnid_entry = ctk.CTkEntry(root, width=200)
pnid_entry.place(x=200, y=20)

ctk.CTkLabel(root, text="Email Address:").place(x=20, y=60)
email_entry = ctk.CTkEntry(root, width=200)
email_entry.place(x=200, y=60)

ctk.CTkLabel(root, text="Password:").place(x=20, y=100)
password_entry = ctk.CTkEntry(root, show='*', width=200)
password_entry.place(x=200, y=100)

ctk.CTkLabel(root, text="Birth Year:").place(x=430, y=20)
birth_year_entry = ctk.CTkEntry(root)
birth_year_entry.place(x=508, y=20)
birth_year_entry.insert(0, '1998')

ctk.CTkLabel(root, text="Birth Month:").place(x=430, y=60)
birth_month_entry = ctk.CTkEntry(root)
birth_month_entry.place(x=508, y=60)
birth_month_entry.insert(0, '01')

ctk.CTkLabel(root, text="Birth Day:").place(x=430, y=100)
birth_day_entry = ctk.CTkEntry(root)
birth_day_entry.place(x=508, y=100)
birth_day_entry.insert(0, '01')

ctk.CTkLabel(root, text="Gender:").place(x=430, y=140)
gender_combobox = ctk.CTkComboBox(root, state='readonly')
gender_combobox.place(x=508, y=140)
CTkScrollableDropdown(gender_combobox, values=["None", "Male", "Female"], justify="left", button_color="transparent")
gender_combobox.set("None")

# Country Dropdown
ctk.CTkLabel(root, text="Country:").place(x=20, y=140)
country_combobox = ctk.CTkComboBox(root, state='readonly', width=200, values=list(countries.keys()))
country_combobox.place(x=200, y=140)
country_dropdown = CTkScrollableDropdown(country_combobox, values=list(countries.keys()), justify="left", button_color="transparent", command=update_country_selection)
country_combobox.set("None")  # Default value

# Region Dropdown
ctk.CTkLabel(root, text="Region:").place(x=20, y=180)
region_combobox = ctk.CTkComboBox(root, state='readonly', width=200, values=["None"])
region_combobox.place(x=200, y=180)
region_dropdown = CTkScrollableDropdown(region_combobox, values=["None"], justify="left", button_color="transparent")
region_combobox.set("None")

# version label
ctk.CTkLabel(root, text="v0.0.6").place(x=610, y=305)

# Messagebox for about page
def about_page():
    msg = CTkMessagebox(root, title="About", message="Pretendo Account Generator\nMade by TheCraZyDuDee", option_1="Issues", option_2="Close", sound=True, icon=None, justify="right", corner_radius=10, button_width=5)
    response = msg.get()

    if response=="Issues":
        webbrowser.open ('https://github.com/TheCraZyDuDee/Pretendo-Account-Generator/issues')

# Open About Page
about_button = ctk.CTkButton(root, text="About", command=about_page, width=10)
about_button.place(x=20, y=290)

# Open Mii Editor Website
miieditor_button = ctk.CTkButton(root, text="Mii Editor", command=lambda: webbrowser.open ('https://pretendo.network/account/login?redirect=/account/miieditor'), width=50)
miieditor_button.place(x=200, y=220)

# Generate Button
generate_button = ctk.CTkButton(root, text="Generate Account", command=generate_account)
generate_button.place(x=508, y=220)

root.mainloop()
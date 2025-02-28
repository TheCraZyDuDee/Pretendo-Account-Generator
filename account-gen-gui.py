import os
import webbrowser
import random
import binascii
from array import array
from struct import pack, unpack
import requests
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox
from CTkScrollableDropdown import *
from CTkMessagebox import *
import customtkinter as ctk
import base64
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
            url = f"https://pnidlt.gabis.online/api/v1/pnid/{pnid}"
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

# Country data
countries = {
    'None': {'id': '0', 'regions': {
    'None': "0000000"
}},
    'Japan': {'id': '1', 'regions': {
    "None": "1000000",
    "Tokyo": "1020000",
    "Hokkaido": "1030000",
    "Aomori": "1040000",
    "Iwate": "1050000",
    "Miyagi": "1060000",
    "Akita": "1070000",
    "Yamagata": "1080000",
    "Fukushima": "1090000",
    "Ibaraki": "10a0000",
    "Tochigi": "10b0000",
    "Gunma": "10c0000",
    "Saitama": "10d0000",
    "Chiba": "10e0000",
    "Kanagawa": "10f0000",
    "Toyama": "1100000",
    "Ishikawa": "1110000",
    "Fukui": "1120000",
    "Yamanashi": "1130000",
    "Nagano": "1140000",
    "Niigata": "1150000",
    "Gifu": "1160000",
    "Shizuoka": "1170000",
    "Aichi": "1180000",
    "Mie": "1190000",
    "Shiga": "11a0000",
    "Kyoto": "11b0000",
    "Osaka": "11c0000",
    "Hyogo": "11d0000",
    "Nara": "11e0000",
    "Wakayama": "11f0000",
    "Tottori": "1200000",
    "Shimane": "1210000",
    "Okayama": "1220000",
    "Hiroshima": "1230000",
    "Yamaguchi": "1240000",
    "Tokushima": "1250000",
    "Kagawa": "1260000",
    "Ehime": "1270000",
    "Kochi": "1280000",
    "Fukuoka": "1290000",
    "Saga": "12a0000",
    "Nagasaki": "12b0000",
    "Kumamoto": "12c0000",
    "Oita": "12d0000",
    "Miyazaki": "12e0000",
    "Kagoshima": "12f0000",
    "Okinawa": "1300000"
}},
    'Brazil': {'id': '10', 'regions': {
    "None": "10000000",
    "Distrito Federal": "10020000",
    "Acre": "10030000",
    "Alagoas": "10040000",
    "Amapá": "10050000",
    "Amazonas": "10060000",
    "Bahia": "10070000",
    "Ceará": "10080000",
    "Espírito Santo": "10090000",
    "Mato Grosso do Sul": "100a0000",
    "Maranhão": "100b0000",
    "Mato Grosso": "100c0000",
    "Minas Gerais": "100d0000",
    "Pará": "100e0000",
    "Paraíba": "100f0000",
    "Paraná": "10100000",
    "Piauí": "10110000",
    "Rio de Janeiro": "10120000",
    "Rio Grande do Norte": "10130000",
    "Rio Grande do Sul": "10140000",
    "Rondônia": "10150000",
    "Roraima": "10160000",
    "Santa Catarina": "10170000",
    "São Paulo": "10180000",
    "Sergipe": "10190000",
    "Goiás": "101a0000",
    "Pernambuco": "101b0000",
    "Tocantins": "101c0000"
}},
    'British Virgin Islands': {'id': '11', 'regions': {
    "None": "11000000",
    "British Virgin Islands": "11010000"
}},
    'Canada': {'id': '12', 'regions': {
    "None": "12000000",
    "Ontario": "12020000",
    "Alberta": "12030000",
    "British Columbia": "12040000",
    "Manitoba": "12050000",
    "New Brunswick": "12060000",
    "Newfoundland and Labrador": "12070000",
    "Nova Scotia": "12080000",
    "Prince Edward Island": "12090000",
    "Quebec": "120a0000",
    "Saskatchewan": "120b0000",
    "Yukon": "120c0000",
    "Northwest Territories": "120d0000",
    "Nunavut": "120e0000"
}},
    'Cayman Islands': {'id': '13', 'regions': {
    "None": "13000000",
    "Cayman Islands": "13010000"
}},
    'Chile': {'id': '14', 'regions': {
    "None": "14000000",
    "Región Metropolitana": "14020000",
    "Valparaíso": "14030000",
    "Aisén del General Carlos Ibáñez del Campo": "14040000",
    "Antofagasta": "14050000",
    "Araucanía": "14060000",
    "Atacama": "14070000",
    "Bío-Bío": "14080000",
    "Coquimbo": "14090000",
    "Libertador General Bernardo O'Higgins": "140a0000",
    "Los Lagos": "140b0000",
    "Magallanes y Antártica Chilena": "140c0000",
    "Maule": "140d0000",
    "Tarapacá": "140e0000"
}},
    'Colombia': {'id': '15', 'regions': {
    "None": "15000000",
    "Distrito Capital": "15020000",
    "Cundinamarca": "15030000",
    "Amazonas": "15040000",
    "Antioquia": "15050000",
    "Arauca": "15060000",
    "Atlántico": "15070000",
    "Bolívar": "15080000",
    "Boyacá": "15090000",
    "Caldas": "150a0000",
    "Caquetá": "150b0000",
    "Cauca": "150c0000",
    "Cesar": "150d0000",
    "Chocó": "150e0000",
    "Córdoba": "150f0000",
    "Guaviare": "15100000",
    "Guainía": "15110000",
    "Huila": "15120000",
    "La Guajira": "15130000",
    "Magdalena": "15140000",
    "Meta": "15150000",
    "Nariño": "15160000",
    "Norte de Santander": "15170000",
    "Putumayo": "15180000",
    "Quindío": "15190000",
    "Risaralda": "151a0000",
    "Archipiélago de San Andrés, Providencia y Santa Catalina": "151b0000",
    "Santander": "151c0000",
    "Sucre": "151d0000",
    "Tolima": "151e0000",
    "Valle del Cauca": "151f0000",
    "Vaupés": "15200000",
    "Vichada": "15210000",
    "Casanare": "15220000"
}},
    'Costa Rica': {'id': '16', 'regions': {
    "None": "16000000",
    "San José": "16020000",
    "Alajuela": "16030000",
    "Cartago": "16040000",
    "Guanacaste": "16050000",
    "Heredia": "16060000",
    "Limón": "16070000",
    "Puntarenas": "16080000"
}},
    'Dominica': {'id': '17', 'regions': {
    "None": "17000000",
    "Dominica": "17010000"
}},
    'Dominican Republic': {'id': '18', 'regions': {
    "None": "18000000",
    "Distrito Nacional": "18020000",
    "Azua": "18030000",
    "Baoruco": "18040000",
    "Barahona": "18050000",
    "Dajabón": "18060000",
    "Duarte": "18070000",
    "Espaillat": "18080000",
    "Independencia": "18090000",
    "La Altagracia": "180a0000",
    "Elías Piña": "180b0000",
    "La Romana": "180c0000",
    "María Trinidad Sánchez": "180d0000",
    "Monte Cristi": "180e0000",
    "Pedernales": "180f0000",
    "Peravia": "18100000",
    "Puerto Plata": "18110000",
    "Salcedo": "18120000",
    "Samaná": "18130000",
    "Sánchez Ramírez": "18140000",
    "San Juan": "18150000",
    "San Pedro de Macorís": "18160000",
    "Santiago": "18170000",
    "Santiago Rodríguez": "18180000",
    "Valverde": "18190000",
    "El Seíbo": "181a0000",
    "Hato Mayor": "181b0000",
    "La Vega": "181c0000",
    "Monseñor Nouel": "181d0000",
    "Monte Plata": "181e0000",
    "San Cristóbal": "181f0000"
}},
    'Ecuador': {'id': '19', 'regions': {
    "None": "19000000",
    "Pichincha": "19020000",
    "Galápagos": "19030000",
    "Azuay": "19040000",
    "Bolívar": "19050000",
    "Cañar": "19060000",
    "Carchi": "19070000",
    "Chimborazo": "19080000",
    "Cotopaxi": "19090000",
    "El Oro": "190a0000",
    "Esmeraldas": "190b0000",
    "Guayas": "190c0000",
    "Imbabura": "190d0000",
    "Loja": "190e0000",
    "Los Ríos": "190f0000",
    "Manabí": "19100000",
    "Morona-Santiago": "19110000",
    "Pastaza": "19120000",
    "Tungurahua": "19130000",
    "Zamora-Chinchipe": "19140000",
    "Sucumbios": "19150000",
    "Napo": "19160000",
    "Orellana": "19170000",
    "Santa Elena": "19180000",
    "Santo Domingo de los Tsáchilas": "19190000"
}},
    'El Salvador': {'id': '1a', 'regions': {
    "None": "1a000000",
    "San Salvador": "1a020000",
    "Ahuachapán": "1a030000",
    "Cabañas": "1a040000",
    "Chalatenango": "1a050000",
    "Cuscatlán": "1a060000",
    "La Libertad": "1a070000",
    "La Paz": "1a080000",
    "La Unión": "1a090000",
    "Morazán": "1a0a0000",
    "San Miguel": "1a0b0000",
    "Santa Ana": "1a0c0000",
    "San Vicente": "1a0d0000",
    "Sonsonate": "1a0e0000",
    "Usulután": "1a0f0000"
}},
    'French Guiana': {'id': '1b', 'regions': {
    "None": "1b000000",
    "French Guiana": "1b010000"
}},
    'Grenada': {'id': '1c', 'regions': {
    "None": "1c000000",
    "Grenada": "1c010000"
}},
    'Guadeloupe': {'id': '1d', 'regions': {
    "None": "1d000000",
    "Guadeloupe": "1d010000"
}},
    'Guatemala': {'id': '1e', 'regions': {
    "None": "1e000000",
    "Guatemala": "1e020000",
    "Alta Verapaz": "1e030000",
    "Baja Verapaz": "1e040000",
    "Chimaltenango": "1e050000",
    "Chiquimula": "1e060000",
    "El Progreso": "1e070000",
    "Escuintla": "1e080000",
    "Huehuetenango": "1e090000",
    "Izabal": "1e0a0000",
    "Jalapa": "1e0b0000",
    "Jutiapa": "1e0c0000",
    "Petén": "1e0d0000",
    "Quetzaltenango": "1e0e0000",
    "Quiché": "1e0f0000",
    "Retalhuleu": "1e100000",
    "Sacatepéquez": "1e110000",
    "San Marcos": "1e120000",
    "Santa Rosa": "1e130000",
    "Sololá": "1e140000",
    "Suchitepéquez": "1e150000",
    "Totonicapán": "1e160000",
    "Zacapa": "1e170000"
}},
    'Guyana': {'id': '1f', 'regions': {
    "None": "1f000000",
    "Demerara-Mahaica": "1f020000",
    "Barima-Waini": "1f030000",
    "Cuyuni-Mazaruni": "1f040000",
    "East Berbice-Corentyne": "1f050000",
    "Essequibo Islands-West Demerara": "1f060000",
    "Mahaica-Berbice": "1f070000",
    "Pomeroon-Supenaam": "1f080000",
    "Potaro-Siparuni": "1f090000",
    "Upper Demerara-Berbice": "1f0a0000",
    "Upper Takutu-Upper Essequibo": "1f0b0000"
}},
    'Haiti': {'id': '20', 'regions': {
    "None": "20000000",
    "Ouest": "20020000",
    "Nord-Ouest": "20030000",
    "Artibonite": "20040000",
    "Centre": "20050000",
    "Grand'Anse": "20060000",
    "Nord": "20070000",
    "Nord-Est": "20080000",
    "Sud": "20090000",
    "Sud-Est": "200a0000",
    "Nippes": "200b0000"
}},
    'Honduras': {'id': '21', 'regions': {
    "None": "21000000",
    "Fr얆徇᥄슃榩ﰕ䮍輝n": "21020000",
    "Atlántida": "21030000",
    "Choluteca": "21040000",
    "Colón": "21050000",
    "Comayagua": "21060000",
    "Copán": "21070000",
    "Cortés": "21080000",
    "El Paraíso": "21090000",
    "Gracias a Dios": "210a0000",
    "Intibucá": "210b0000",
    "Islas de la Bahía": "210c0000",
    "La Paz": "210d0000",
    "Lempira": "210e0000",
    "Ocotepeque": "210f0000",
    "Olancho": "21100000",
    "Santa Bárbara": "21110000",
    "Valle": "21120000",
    "Yoro": "21130000"
}},
    'Jamaica': {'id': '22', 'regions': {
    "None": "22000000",
    "Saint Thomas": "22020000",
    "Clarendon": "22030000",
    "Hanover": "22040000",
    "Manchester": "22050000",
    "Portland": "22060000",
    "Saint Andrew": "22070000",
    "Saint Ann": "22080000",
    "Saint Catherine": "22090000",
    "Saint Elizabeth": "220a0000",
    "Saint James": "220b0000",
    "Saint Mary": "220c0000",
    "Trelawny": "220d0000",
    "Westmoreland": "220e0000",
    "Kingston": "220f0000"
}},
    'Martinique': {'id': '23', 'regions': {
    "None": "23000000",
    "Martinique": "23010000"
}},
    'Mexico': {'id': '24', 'regions': {
    "None": "24000000",
    "Distrito Federal": "24020000",
    "Aguascalientes": "24030000",
    "Baja California": "24040000",
    "Baja California Sur": "24050000",
    "Campeche": "24060000",
    "Chiapas": "24070000",
    "Chihuahua": "24080000",
    "Coahuila de Zaragoza": "24090000",
    "Colima": "240a0000",
    "Durango": "240b0000",
    "Guanajuato": "240c0000",
    "Guerrero": "240d0000",
    "Hidalgo": "240e0000",
    "Jalisco": "240f0000",
    "México": "24100000",
    "Michoacán de Ocampo": "24110000",
    "Morelos": "24120000",
    "Nayarit": "24130000",
    "Nuevo León": "24140000",
    "Oaxaca": "24150000",
    "Puebla": "24160000",
    "Querétaro de Arteaga": "24170000",
    "Quintana Roo": "24180000",
    "San Luis Potosí": "24190000",
    "Sinaloa": "241a0000",
    "Sonora": "241b0000",
    "Tabasco": "241c0000",
    "Tamaulipas": "241d0000",
    "Tlaxcala": "241e0000",
    "Veracruz-Llave": "241f0000",
    "Yucatán": "24200000",
    "Zacatecas": "24210000"
}},
    'Montserrat': {'id': '25', 'regions': {
    "None": "25000000",
    "Montserrat": "25010000"
}},
    'Netherlands Antilles': {'id': '26', 'regions': {
    "None": "26000000",
    "Netherlands Antilles": "26010000"
}},
    'Nicaragua': {'id': '27', 'regions': {
    "None": "27000000",
    "Managua": "27020000",
    "Boaco": "27030000",
    "Carazo": "27040000",
    "Chinandega": "27050000",
    "Chontales": "27060000",
    "Estelí": "27070000",
    "Granada": "27080000",
    "Jinotega": "27090000",
    "León": "270a0000",
    "Madriz": "270b0000",
    "Masaya": "270c0000",
    "Matagalpa": "270d0000",
    "Nueva Segovia": "270e0000",
    "Río San Juan": "270f0000",
    "Rivas": "27100000",
    "Atlántico Norte": "27110000",
    "Atlántico Sur": "27120000"
}},
    'Panama': {'id': '28', 'regions': {
    "None": "28000000",
    "Panamá": "28020000",
    "Bocas del Toro": "28030000",
    "Chiriquí": "28040000",
    "Coclé": "28050000",
    "Colón": "28060000",
    "Darién": "28070000",
    "Herrera": "28080000",
    "Los Santos": "28090000",
    "Kuna Yala": "280a0000",
    "Veraguas": "280b0000"
}},
    'Paraguay': {'id': '29', 'regions': {
    "None": "29000000",
    "Central": "29020000",
    "Alto Paraná": "29030000",
    "Amambay": "29040000",
    "Caaguazú": "29050000",
    "Caazapá": "29060000",
    "Concepción": "29070000",
    "Cordillera": "29080000",
    "Guairá": "29090000",
    "Itapúa": "290a0000",
    "Misiones": "290b0000",
    "Ñeembucú": "290c0000",
    "Paraguarí": "290d0000",
    "Presidente Hayes": "290e0000",
    "San Pedro": "290f0000",
    "Canindeyú": "29100000",
    "Asunción": "29110000",
    "Alto Paraguay": "29120000",
    "Boquerón": "29130000"
}},
    'Peru': {'id': '2a', 'regions': {
    "None": "2a000000",
    "Lima": "2a020000",
    "Amazonas": "2a030000",
    "Ancash": "2a040000",
    "Apurímac": "2a050000",
    "Arequipa": "2a060000",
    "Ayacucho": "2a070000",
    "Cajamarca": "2a080000",
    "Callao": "2a090000",
    "Cuzco": "2a0a0000",
    "Huancavelica": "2a0b0000",
    "Huánuco": "2a0c0000",
    "Ica": "2a0d0000",
    "Junín": "2a0e0000",
    "La Libertad": "2a0f0000",
    "Lambayeque": "2a100000",
    "Loreto": "2a110000",
    "Madre de Dios": "2a120000",
    "Moquegua": "2a130000",
    "Pasco": "2a140000",
    "Piura": "2a150000",
    "Puno": "2a160000",
    "San Martín": "2a170000",
    "Tacna": "2a180000",
    "Tumbes": "2a190000",
    "Ucayali": "2a1a0000"
}},
    'St. Kitts and Nevis': {'id': '2b', 'regions': {
    "None": "2b000000",
    "Saint George Basseterre": "2b020000",
    "Christ Church Nichola Town": "2b030000",
    "Saint Anne Sandy Point": "2b040000",
    "Saint George Gingerland": "2b050000",
    "Saint James Windward": "2b060000",
    "Saint John Capesterre": "2b070000",
    "Saint John Figtree": "2b080000",
    "Saint Mary Cayon": "2b090000",
    "Saint Paul Capesterre": "2b0a0000",
    "Saint Paul Charlestown": "2b0b0000",
    "Saint Peter Basseterre": "2b0c0000",
    "Saint Thomas Lowland": "2b0d0000",
    "Saint Thomas Middle Island": "2b0e0000",
    "Trinity Palmetto Point": "2b0f0000"
}},
    'St. Lucia': {'id': '2c', 'regions': {
    "None": "2c000000",
    "St. Lucia": "2c010000"
}},
    'St. Vincent and the Grenadines': {'id': '2d', 'regions': {
    "None": "2d000000",
    "St. Vincent and the Grenadines": "2d010000"
}},
    'Suriname': {'id': '2e', 'regions': {
    "None": "2e000000",
    "Paramaribo": "2e020000",
    "Brokopondo": "2e030000",
    "Commewijne": "2e040000",
    "Coronie": "2e050000",
    "Marowijne": "2e060000",
    "Nickerie": "2e070000",
    "Para": "2e080000",
    "Saramacca": "2e090000",
    "Sipaliwini": "2e0a0000",
    "Wanica": "2e0b0000"
}},
    'Trinidad and Tobago': {'id': '2f', 'regions': {
    "None": "2f000000",
    "Port-of-Spain": "2f020000",
    "Arima": "2f030000",
    "Caroni": "2f040000",
    "Mayaro": "2f050000",
    "Nariva": "2f060000",
    "Saint Andrew": "2f070000",
    "Saint David": "2f080000",
    "Saint George": "2f090000",
    "Saint Patrick": "2f0a0000",
    "San Fernando": "2f0b0000",
    "Tobago": "2f0c0000",
    "Victoria": "2f0d0000",
    "Point Fortin": "2f0e0000"
}},
    'Turks and Caicos Islands': {'id': '30', 'regions': {
    "None": "30000000",
    "Turks and Caicos Islands": "30010000"
}},
    'United States': {'id': '31', 'regions': {
    "None": "31000000",
    "District of Columbia": "31020000",
    "Alaska": "31030000",
    "Alabama": "31040000",
    "Arkansas": "31050000",
    "Arizona": "31060000",
    "California": "31070000",
    "Colorado": "31080000",
    "Connecticut": "31090000",
    "Delaware": "310a0000",
    "Florida": "310b0000",
    "Georgia": "310c0000",
    "Hawaii": "310d0000",
    "Iowa": "310e0000",
    "Idaho": "310f0000",
    "Illinois": "31100000",
    "Indiana": "31110000",
    "Kansas": "31120000",
    "Kentucky": "31130000",
    "Louisiana": "31140000",
    "Massachusetts": "31150000",
    "Maryland": "31160000",
    "Maine": "31170000",
    "Michigan": "31180000",
    "Minnesota": "31190000",
    "Missouri": "311a0000",
    "Mississippi": "311b0000",
    "Montana": "311c0000",
    "North Carolina": "311d0000",
    "North Dakota": "311e0000",
    "Nebraska": "311f0000",
    "New Hampshire": "31200000",
    "New Jersey": "31210000",
    "New Mexico": "31220000",
    "Nevada": "31230000",
    "New York": "31240000",
    "Ohio": "31250000",
    "Oklahoma": "31260000",
    "Oregon": "31270000",
    "Pennsylvania": "31280000",
    "Rhode Island": "31290000",
    "South Carolina": "312a0000",
    "South Dakota": "312b0000",
    "Tennessee": "312c0000",
    "Texas": "312d0000",
    "Utah": "312e0000",
    "Virginia": "312f0000",
    "Vermont": "31300000",
    "Washington": "31310000",
    "Wisconsin": "31320000",
    "West Virginia": "31330000",
    "Wyoming": "31340000",
    "Puerto Rico": "31350000"
}},
    'Uruguay': {'id': '32', 'regions': {
    "None": "32000000",
    "Montevideo": "32020000",
    "Artigas": "32030000",
    "Canelones": "32040000",
    "Cerro Largo": "32050000",
    "Colonia": "32060000",
    "Durazno": "32070000",
    "Flores": "32080000",
    "Florida": "32090000",
    "Lavalleja": "320a0000",
    "Maldonado": "320b0000",
    "Paysandú": "320c0000",
    "Río Negro": "320d0000",
    "Rivera": "320e0000",
    "Rocha": "320f0000",
    "Salto": "32100000",
    "San José": "32110000",
    "Soriano": "32120000",
    "Tacuarembó": "32130000",
    "Treinta y Tres": "32140000"
}},
    'US Virgin Islands': {'id': '33', 'regions': {
    "None": "33000000",
    "US Virgin Islands": "33010000"
}},
    'Venezuela': {'id': '34', 'regions': {
    "None": "34000000",
    "Distrito Federal": "34020000",
    "Amazonas": "34030000",
    "Anzoátegui": "34040000",
    "Apure": "34050000",
    "Aragua": "34060000",
    "Barinas": "34070000",
    "Bolívar": "34080000",
    "Carabobo": "34090000",
    "Cojedes": "340a0000",
    "Delta Amacuro": "340b0000",
    "Falcón": "340c0000",
    "Guárico": "340d0000",
    "Lara": "340e0000",
    "Mérida": "340f0000",
    "Miranda": "34100000",
    "Monagas": "34110000",
    "Nueva Esparta": "34120000",
    "Portuguesa": "34130000",
    "Sucre": "34140000",
    "Táchira": "34150000",
    "Trujillo": "34160000",
    "Yaracuy": "34170000",
    "Zulia": "34180000",
    "Dependencias Federales": "34190000",
    "Vargas": "341a0000"
}},
    'Albania': {'id': '40', 'regions': {
    "None": "40000000",
    "Tirana": "40020000",
    "Berat": "40030000",
    "Dibër": "40040000",
    "Durrës": "40050000",
    "Elbasan": "40060000",
    "Fier": "40070000",
    "Gjirokastër": "40080000",
    "Korçë": "40090000",
    "Kukës": "400a0000",
    "Lezhë": "400b0000",
    "Shkodër": "400c0000",
    "Vlorë": "400d0000"
}},
    'Australia': {'id': '41', 'regions': {
    "None": "41000000",
    "Australian Capital Territory": "41020000",
    "New South Wales": "41030000",
    "Northern Territory": "41040000",
    "Queensland": "41050000",
    "South Australia": "41060000",
    "Tasmania": "41070000",
    "Victoria": "41080000",
    "Western Australia": "41090000"
}},
    'Austria': {'id': '42', 'regions': {
    "None": "42000000",
    "Vienna": "42020000",
    "Burgenland": "42030000",
    "Carinthia": "42040000",
    "Lower Austria": "42050000",
    "Upper Austria": "42060000",
    "Salzburg": "42070000",
    "Styria": "42080000",
    "Tyrol": "42090000",
    "Vorarlberg": "420a0000"
}},
    'Belgium': {'id': '43', 'regions': {
    "None": "43000000",
    "Brussels Region": "43020000",
    "Flanders": "43030000",
    "Wallonia": "43040000"
}},
    'Bosnia and Herzegovina': {'id': '44', 'regions': {
    "None": "44000000",
    "Federation of Bosnia and Herzegovina": "44020000",
    "Republika Srpska": "44030000",
    "Brčko District": "44040000"
}},
    'Botswana': {'id': '45', 'regions': {
    "None": "45000000",
    "Botswana": "45010000"
}},
    'Bulgaria': {'id': '46', 'regions': {
    "None": "46000000",
    "Sofia City": "46020000",
    "Sofia Province": "46030000",
    "Blagoevgrad": "46040000",
    "Pleven": "46050000",
    "Vidin": "46060000",
    "Varna": "46070000",
    "Burgas": "46080000",
    "Dobrich": "46090000",
    "Gabrovo": "460a0000",
    "Haskovo": "460b0000",
    "Yambol": "460c0000",
    "Kardzhali": "460d0000",
    "Kyustendil": "460e0000",
    "Lovech": "460f0000",
    "Montana": "46100000",
    "Pazardzhik": "46110000",
    "Pernik": "46120000",
    "Plovdiv": "46130000",
    "Razgrad": "46140000",
    "Ruse": "46150000",
    "Silistra": "46160000",
    "Sliven": "46170000",
    "Smolyan": "46180000",
    "Stara Zagora": "46190000",
    "Shumen": "461a0000",
    "Targovishte": "461b0000",
    "Veliko Tarnovo": "461c0000",
    "Vratsa": "461d0000"
}},
    'Croatia': {'id': '47', 'regions': {
    "None": "47000000",
    "Zagreb": "47060000",
    "Bjelovar-Bilogora County": "47070000",
    "Brod-Posavina County": "47080000",
    "Dubrovnik-Neretva County": "47090000",
    "Istria County": "470a0000",
    "Karlovac County": "470b0000",
    "Koprivnica-Križevci County": "470c0000",
    "Krapina-Zagorje County": "470d0000",
    "Lika-Senj County": "470e0000",
    "Međimurje County": "470f0000",
    "Osijek-Baranja County": "47100000",
    "Požega-Slavonia County": "47110000",
    "Primorje-Gorski Kotar County": "47120000",
    "Sisak-Moslavina County": "47130000",
    "Split-Dalmatia County": "47140000",
    "Šibenik-Knin County": "47150000",
    "Varaždin County": "47160000",
    "Virovitica-Podravina County": "47170000",
    "Vukovar-Syrmia County": "47180000",
    "Zadar County": "47190000",
    "Zagreb County": "471a0000"
}},
    'Cyprus': {'id': '48', 'regions': {
    "None": "48000000",
    "Cyprus": "48010000"
}},
    'Czech Republic': {'id': '49', 'regions': {
    "None": "49000000",
    "Prague": "49020000",
    "Central Bohemian Region": "49030000",
    "South Bohemian Region": "49040000",
    "Plzeň Region": "49050000",
    "Karlovy Vary Region": "49060000",
    "Ústí nad Labem Region": "49070000",
    "Liberec Region": "49080000",
    "Hradec Králové Region": "49090000",
    "Pardubice Region": "490a0000",
    "Olomouc Region": "490b0000",
    "Moravian-Silesian Region": "490c0000",
    "South Moravian Region": "490d0000",
    "Zlín Region": "490e0000",
    "Vysočina Region": "490f0000"
}},
    'Denmark (Kingdom of)': {'id': '4a', 'regions': {
    "None": "4a000000",
    "Greenland": "4a120000",
    "Capital Region of Denmark": "4a130000",
    "Central Denmark Region": "4a140000",
    "North Denmark Region": "4a150000",
    "Region Zealand": "4a160000",
    "Region of Southern Denmark": "4a170000",
    "Faroe Islands": "4a180000"
}},
    'Estonia': {'id': '4b', 'regions': {
    "None": "4b000000",
    "Estonia": "4b010000"
}},
    'Finland': {'id': '4c', 'regions': {
    "None": "4c000000",
    "Uusimaa / Nyland": "4c080000",
    "Lappi / Lapland": "4c090000",
    "Pohjois-Pohjanmaa / Norra Österbotten": "4c0a0000",
    "Kainuu / Kajanaland": "4c0b0000",
    "Pohjois-Karjala / Norra Karelen": "4c0c0000",
    "Pohjois-Savo / Norra Savolax": "4c0d0000",
    "Etelä-Savo / Södra Savolax": "4c0e0000",
    "Etelä-Pohjanmaa / Södra Österbotten": "4c0f0000",
    "Pohjanmaa / Österbotten": "4c100000",
    "Pirkanmaa / Birkaland": "4c110000",
    "Satakunta / Satakunda": "4c120000",
    "Keski-Pohjanmaa / Mellersta Österbotten": "4c130000",
    "Keski-Suomi / Mellersta Finland": "4c140000",
    "Varsinais-Suomi / Egentliga Finland": "4c150000",
    "Etelä-Karjala / Södra Karelen": "4c160000",
    "Päijät-Häme / Päijänne Tavastland": "4c170000",
    "Kanta-Häme / Egentliga Tavastland": "4c180000",
    "Kymenlaakso / Kymmenedalen": "4c1a0000",
    "Ahvenanmaa / Åland": "4c1b0000"
}},
    'France': {'id': '4d', 'regions': {
    "None": "4d000000",
    "Île-de-France": "4d020000",
    "Alsace": "4d030000",
    "Aquitaine": "4d040000",
    "Auvergne": "4d050000",
    "Lower Normandy": "4d060000",
    "Burgundy": "4d070000",
    "Brittany": "4d080000",
    "Centre": "4d090000",
    "Champagne-Ardenne": "4d0a0000",
    "Corsica": "4d0b0000",
    "Franche-Comté": "4d0c0000",
    "Upper Normandy": "4d0d0000",
    "Languedoc-Roussillon": "4d0e0000",
    "Limousin": "4d0f0000",
    "Lorraine": "4d100000",
    "Midi-Pyrénées": "4d110000",
    "Nord-Pas-de-Calais": "4d120000",
    "Pays de la Loire": "4d130000",
    "Picardy": "4d140000",
    "Poitou-Charentes": "4d150000",
    "Provence-Alpes-Côte d'Azur": "4d160000",
    "Rhône-Alpes": "4d170000",
    "Guadeloupe": "4d180000",
    "Martinique": "4d190000",
    "French Guiana": "4d1a0000",
    "Réunion": "4d1b0000",
    "Mayotte": "4d1c0000"
}},
    'Germany': {'id': '4e', 'regions': {
    "None": "4e000000",
    "Berlin": "4e020000",
    "Hesse": "4e030000",
    "Baden-Württemberg": "4e040000",
    "Bavaria": "4e050000",
    "Brandenburg": "4e060000",
    "Bremen": "4e070000",
    "Hamburg": "4e080000",
    "Mecklenburg-Vorpommern": "4e090000",
    "Lower Saxony": "4e0a0000",
    "North Rhine-Westphalia": "4e0b0000",
    "Rhineland-Palatinate": "4e0c0000",
    "Saarland": "4e0d0000",
    "Saxony": "4e0e0000",
    "Saxony-Anhalt": "4e0f0000",
    "Schleswig-Holstein": "4e100000",
    "Thuringia": "4e110000"
}},
    'Greece': {'id': '4f', 'regions': {
    "None": "4f000000",
    "Attica": "4f020000",
    "Central Greece": "4f030000",
    "Central Macedonia": "4f040000",
    "Crete": "4f050000",
    "East Macedonia and Thrace": "4f060000",
    "Epirus": "4f070000",
    "Ionian Islands": "4f080000",
    "North Aegean": "4f090000",
    "Peloponnese": "4f0a0000",
    "South Aegean": "4f0b0000",
    "Thessaly": "4f0c0000",
    "West Greece": "4f0d0000",
    "West Macedonia": "4f0e0000"
}},
    'Hungary': {'id': '50', 'regions': {
    "None": "50000000",
    "Budapest": "50020000",
    "Bács-Kiskun County": "50030000",
    "Baranya County": "50040000",
    "Békés County": "50050000",
    "Borsod-Abaúj-Zemplén County": "50060000",
    "Csongrád County": "50070000",
    "Fejér County": "50080000",
    "Győr-Moson-Sopron County": "50090000",
    "Hajdú-Bihar County": "500a0000",
    "Heves County": "500b0000",
    "Jász-Nagykun-Szolnok County": "500c0000",
    "Komárom-Esztergom County": "500d0000",
    "Nógrád County": "500e0000",
    "Pest County": "500f0000",
    "Somogy County": "50100000",
    "Szabolcs-Szatmár-Bereg County": "50110000",
    "Tolna County": "50120000",
    "Vas County": "50130000",
    "Veszprém County": "50140000",
    "Zala County": "50150000"
}},
    'Iceland': {'id': '51', 'regions': {
    "None": "51000000",
    "Iceland": "51010000"
}},
    'Ireland': {'id': '52', 'regions': {
    "None": "52000000",
    "Dublin": "52020000",
    "County Carlow": "520a0000",
    "County Cavan": "520b0000",
    "County Clare": "520c0000",
    "County Cork": "520d0000",
    "County Donegal": "520e0000",
    "County Galway": "520f0000",
    "County Kerry": "52100000",
    "County Kildare": "52110000",
    "County Kilkenny": "52120000",
    "County Laois": "52130000",
    "County Leitrim": "52140000",
    "County Limerick": "52150000",
    "County Longford": "52160000",
    "County Louth": "52170000",
    "County Mayo": "52180000",
    "County Meath": "52190000",
    "County Monaghan": "521a0000",
    "County Offaly": "521b0000",
    "County Roscommon": "521c0000",
    "County Sligo": "521d0000",
    "County Tipperary": "521e0000",
    "County Waterford": "521f0000",
    "County Westmeath": "52200000",
    "County Wexford": "52210000",
    "County Wicklow": "52220000"
}},
    'Italy': {'id': '53', 'regions': {
    "None": "53000000",
    "Lazio": "53020000",
    "Aosta Valley": "53030000",
    "Piedmont": "53040000",
    "Liguria": "53050000",
    "Lombardy": "53060000",
    "Trentino-Alto Adige": "53070000",
    "Veneto": "53080000",
    "Friuli Venezia Giulia": "53090000",
    "Emilia-Romagna": "530a0000",
    "Tuscany": "530b0000",
    "Umbria": "530c0000",
    "Marche": "530d0000",
    "Abruzzo": "530e0000",
    "Molise": "530f0000",
    "Campania": "53100000",
    "Apulia": "53110000",
    "Basilicata": "53120000",
    "Calabria": "53130000",
    "Sicily": "53140000",
    "Sardinia": "53150000"
}},
    'Latvia': {'id': '54', 'regions': {
    "None": "54000000",
    "Latvia": "54010000"
}},
    'Lesotho': {'id': '55', 'regions': {
    "None": "55000000",
    "Maseru": "55020000",
    "Berea": "55030000",
    "Butha-Buthe": "55040000",
    "Leribe": "55050000",
    "Mafeteng": "55060000",
    "Mohale's Hoek": "55070000",
    "Mokhotlong": "55080000",
    "Qacha's Nek": "55090000",
    "Quthing": "550a0000",
    "Thaba-Tseka": "550b0000"
}},
    'Liechtenstein': {'id': '56', 'regions': {
    "None": "56000000",
    "Liechtenstein": "56010000"
}},
    'Lithuania': {'id': '57', 'regions': {
    "None": "57000000",
    "Vilnius": "57020000",
    "Alytus": "57030000",
    "Kaunas": "57040000",
    "Klaipėda": "57050000",
    "Marijampolė": "57060000",
    "Panevėžys": "57070000",
    "Šiauliai": "57080000",
    "Taurage": "57090000",
    "Telšiai": "570a0000",
    "Utena": "570b0000"
}},
    'Luxembourg': {'id': '58', 'regions': {
    "None": "58000000",
    "Luxembourg": "58010000"
}},
    'Macedonia (Republic of)': {'id': '59', 'regions': {
    "None": "59000000",
    "Macedonia (Republic of)": "59010000"
}},
    'Malta': {'id': '5a', 'regions': {
    "None": "5a000000",
    "Malta": "5a010000"
}},
    'Montenegro': {'id': '5b', 'regions': {
    "None": "5b000000",
    "Montenegro": "5b010000"
}},
    'Mozambique': {'id': '5c', 'regions': {
    "None": "5c000000",
    "Mozambique": "5c010000"
}},
    'Namibia': {'id': '5d', 'regions': {
    "None": "5d000000",
    "Namibia": "5d010000"
}},
    'Netherlands': {'id': '5e', 'regions': {
    "None": "5e000000",
    "North Holland": "5e020000",
    "Drenthe": "5e030000",
    "Flevoland": "5e040000",
    "Friesland": "5e050000",
    "Gelderland": "5e060000",
    "Groningen": "5e070000",
    "Limburg": "5e080000",
    "North Brabant": "5e090000",
    "Overijssel": "5e0a0000",
    "South Holland": "5e0b0000",
    "Utrecht": "5e0c0000",
    "Zeeland": "5e0d0000"
}},
    'New Zealand': {'id': '5f', 'regions': {
    "None": "5f000000",
    "Wellington": "5f020000",
    "Auckland": "5f030000",
    "Bay of Plenty": "5f040000",
    "Canterbury": "5f050000",
    "Otago": "5f060000",
    "Hawke's Bay": "5f070000",
    "Manawatu-Wanganui": "5f080000",
    "Nelson": "5f090000",
    "Northland": "5f0a0000",
    "Southland": "5f0c0000",
    "Taranaki": "5f0d0000",
    "Waikato": "5f0e0000",
    "Gisborne": "5f0f0000",
    "West Coast": "5f100000",
    "Marlborough": "5f110000",
    "Tasman": "5f120000"
}},
    'Norway': {'id': '60', 'regions': {
    "None": "60000000",
    "Oslo": "60070000",
    "Akershus": "60080000",
    "Aust-Agder": "60090000",
    "Buskerud": "600a0000",
    "Finnmark": "600b0000",
    "Hedmark": "600c0000",
    "Hordaland": "600d0000",
    "Møre og Romsdal": "600e0000",
    "Nordland": "600f0000",
    "Nord-Trøndelag": "60100000",
    "Oppland": "60110000",
    "Rogaland": "60120000",
    "Sogn og Fjordane": "60130000",
    "Sør-Trøndelag": "60140000",
    "Telemark": "60150000",
    "Troms": "60160000",
    "Vest-Agder": "60170000",
    "Vestfold": "60180000",
    "Østfold": "60190000",
    "Svalbard": "601a0000"
}},
    'Poland': {'id': '61', 'regions': {
    "None": "61000000",
    "Masovia": "61020000",
    "Lower Silesia": "61030000",
    "Kuyavian-Pomeranian Voivodeship": "61040000",
    "Lodz": "61050000",
    "Lublin": "61060000",
    "Lubusz": "61070000",
    "Lesser Poland": "61080000",
    "Opole": "61090000",
    "Subcarpathia": "610a0000",
    "Podlachia": "610b0000",
    "Pomerania": "610c0000",
    "Silesia": "610d0000",
    "Świętokrzyskie": "610e0000",
    "Warmian-Masurian Voivodeship": "610f0000",
    "Greater Poland": "61100000",
    "Western Pomerania": "61110000"
}},
    'Portugal': {'id': '62', 'regions': {
    "None": "62000000",
    "Lisbon": "62020000",
    "Madeira": "62070000",
    "Azores": "62080000",
    "Aveiro": "62090000",
    "Beja": "620a0000",
    "Braga": "620b0000",
    "Bragança": "620c0000",
    "Castelo Branco": "620d0000",
    "Coimbra": "620e0000",
    "Évora": "620f0000",
    "Faro": "62100000",
    "Guarda": "62110000",
    "Leiria": "62120000",
    "Portalegre": "62130000",
    "Porto": "62140000",
    "Santarém": "62150000",
    "Setúbal": "62160000",
    "Viana do Castelo": "62170000",
    "Vila Real": "62180000",
    "Viseu": "62190000"
}},
    'Romania': {'id': '63', 'regions': {
    "None": "63000000",
    "Bucharest": "63020000",
    "Alba": "63030000",
    "Arad": "63040000",
    "Arges": "63050000",
    "Bacau": "63060000",
    "Bihor": "63070000",
    "Bistrita-Nasaud": "63080000",
    "Botosani": "63090000",
    "Braila": "630a0000",
    "Brasov": "630b0000",
    "Buzau": "630c0000",
    "Calarasi": "630d0000",
    "Caras-Severin": "630e0000",
    "Cluj": "630f0000",
    "Constanta": "63100000",
    "Covasna": "63110000",
    "Dâmbovita": "63120000",
    "Dolj": "63130000",
    "Galati": "63140000",
    "Giurgiu": "63150000",
    "Gorj": "63160000",
    "Harghita": "63170000",
    "Hunedoara": "63180000",
    "Ialomita": "63190000",
    "Iasi": "631a0000",
    "Ilfov": "631b0000",
    "Maramures": "631c0000",
    "Mehedinti": "631d0000",
    "Mures": "631e0000",
    "Neamt": "631f0000",
    "Olt": "63200000",
    "Prahova": "63210000",
    "Salaj": "63220000",
    "Satu Mare": "63230000",
    "Sibiu": "63240000",
    "Suceava": "63250000",
    "Teleorman": "63260000",
    "Timis": "63270000",
    "Tulcea": "63280000",
    "Vâlcea": "63290000",
    "Vaslui": "632a0000",
    "Vrancea": "632b0000"
}},
    'Russia': {'id': '64', 'regions': {
    "None": "64000000",
    "Moscow City": "64090000",
    "Adygey": "640a0000",
    "Gorno-Altay": "640b0000",
    "Altay": "640c0000",
    "Amur": "640d0000",
    "Arkhangel'sk": "640e0000",
    "Astrakhan'": "640f0000",
    "Bashkortostan": "64100000",
    "Belgorod": "64110000",
    "Bryansk": "64120000",
    "Buryat": "64130000",
    "Chechnya": "64140000",
    "Chelyabinsk": "64150000",
    "Chukot": "64160000",
    "Chuvash": "64170000",
    "Dagestan": "64180000",
    "Ingushetia": "64190000",
    "Irkutsk": "641a0000",
    "Ivanovo": "641b0000",
    "Kabardin-Balkar": "641c0000",
    "Kaliningrad": "641d0000",
    "Kalmyk": "641e0000",
    "Kaluga": "641f0000",
    "Kamchatka": "64200000",
    "Karachay-Cherkess": "64210000",
    "Karelia": "64220000",
    "Kemerovo": "64230000",
    "Khabarovsk": "64240000",
    "Khakassia": "64250000",
    "Khanty-Mansiy": "64260000",
    "Kirov": "64270000",
    "Komi": "64280000",
    "Kostroma": "64290000",
    "Krasnodar": "642a0000",
    "Krasnoyarsk": "642b0000",
    "Kurgan": "642c0000",
    "Kursk": "642d0000",
    "Leningrad": "642e0000",
    "Lipetsk": "642f0000",
    "Magadan": "64300000",
    "Mariy-El": "64310000",
    "Mordovia": "64320000",
    "Moscow": "64330000",
    "Murmansk": "64340000",
    "Nenets": "64350000",
    "Nizhegorod": "64360000",
    "Novgorod": "64370000",
    "Novosibirsk": "64380000",
    "Omsk": "64390000",
    "Orenburg": "643a0000",
    "Orel": "643b0000",
    "Penza": "643c0000",
    "Perm'": "643d0000",
    "Primor'ye": "643e0000",
    "Pskov": "643f0000",
    "Rostov": "64400000",
    "Ryazan'": "64410000",
    "Sakha": "64420000",
    "Sakhalin": "64430000",
    "Samara": "64440000",
    "St. Petersburg": "64450000",
    "Saratov": "64460000",
    "North Ossetia": "64470000",
    "Smolensk": "64480000",
    "Stavropol'": "64490000",
    "Sverdlovsk": "644a0000",
    "Tambov": "644b0000",
    "Tatarstan": "644c0000",
    "Tomsk": "644d0000",
    "Tula": "644e0000",
    "Tver'": "644f0000",
    "Tyumen'": "64500000",
    "Tuva": "64510000",
    "Udmurt": "64520000",
    "Ul'yanovsk": "64530000",
    "Vladimir": "64540000",
    "Volgograd": "64550000",
    "Vologda": "64560000",
    "Voronezh": "64570000",
    "Yamal-Nenets": "64580000",
    "Yaroslavl'": "64590000",
    "Yevrey": "645a0000",
    "Zabaykal'ye": "645b0000"
}},
    'Serbia and Kosovo': {'id': '65', 'regions': {
    "None": "65000000",
    "Serbia and Kosovo": "65010000"
}},
    'Slovakia': {'id': '66', 'regions': {
    "None": "66000000",
    "Bratislava": "66020000",
    "Banská Bystrica": "66030000",
    "Košice": "66040000",
    "Nitra": "66050000",
    "Prešov": "66060000",
    "Trencín": "66070000",
    "Trnava": "66080000",
    "Žilina": "66090000"
}},
    'Slovenia': {'id': '67', 'regions': {
    "None": "67000000",
    "Slovenia": "67010000"
}},
    'South Africa': {'id': '68', 'regions': {
    "None": "68000000",
    "Gauteng": "68020000",
    "Western Cape": "68030000",
    "Northern Cape": "68040000",
    "Eastern Cape": "68050000",
    "KwaZulu-Natal": "68060000",
    "Free State": "68070000",
    "North West": "68080000",
    "Mpumalanga": "68090000",
    "Limpopo": "680a0000"
}},
    'Spain': {'id': '69', 'regions': {
    "None": "69000000",
    "Madrid": "69020000",
    "Andalusia": "69030000",
    "Aragon": "69040000",
    "Principality of Asturias": "69050000",
    "Balearic Islands": "69060000",
    "Canary Islands": "69070000",
    "Cantabria": "69080000",
    "Castile-La Mancha": "69090000",
    "Castilla y León": "690a0000",
    "Catalonia": "690b0000",
    "Valencia": "690c0000",
    "Extremadura": "690d0000",
    "Galicia": "690e0000",
    "Murcia": "690f0000",
    "Navarre": "69100000",
    "Basque Country": "69110000",
    "La Rioja": "69120000",
    "Ceuta": "69130000",
    "Melilla": "69140000"
}},
    'Swaziland': {'id': '6a', 'regions': {
    "None": "6a000000",
    "Hhohho": "6a020000",
    "Lubombo": "6a030000",
    "Manzini": "6a040000",
    "Shiselweni": "6a050000"
}},
    'Sweden': {'id': '6b', 'regions': {
    "None": "6b000000",
    "Stockholm County": "6b020000",
    "Skåne County": "6b030000",
    "Västra Götaland County": "6b040000",
    "Östergötland County": "6b050000",
    "Södermanland County": "6b060000",
    "Värmland County": "6b070000",
    "Uppsala County": "6b080000",
    "Gävleborg County": "6b090000",
    "Västerbotten County": "6b0a0000",
    "Norrbotten County": "6b0b0000",
    "Gotland Island": "6b0c0000",
    "Jämtland County": "6b0d0000",
    "Dalarna County": "6b0e0000",
    "Blekinge County": "6b0f0000",
    "Örebro County": "6b100000",
    "Västernorrland County": "6b110000",
    "Jönköping County": "6b120000",
    "Kronoberg County": "6b130000",
    "Kalmar County": "6b140000",
    "Västmanland County": "6b150000",
    "Halland County": "6b160000"
}},
    'Switzerland': {'id': '6c', 'regions': {
    "None": "6c000000",
    "Bern": "6c020000",
    "Aargau": "6c040000",
    "Basel-City": "6c050000",
    "Fribourg": "6c060000",
    "Geneva": "6c070000",
    "Glarus": "6c080000",
    "Graubünden": "6c090000",
    "Jura": "6c0a0000",
    "Luzern": "6c0b0000",
    "Neuchâtel": "6c0c0000",
    "Obwalden": "6c0d0000",
    "St. Gallen": "6c0e0000",
    "Schaffhausen": "6c0f0000",
    "Schwyz": "6c100000",
    "Solothurn": "6c110000",
    "Thurgau": "6c120000",
    "Ticino": "6c130000",
    "Uri": "6c140000",
    "Valais": "6c150000",
    "Vaud": "6c160000",
    "Zug": "6c170000",
    "Zurich": "6c180000",
    "Appenzell Outer Rhodes": "6c190000",
    "Appenzell Inner Rhodes": "6c1a0000",
    "Basel-Landschaft": "6c1b0000",
    "Nidwalden": "6c1c0000"
}},
    'Turkey': {'id': '6d', 'regions': {
    "None": "6d000000",
    "Ankara": "6d020000",
    "İstanbul": "6d030000",
    "İzmir": "6d040000",
    "Bursa": "6d050000",
    "Adana": "6d060000",
    "Gaziantep": "6d070000",
    "Konya": "6d080000",
    "Antalya": "6d090000",
    "Diyarbakır": "6d0a0000",
    "Mersin": "6d0b0000",
    "Kayseri": "6d0c0000",
    "Şanlıurfa": "6d0e0000",
    "Malatya": "6d0f0000",
    "Erzurum": "6d100000",
    "Samsun": "6d110000",
    "Van": "6d120000",
    "Kahramanmaraş": "6d130000",
    "Denizli": "6d140000",
    "Batman": "6d150000",
    "Elazığ": "6d160000",
    "Sakarya": "6d170000",
    "Kocaeli": "6d180000",
    "Sivas": "6d190000",
    "Manisa": "6d1a0000",
    "Trabzon": "6d1b0000",
    "Balıkesir": "6d1c0000",
    "Adıyaman": "6d1d0000",
    "Tekirdağ": "6d1e0000",
    "Kırıkkale": "6d1f0000",
    "Osmaniye": "6d200000",
    "Kütahya": "6d210000",
    "Çorum": "6d220000",
    "Isparta": "6d230000",
    "Aydın": "6d240000",
    "Hatay": "6d250000",
    "Mardin": "6d260000",
    "Aksaray": "6d270000",
    "Afyonkarahisar": "6d280000",
    "Tokat": "6d290000",
    "Edirne": "6d2a0000",
    "Karaman": "6d2b0000",
    "Ordu": "6d2c0000",
    "Siirt": "6d2d0000",
    "Erzincan": "6d2e0000",
    "Çankırı": "6d2f0000",
    "Zonguldak": "6d300000",
    "Yozgat": "6d310000",
    "Uşak": "6d320000",
    "Ağrı": "6d330000",
    "Amasya": "6d340000",
    "Ardahan": "6d350000",
    "Artvin": "6d360000",
    "Bartın": "6d370000",
    "Bayburt": "6d380000",
    "Bilecik": "6d390000",
    "Bingöl": "6d3a0000",
    "Bitlis": "6d3b0000",
    "Bolu": "6d3c0000",
    "Burdur": "6d3d0000",
    "Çanakkale": "6d3e0000",
    "Düzce": "6d3f0000",
    "Eskişehir": "6d400000",
    "Giresun": "6d410000",
    "Gümüşhane": "6d420000",
    "Hakkari": "6d430000",
    "Iğdır": "6d440000",
    "Karabük": "6d450000",
    "Kars": "6d460000",
    "Kastamonu": "6d470000",
    "Kilis": "6d480000",
    "Kırklareli": "6d490000",
    "Kırşehir": "6d4a0000",
    "Muğla": "6d4b0000",
    "Muş": "6d4c0000",
    "Nevşehir": "6d4d0000",
    "Niğde": "6d4e0000",
    "Rize": "6d4f0000",
    "Sinop": "6d500000",
    "Şırnak": "6d510000",
    "Tunceli": "6d520000",
    "Yalova": "6d530000"
}},
    'United Kingdom': {'id': '6e', 'regions': {
    "None": "6e000000",
    "London": "6e030000",
    "Scotland": "6e050000",
    "Wales": "6e060000",
    "Northern Ireland": "6e070000",
    "South West": "6e080000",
    "West Midlands": "6e090000",
    "North West": "6e0a0000",
    "North East": "6e0b0000",
    "Yorkshire and the Humber": "6e0c0000",
    "East Midlands": "6e0d0000",
    "East of England": "6e0e0000",
    "South East": "6e0f0000"
}},
    'Zambia': {'id': '6f', 'regions': {
    "None": "6f000000",
    "Zambia": "6f010000"
}},
    'Zimbabwe': {'id': '70', 'regions': {
    "None": "70000000",
    "Zimbabwe": "70010000"
}},
    'Azerbaijan': {'id': '71', 'regions': {
    "None": "71000000",
    "Azerbaijan": "71010000"
}},
    'Mauritania': {'id': '72', 'regions': {
    "None": "72000000",
    "Mauritania": "72010000"
}},
    'Mali': {'id': '73', 'regions': {
    "None": "73000000",
    "Mali": "73010000"
}},
    'Niger': {'id': '74', 'regions': {
    "None": "74000000",
    "Niger": "74010000"
}},
    'Chad': {'id': '75', 'regions': {
    "None": "75000000",
    "Chad": "75010000"
}},
    'Sudan': {'id': '76', 'regions': {
    "None": "76000000",
    "Sudan": "76010000"
}},
    'Eritrea': {'id': '77', 'regions': {
    "None": "77000000",
    "Eritrea": "77010000"
}},
    'Djibouti': {'id': '78', 'regions': {
    "None": "78000000",
    "Djibouti": "78010000"
}},
    'Somalia': {'id': '79', 'regions': {
    "None": "79000000",
    "Somalia": "79010000"
}},
    'Andorra': {'id': '7a', 'regions': {
    "None": "7a000000",
    "Andorra": "7a010000"
}},
    'Gibraltar': {'id': '7b', 'regions': {
    "None": "7b000000",
    "Gibraltar": "7b010000"
}},
    'Guernsey': {'id': '7c', 'regions': {
    "None": "7c000000",
    "Guernsey": "7c010000"
}},
    'Isle of Man': {'id': '7d', 'regions': {
    "None": "7d000000",
    "Isle of Man": "7d010000"
}},
    'Jersey': {'id': '7e', 'regions': {
    "None": "7e000000",
    "Jersey": "7e010000"
}},
    'Monaco': {'id': '7f', 'regions': {
    "None": "7f000000",
    "Monaco": "7f010000"
}},
    'Anguilla': {'id': '8', 'regions': {
    "None": "8000000",
    "Anguilla": "8010000"
}},
    'Taiwan': {'id': '80', 'regions': {
    "None": "80000000",
    "Taipei City": "80020000",
    "Kaohsiung City": "80030000",
    "Keelung City": "80040000",
    "Hsinchu City": "80050000",
    "Taichung City": "80060000",
    "Chiayi City": "80070000",
    "Tainan City": "80080000",
    "New Taipei City": "80090000",
    "Taoyuan City": "800a0000",
    "HsinChu County": "800b0000",
    "Miaoli County": "800c0000",
    "Taichung County": "800d0000",
    "Changhua County": "800e0000",
    "Nantou County": "800f0000",
    "Yunlin County": "80100000",
    "Chiayi County": "80110000",
    "Tainan County": "80120000",
    "Kaohsiung County": "80130000",
    "Pingtung County": "80140000",
    "Yilan County": "80150000",
    "Hualien County": "80160000",
    "Taitung County": "80170000",
    "Penghu County": "80180000",
    "Kinmen County": "80190000",
    "Lienchiang County": "801a0000"
}},
    'South Korea': {'id': '88', 'regions': {
    "None": "88000000",
    "Seoul-teukbyeolsi": "88020000",
    "Busan-gwangyeoksi": "88030000",
    "Daegu-gwangyeoksi": "88040000",
    "Incheon-gwangyeoksi": "88050000",
    "Gwangju-gwangyeoksi": "88060000",
    "Daejeon-gwangyeoksi": "88070000",
    "Ulsan-gwangyeoksi": "88080000",
    "Gyeonggi-do": "88090000",
    "Gangwon-do": "880a0000",
    "Chungcheongbuk-do": "880b0000",
    "Chungcheongnam-do": "880c0000",
    "Jeollabuk-do": "880d0000",
    "Jeollanam-do": "880e0000",
    "Gyeongsangbuk-do": "880f0000",
    "Gyeongsangnam-do": "88100000",
    "Jeju-teukbyeoljachido": "88110000"
}},
    'Antigua and Barbuda': {'id': '9', 'regions': {
    "None": "9000000",
    "Saint John": "9020000",
    "Barbuda": "9030000",
    "Saint George": "9040000",
    "Saint Mary": "9050000",
    "Saint Paul": "9060000",
    "Saint Peter": "9070000",
    "Saint Philip": "9080000"
}},
    'Hong Kong': {'id': '90', 'regions': {
    "None": "90000000",
    "Hong Kong": "90010000"
}},
    'Macao': {'id': '91', 'regions': {
    "None": "91000000",
    "Macao": "91010000"
}},
    'Singapore': {'id': '99', 'regions': {
    "None": "99000000",
    "Singapore": "99010000"
}},
    'Malaysia': {'id': '9c', 'regions': {
    "None": "9c000000",
    "Kuala Lumpur": "9c020000",
    "Johor": "9c030000",
    "Kedah": "9c040000",
    "Kelantan": "9c050000",
    "Melaka": "9c060000",
    "Negeri Sembilan": "9c070000",
    "Pahang": "9c080000",
    "Perak": "9c090000",
    "Perlis": "9c0a0000",
    "Penang": "9c0b0000",
    "Sarawak": "9c0c0000",
    "Selangor": "9c0d0000",
    "Terengganu": "9c0e0000",
    "Labuan": "9c0f0000",
    "Sabah": "9c100000",
    "Putrajaya": "9c110000"
}},
    'Argentina': {'id': 'a', 'regions': {
    "None": "a000000",
    "Distrito Federal": "a020000",
    "Buenos Aires": "a030000",
    "Catamarca": "a040000",
    "Chaco": "a050000",
    "Chubut": "a060000",
    "Córdoba": "a070000",
    "Corrientes": "a080000",
    "Entre Ríos": "a090000",
    "Formosa": "a0a0000",
    "Jujuy": "a0b0000",
    "La Pampa": "a0c0000",
    "La Rioja": "a0d0000",
    "Mendoza": "a0e0000",
    "Misiones": "a0f0000",
    "Neuquén": "a100000",
    "Río Negro": "a110000",
    "Salta": "a120000",
    "San Juan": "a130000",
    "San Luis": "a140000",
    "Santa Cruz": "a150000",
    "Santa Fe": "a160000",
    "Santiago del Estero": "a170000",
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "a180000",
    "Tucumán": "a190000"
}},
    'China': {'id': 'a0', 'regions': {
    "None": "a0000000",
    "Beijing": "a0020000",
    "Chongqing": "a0030000",
    "Shanghai": "a0040000",
    "Tianjin": "a0050000",
    "Anhui": "a0060000",
    "Fujian": "a0070000",
    "Gansu": "a0080000",
    "Guangdong": "a0090000",
    "Guizhou": "a00a0000",
    "Hainan": "a00b0000",
    "Hebei": "a00c0000",
    "Heilongjiang": "a00d0000",
    "Henan": "a00e0000",
    "Hubei": "a00f0000",
    "Húnán": "a0100000",
    "Jiangsu": "a0110000",
    "Jiangxi": "a0120000",
    "Jilin": "a0130000",
    "Liaoning": "a0140000",
    "Qinghai": "a0150000",
    "Shanxi": "a0180000",
    "Shandong": "a0170000",
    "Sichuan": "a0190000",
    "Yunnan": "a01a0000",
    "Zhejiang": "a01b0000",
    "Taiwan": "a01c0000",
    "Guangxi-Zhuangzu": "a01d0000",
    "Nei-Menggu": "a01e0000",
    "Ningxia-huizu": "a01f0000",
    "Xinjiang-Weiwu'er-zu": "a0200000",
    "Xizang": "a0210000",
    "Macao": "a0220000",
    "Hong Kong": "a0230000"
}},
    'U.A.E.': {'id': 'a8', 'regions': {
    "None": "a8000000",
    "Abu Dhabi": "a8020000",
    "Ajman": "a8030000",
    "Ash Shariqah": "a8040000",
    "Ras al-Khaimah": "a8050000",
    "Dubai": "a8060000",
    "Al Fujayrah": "a8070000",
    "Umm al Qaywayn": "a8080000"
}},
    'Saudi Arabia': {'id': 'ae', 'regions': {
    "None": "ae000000",
    "Ar Riyad": "ae020000",
    "Al Bahah": "ae030000",
    "Al Madinah": "ae040000",
    "Ash Sharqiyah": "ae050000",
    "Al Qasim": "ae060000",
    "'Asir": "ae070000",
    "Ha'il": "ae080000",
    "Makkah": "ae090000",
    "Al Hudud ash Shamaliyah": "ae0a0000",
    "Najran": "ae0b0000",
    "Jizan": "ae0c0000",
    "Tabuk": "ae0d0000",
    "Al Jawf": "ae0e0000"
}},
    'Aruba': {'id': 'b', 'regions': {
    "None": "b000000",
    "Aruba": "b010000"
}},
    'San Marino': {'id': 'b8', 'regions': {
    "None": "b8000000",
    "San Marino": "b8010000"
}},
    'Vatican City': {'id': 'b9', 'regions': {
    "None": "b9000000",
    "Vatican City": "b9010000"
}},
    'Bermuda': {'id': 'ba', 'regions': {
    "None": "ba000000",
    "Bermuda": "ba010000"
}},
    'Bahamas': {'id': 'c', 'regions': {
    "None": "c000000",
    "Bahamas": "c010000"
}},
    'Barbados': {'id': 'd', 'regions': {
    "None": "d000000",
    "Barbados": "d010000"
}},
    'Belize': {'id': 'e', 'regions': {
    "None": "e000000",
    "Cayo": "e020000",
    "Belize": "e030000",
    "Corozal": "e040000",
    "Orange Walk": "e050000",
    "Stann Creek": "e060000",
    "Toledo": "e070000"
}},
    'Bolivia': {'id': 'f', 'regions': {
    "None": "f000000",
    "La Paz": "f020000",
    "Chuquisaca": "f030000",
    "Cochabamba": "f040000",
    "El Beni": "f050000",
    "Oruro": "f060000",
    "Pando": "f070000",
    "Potosí": "f080000",
    "Santa Cruz": "f090000",
    "Tarija": "f0a0000"
}},
}

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
        mlcpath = "mlc01/usr/save/system/act/80000001"
        if not os.path.exists(mlcpath):
            os.makedirs(mlcpath)

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
ctk.CTkLabel(root, text="v0.0.4").place(x=610, y=305)

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

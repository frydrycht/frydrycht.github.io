import json
import requests
import urllib3
import threading
import sys
import time

# stop processing flag
stop_flag = False

def check_url_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=2, verify=False)
        return response.status_code != 404
    except Exception:
        return False

def find_urls(data, path=""):
    urls = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            if key == "url" or key == "project_url":
                urls.append((new_path, value))
            else:
                urls.extend(find_urls(value, new_path))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_path = f"{path}[{index}]"
            urls.extend(find_urls(item, new_path))
    return urls

def listen_for_quit():
    global stop_flag
    while True:
        user_input = input()
        if user_input.strip().lower() == 'q':
            stop_flag = True
            print("\nZatrzymywanie... proszę czekać na zakończenie bieżącego sprawdzenia.\n")
            break

def validate_links(json_file):
    global stop_flag
    print("Sprawdzanie linków w pliku...")
    print("Wpisz 'q' i naciśnij Enter w dowolnym momencie, aby zakończyć działanie skryptu.\n")

    with open(json_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    # start listening for quit in background
    threading.Thread(target=listen_for_quit, daemon=True).start()

    for entry in entries:
        if stop_flag:
            break
        entry_id = entry.get("id", "unknown")
        print(f"Analyzing {entry_id}:{entry.get("description","")}")
        urls = find_urls(entry)
        for path, url in urls:
            if stop_flag:
                break
            if url and url.lower().startswith("http"):
                if not check_url_status(url):
                    print(f"❌ Niedostępny link! ID: {entry_id}, Ścieżka: {path} -> {url}")


urllib3.disable_warnings()
validate_links("./data.json")
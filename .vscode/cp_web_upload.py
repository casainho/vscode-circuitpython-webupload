import os
import requests
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
import time

def main():
    # Following the CircuitPython Files Rest API:
    # https://docs.circuitpython.org/en/latest/docs/workflows.html

    source_dir = Path('.').resolve()
    base_url = 'http://' + url + '/fs/'
    
    # Get the list of files and folders from the device
    device_files = list_device_files(base_url, password)

    # Copy project files and folders to device
    for src_path in source_dir.rglob('*'):
        rel_path = src_path.relative_to(source_dir)
        device_path = rel_path.as_posix()

        # Should this file / folder be ignored? base on configs:
        # DEVICE_FILES_FOLDERS_TO_IGNORE
        # PROJECT_FILES_FOLDERS_TO_IGNORE
        if should_ignore(rel_path):
            continue

        # If is a directory, create it on the device
        if src_path.is_dir():
            if device_path not in device_files:
                create_device_folder(base_url, device_path)
        # If is a file, copy it to the device
        else:
            upload_file(base_url, src_path, device_path, device_files)

    # Remove extra device files and folders
    device_paths = {item['name'] for item in device_files}
    local_paths = {p.relative_to(source_dir).as_posix() for p in source_dir.rglob('*') if not should_ignore(p.relative_to(source_dir))}
    
    # Remove files and folders on device that do not exist on the project
    for device_path in device_paths - local_paths:
        if not should_ignore(Path(device_path)):
            delete_device_file_or_folder(base_url, device_path)
    
    # And it is finished
    print("finished")
    

# Get variables from .env file
url = os.getenv("URL")
password = os.getenv("CIRCUITPY_WEB_API_PASSWORD")

device_files_folders_to_ignore = set(os.getenv('DEVICE_FILES_FOLDERS_TO_IGNORE', '').split(','))
device_files_folders_to_ignore = [file_folder.strip() for file_folder in device_files_folders_to_ignore]
device_files_folders_to_ignore = set(device_files_folders_to_ignore)

project_files_folders_to_ignore = set(os.getenv('PROJECT_FILES_FOLDERS_TO_IGNORE', '').split(','))
project_files_folders_to_ignore = [file_folder.strip() for file_folder in project_files_folders_to_ignore]
project_files_folders_to_ignore = set(project_files_folders_to_ignore)

def should_ignore(path):
    parts = set(path.parts)
    return parts & device_files_folders_to_ignore or parts & project_files_folders_to_ignore


def list_device_files(base_url, password):
    
    response = requests.get(base_url, auth=("", password), headers={"Accept": "application/json"})
    if response.status_code == 200:
        try:
            data = response.json()
            files_list = data.get('files', [])  # Extract the 'files' list, default to empty list if not found
            return files_list  # Return only the list of files
        except (ValueError, KeyError):  # Handle JSON decoding or missing 'files' key errors
            print("Error: Invalid JSON response or missing 'files' key")
        return []  # Return an empty list in case of error
    else:
        print(f"Failed to list device files: {response.status_code}")
        return {}


def create_device_folder(base_url, device_path):
    response = requests.put(base_url + device_path + '/', auth=("",password), headers={"X-Timestamp": str(int(time.time_ns()/1000000))})
    if(response.status_code == 201):
        print("Directory created:", device_path)
    elif(response.status_code == 204):
        print("Skipped (already exist):", device_path)
    else:
        print("Failed to create directory:", response.status_code, response.reason)

def upload_file(base_url, src_path, device_path, device_files):
    local_timestamp_ns = src_path.stat().st_mtime_ns
        
    device_file_info = None  # Initialize to None
    for file_info in device_files:  # Iterate through the list of file dictionaries
        if file_info.get('name') == device_path:  # Check if the name matches
            device_file_info = file_info  # Store the matching dictionary
            break  # Exit the loop once found
    
    device_timestamp_ns = 0
    if device_file_info:  # Check if a matching file was found
        device_timestamp_ns = device_file_info.get('modified_ns')

    if device_timestamp_ns and local_timestamp_ns <= device_timestamp_ns:
        return
    
    with open(src_path, 'rb') as file:
        response = requests.put(base_url + device_path, data=file, auth=("", password), headers={"X-Timestamp": str(int(time.time_ns()/1000000))})
        if response.status_code not in [201, 204]:
            print(f"Failed to copy {device_path}: {response.status_code} - {response.reason}")
        else:
            print(f"File copy: {device_path}")


def delete_device_file_or_folder(base_url, device_path):
    response = requests.delete(base_url + device_path, auth=("", password))    
    if response.status_code == 200:
        print(f"Deleted: {device_path}")
    elif response.status_code == 204:
        print(f"Deleted: {device_path}")
    else:
        print(f"Failed to delete {device_path}: {response.status_code}")
        

if __name__ == "__main__":  # Only run main() when the script is executed directly
    main()
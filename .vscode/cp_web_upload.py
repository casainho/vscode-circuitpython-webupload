import sys
import os
import requests
from dotenv import load_dotenv
load_dotenv()

def main():
    ############################################################################
    #
    # The idea is to mirror the project files and folders to the CircuitPyhton
    # device memory - example ESP32-C3.
    #
    # Steps:
    #
    #   1. Get a list of all device folders and files
    #
    #   2. Get a list of all project folders and files
    #
    #   3. Remove all files and folders on the device that do not exist on the project.
    #      Ignore the DEVICE_FILES_FOLDERS_TO_IGNORE.
    #
    #   4. Copy all files and folders from the project to the device that do not exist on the device.
    #      Overwrite the files that are more recent.
    #      Ignore the PROJECT_FILES_FOLDERS_TO_IGNORE.

    # Following the # CircuitPython Files Rest API:
    # https://docs.circuitpython.org/en/latest/docs/workflows.html


    # Get a list of all device folders and files
    device_files = device_get_all_files(baseURL)
    device_files_filtered = filter_files(device_files, device_files_folders_to_ignore)

    # Get a list of all project folders and files
    project_files = project_get_all_files()
    project_files_filtered = filter_files(project_files, project_files_folders_to_ignore)

    # Remove files on device that do not exist on the project
    # Ignore the DEVICE_FILES_FOLDERS_TO_IGNORE.
    files_to_remove = filter_files(device_files_filtered, project_files_filtered)
    device_remove_files(baseURL, files_to_remove)

    # Copy all files and folders from the project to the device that do not exist on the device.
    # Overwrite the files that are more recent.
    # Ignore the PROJECT_FILES_FOLDERS_TO_IGNORE.
    files_to_copy = filter_files_date_higher(project_files_filtered, device_files_filtered)
    device_copy_files(baseURL, files_to_copy)
    
    print("finished")
    

# Get variables from .env file
url = os.getenv("URL")
password = os.getenv("CIRCUITPY_WEB_API_PASSWORD")
device_files_folders_to_ignore = os.getenv("DEVICE_FILES_FOLDERS_TO_IGNORE").split(",")
device_files_folders_to_ignore = [folder.strip() for folder in device_files_folders_to_ignore]
device_files_folders_to_ignore = {item: {} for item in device_files_folders_to_ignore}

project_files_folders_to_ignore = os.getenv("PROJECT_FILES_FOLDERS_TO_IGNORE", "").split(",")
project_files_folders_to_ignore = [folder.strip() for folder in project_files_folders_to_ignore]
project_files_folders_to_ignore = {item: {} for item in project_files_folders_to_ignore}

baseURL = "http://" + url + "/fs"


def device_get_all_files(base_url, path='', files=None):

    if files is None:
        files = {}

    path_url = base_url + '/' + path
    response = requests.get(path_url, auth=("", password), headers={"Accept": "application/json"})

    if response.status_code == 200:
        try:
            data = response.json()
            for file in data.get("files", []):                
                if file.get("directory", True):  # If it's a directory, call recursively
                    device_get_all_files(base_url, path=file['name'] + '/', files=files)
                else:
                    full_file_name = path + file['name']
                    if full_file_name not in files:  # Prevent adding already existing files
                        files[full_file_name] = {'file_size': file['file_size'], 'modified_ns': file['modified_ns']}
  
            return files  # Return the updated files dictionary

        except ValueError:
            print("Error: Unable to parse JSON response.")
    else:
        print(f"Error {response.status_code}: {response.reason}")

    return files


def device_remove_files(base_url, files):

    for file_path in files.keys():
        delete_url = f"{base_url}/{file_path}"
        response = requests.delete(delete_url, auth=("", password))

        if response.status_code != 200:
            print(f"Failed to delete {file_path}: {response.status_code} - {response.reason}")

    return


def device_copy_files(base_url, files):
    for file_path, file_properties in files.items():
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue

        with open(file_path, "rb") as f:
            file_content = f.read()

        # Define the destination URL using the destination file name
        dest_url = f"{base_url}/{file_path}"

        # Send the file using PUT request
        put_response = requests.put(dest_url, data=file_content, auth=("", password), headers={"X-Timestamp": str(os.path.getmtime(file_path))})

        if put_response.status_code not in [201, 204]:
            print(f"Failed to copy {file_path}: {put_response.status_code} - {put_response.reason}")

    return


def project_get_all_files(path='.', files=None):
    if files is None:
        files = {}

    for root, _, file_names in os.walk(path):
        for file_name in file_names:
            full_file_path = os.path.join(root, file_name)
            relative_file_name = os.path.relpath(full_file_path, path)
            file_stat = os.stat(full_file_path)

            if relative_file_name not in files:  # Prevent duplicates
                files[relative_file_name] = {
                    'file_size': file_stat.st_size,
                    'modified_ns': file_stat.st_mtime_ns
                }

    return files


def filter_files(files_folders_dict, filter_dict):
    return {file_name: file_info for file_name, file_info in files_folders_dict.items()
            if not any(ignored in file_name for ignored in filter_dict.keys())}


def filter_files_date_higher(files_folders_dict, filter_dict):
    filtered_files = {}

    for file_name, file_info in files_folders_dict.items():
        should_ignore = False
        
        # Check if the file name is in the filter list dictionary
        for ignored_file_name, ignored_file_info in filter_dict.items():
            if ignored_file_name in file_name:
                # If the file name is in the ignored list, compare modification dates
                if file_info['modified_ns'] <= ignored_file_info['modified_ns']:
                    should_ignore = True
                    break
        
        # If the file should not be ignored, add it to the filtered_files dictionary
        if not should_ignore:
            filtered_files[file_name] = file_info

    return filtered_files


def create_parent_directory(relative_path):
    relative_path = relative_path.removesuffix("/")
    print("Creating parent directory for:",relative_path)
    directory = relative_path.replace(relative_path.split("/")[-1],"")
    dir_response = requests.put(baseURL + directory, auth=("",password))
    if(dir_response.status_code == 201):
        print("Directory created:", directory)
    else:
        print(dir_response.status_code, dir_response.reason)


if __name__ == "__main__":  # Only run main() when the script is executed directly
    main()
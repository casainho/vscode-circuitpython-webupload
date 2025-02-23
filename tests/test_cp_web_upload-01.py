import sys
import os

vscode_path = os.path.join(os.getcwd(), ".vscode")
sys.path.insert(0, vscode_path)
from cp_web_upload import filter_files

def test_filter_files_positive():
    files_folders_dict = {
        "main.py": {"size": 1024},
        "boot_out.txt": {"size": 512},
    }
    filter_dict = {
        "boot_out.txt": {"size": 512},
    }

    expected_output = {
        "main.py": {"size": 1024},
    }

    assert filter_files(files_folders_dict, filter_dict) == expected_output

def test_filter_files_negative():
    files_folders_dict = {
        "main.py": {"size": 1024},
        "boot_out.txt": {"size": 512},
        "settings.toml": {"size": 2048},
    }
    filter_dict = {
        "boot_out.txt": {"size": 512},
    }

    expected_output = {
        "main.py": {"size": 1024},
    }

    assert filter_files(files_folders_dict, filter_dict) != expected_output
    
def test_filter_files_empty_input():
    assert filter_files({}, {}) == {}
    
def test_filter_files_empty_filter():
    files_folders_dict = {
        "main.py": {"size": 1024},
        "boot_out.txt": {"size": 512},
    }
    assert filter_files(files_folders_dict, {}) == files_folders_dict

def test_filter_files_no_match():
    files_folders_dict = {
        "main.py": {"size": 1024},
        "boot_out.txt": {"size": 512},
    }
    filter_dict = {
        "settings.toml": {"size": 512},
    }
    assert filter_files(files_folders_dict, filter_dict) == files_folders_dict
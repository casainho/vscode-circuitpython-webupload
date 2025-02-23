import unittest.mock
import sys
import os
from dotenv import load_dotenv
load_dotenv()

vscode_path = os.path.join(os.getcwd(), ".vscode")
sys.path.insert(0, vscode_path)
from cp_web_upload import device_get_all_files

# Get variables from .env file
password = os.getenv("CIRCUITPY_WEB_API_PASSWORD")

def test_device_get_all_files():
    # 1. Arrange (Set up the mock)
    mock_response = unittest.mock.Mock()  # Create a mock response object
    mock_response.status_code = 200  # Simulate a successful response
    mock_response.json.return_value = {  # Simulate the JSON data returned by the API
        "files": [
            {"name": "main.py", "directory": False, "file_size": 1024, "modified_ns": 1678886400000000000},
        ]
    }

    # Mock the requests.get call to return our mock response
    with unittest.mock.patch("requests.get") as mock_get:
        mock_get.return_value = mock_response

        # 2. Act (Call the function)
        base_url = "http://mockurl/fs"  # Doesn't matter; it's mocked
        files = device_get_all_files(base_url)

        # 3. Assert (Check the results)
        expected_files = {
            "main.py": {"file_size": 1024, "modified_ns": 1678886400000000000},
        }
        assert files == expected_files

        # Ensure that requests.get was called with the correct URL
        mock_get.assert_called_once_with(
            "http://mockurl/fs/",
            auth=('', password),
            headers={'Accept': 'application/json'}
        )

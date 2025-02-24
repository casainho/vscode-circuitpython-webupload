# vscode-circuitpython-webupload
Task definition and Python script to upload from VS Code to CircuitPython board via web workflow REST API.

CircuitPython 8.x adds [web workflow](https://docs.circuitpython.org/en/latest/docs/workflows.html#web) allowing code to be edited/uploaded via the local network. There is built-in browser support and also a Web REST API. This project utilizes the latter to upload a file directly from VS Code.

## Setup
* Python 3 installed and in your path.
  * [requests](https://pypi.org/project/requests/) and [python-dotenv](https://pypi.org/project/python-dotenv/)
* CircuitPython 8.x on your board.
* Board connected to same Wi-Fi with web workflow configured and reachable from machine running VS Code.
  * [This is for ESP32 (original) but should be close enough for any of the ESP32-S2 or S3 boards, also](https://learn.adafruit.com/circuitpython-with-esp32-quick-start/setting-up-web-workflow).
* Copy .vscode directory from this project to the root of your CircuitPython project. It does not have to be copied to your CircuitPython board, just the machine running VS Code.
* Edit .vscode/.env and set _baseURL_, CIRCUITPY_WEB_API_PASSWORD and the files and folders to be ignored.
* To update the files on the device, execute the "Run Task..." command.
  * Menu: _Terminal, Run Task..._
  * Command pallet: _Tasks: Run Task_
  * Shortcut keys: TODO:DOCUMENT_THESE
  * [Keybindings can be configured to call a specific task](https://code.visualstudio.com/docs/editor/tasks#_binding-keyboard-shortcuts-to-tasks).

NOTE:
  * New files and folders that exist in the project folder but not on the device will be copied to the device.
  * Files and folders present on the device but missing from the project folder will be deleted from the device.


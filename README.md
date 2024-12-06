# 54rt Project Setup

## Prerequisites

1. Install Python 3.11 or higher
   - Download from [Python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. Install VS Code Pymakr Extension
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Pymakr" 
   - Click Install

3. Install CP210x USB-to-UART Driver
   - For Windows:
     - Download driver from [Silicon Labs website](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
     - Follow installation instructions
   - For Linux:
     - Drivers are typically included in the kernel
     - Add your user to the dialout group:
       ```bash
       sudo usermod -a -G dialout $USER
       ```
     - Log out and back in for changes to take effect

4. WiPy Setup
   - Connect WiPy board via USB
   - Verify connection in Device Manager (Windows) or `lsusb` (Linux)
   - Note the COM port or device path

5. Clone this repository

6. Essential Pymakr Commands
   In VS Code, press Ctrl+Shift+P then:
   - Pymakr > Upload Project - Upload entire project
   - Pymakr > Connect - Connect to device
   - Pymakr > Global Settings - Global configuration
   - Pymakr > Run Current File - Execute current file

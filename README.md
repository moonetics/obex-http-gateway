# OBEX-to-HTTP Gateway

A lightweight Bluetooth-to-HTTP file transfer system. Send files over Bluetooth (OBEX Object Push) from any client (Python GUI or Android), forward them to a Flask HTTP server, and view/download them in a modern web dashboard.

## Features

- **Bluetooth Gateway**  
  Listens for OBEX Object Push on a device named `BT-Gateway`, saves incoming files temporarily, and forwards them via HTTP POST to your Flask server.

- **Flask HTTP Server & Dashboard**  
  Serves a responsive, minimalistic dashboard at `/dashboard` that displays all uploaded files with name, size, modification time, and a download button.

- **Python GUI Client**  
  A Tkinter-based GUI (`sender.py`) to browse for a file, scan for Bluetooth devices, select your gateway, and send with a single click.

## Prerequisites

- **Python 3.8+**  
- **Bluetooth adapter** on your host machine:  
  - On Windows: rename the adapter to **BT-Gateway** and enable “Allow Bluetooth devices to find this PC.”  
  - On Linux/macOS: ensure BlueZ (or the native Bluetooth stack) is installed and enabled.  
- **Build tools** (Windows only):  
  - [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or use `pipwin install pybluez`.

## Installation

1. **Clone this repository**  
   ```bash
   git clone https://github.com/yourusername/obex-http-gateway.git
   cd obex-http-gateway
   ```

## Screenshot
![Sender GUI](https://github.com/user-attachments/assets/464e5d00-16ab-4c26-89dd-4afd62d9cb4b)
![Web Dashboard](https://github.com/user-attachments/assets/f453261b-f01d-4d42-9b11-9f60ba098686)

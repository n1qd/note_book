import hashlib
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
import pymysql
from private import db_config

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class LoginWidget(QWidget):
    login_successful = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.username_input = QLineEdit(placeholderText="Username")
        self.username_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(placeholderText="Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.register_button.clicked.connect(self.go_to_register)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password cannot be empty.")
            return

        conn = pymysql.connect(**db_config)
        with conn.cursor() as c:
            c.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            user = c.fetchone()
        conn.close()

        if user and user[1] == hash_password(password):
            self.login_successful.emit(user[0])
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")

    def go_to_register(self):
        self.parentWidget().parentWidget().stacked_widget.setCurrentWidget(
            self.parentWidget().parentWidget().register_widget)

class RegisterWidget(QWidget):
    registration_successful = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit(placeholderText="Username")
        self.username_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(placeholderText="Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit(placeholderText="Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.confirm_password_input)

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        self.back_button = QPushButton("Back to Login")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.back_button.clicked.connect(self.go_to_login)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        conn = pymysql.connect(**db_config)
        try:
            with conn.cursor() as c:
                c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hash_password(password)))
                conn.commit()
            self.registration_successful.emit()
        except pymysql.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists.")
        finally:
            conn.close()

    def go_to_login(self):
        self.parentWidget().parentWidget().stacked_widget.setCurrentWidget(self.parentWidget().parentWidget().login_widget)

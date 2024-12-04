from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from auth import LoginWidget, RegisterWidget
from notes import NotesWidget

class NoteApp(QWidget):
    def __init__(self):
        super().__init__()
        self.user_id = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Notes")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #121212; color: #FFFFFF; font-family: 'Comfortaa', sans-serif;")

        self.stacked_widget = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)

        self.login_widget = LoginWidget(self.stacked_widget)
        self.login_widget.login_successful.connect(self.on_login_successful)
        self.stacked_widget.addWidget(self.login_widget)

        self.register_widget = RegisterWidget(self.stacked_widget)
        self.register_widget.registration_successful.connect(self.on_registration_successful)
        self.stacked_widget.addWidget(self.register_widget)

        self.notes_widget = NotesWidget(self.stacked_widget)
        self.stacked_widget.addWidget(self.notes_widget)

        self.setLayout(layout)

    def on_login_successful(self, user_id):
        self.user_id = user_id
        self.notes_widget.user_id = user_id
        self.notes_widget.load_notes(self.user_id)
        self.notes_widget.load_categories(self.user_id)
        self.stacked_widget.setCurrentWidget(self.notes_widget)

    def on_registration_successful(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)

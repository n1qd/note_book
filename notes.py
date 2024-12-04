from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QListWidget, \
    QComboBox, QDialog, QScrollArea, QSizePolicy, QLabel, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import pymysql

from private import db_config

class NotesWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.user_id = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.note_list = QListWidget()
        self.note_list.itemClicked.connect(self.load_note)
        self.note_list.setStyleSheet("background-color: #343A40; color: #FFFFFF;")
        layout.addWidget(self.note_list)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(placeholderText="Search")
        self.search_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        self.search_input.textChanged.connect(self.search_notes)
        search_layout.addWidget(self.search_input)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        self.category_combo.currentTextChanged.connect(self.filter_notes)
        search_layout.addWidget(self.category_combo)

        layout.addLayout(search_layout)

        form_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        self.title_input = QLineEdit(placeholderText="Title")
        self.title_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        left_layout.addWidget(self.title_input)

        self.content_input = QTextEdit()
        self.content_input.setFont(QFont("Comfortaa", 12))
        self.content_input.setPlaceholderText("Note content")
        self.content_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px; QScrollBar:vertical { width: 10px; }")
        left_layout.addWidget(self.content_input)

        self.category_input = QLineEdit(placeholderText="Category")
        self.category_input.setStyleSheet("background-color: #495057; color: #FFFFFF; border: none; border-radius: 5px; padding: 5px;")
        left_layout.addWidget(self.category_input)

        form_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()
        self.new_note_button = QPushButton("New Note")
        self.new_note_button.setStyleSheet("""
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
        self.new_note_button.clicked.connect(self.clear_fields)
        right_layout.addWidget(self.new_note_button)

        self.add_button = QPushButton("Add")
        self.add_button.setStyleSheet("""
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
        self.add_button.clicked.connect(self.save_note)
        right_layout.addWidget(self.add_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
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
        self.cancel_button.clicked.connect(self.clear_fields)
        right_layout.addWidget(self.cancel_button)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.logout_button.clicked.connect(self.logout)
        right_layout.addWidget(self.logout_button)

        form_layout.addLayout(right_layout)

        layout.addLayout(form_layout)

        self.setLayout(layout)

        self.note_preview = NotePreview(self)
        self.note_preview.delete_note.connect(self.delete_note)

    def logout(self):
        self.user_id = None
        self.clear_fields()
        self.note_list.clear()
        self.category_combo.clear()
        self.parentWidget().parentWidget().stacked_widget.setCurrentWidget(self.parentWidget().parentWidget().login_widget)

    def load_notes(self, user_id):
        conn = pymysql.connect(**db_config)
        try:
            with conn.cursor() as c:
                c.execute("SELECT id, title FROM notes WHERE user_id = %s", (user_id,))
                notes = c.fetchall()
            self.note_list.clear()
            for note in notes:
                self.note_list.addItem(note[1])
        finally:
            conn.close()

    def load_categories(self, user_id):
        conn = pymysql.connect(**db_config)
        try:
            with conn.cursor() as c:
                c.execute("SELECT DISTINCT category FROM notes WHERE user_id = %s", (user_id,))
                categories = c.fetchall()
            self.category_combo.clear()
            self.category_combo.addItem("All categories")
            for category in categories:
                self.category_combo.addItem(category[0])
        finally:
            conn.close()

    def load_note(self, item):
        title = item.text()
        conn = pymysql.connect(**db_config)
        try:
            with conn.cursor() as c:
                c.execute("SELECT content, category FROM notes WHERE title = %s AND user_id = %s", (title, self.user_id))
                note = c.fetchone()
            if note:
                self.title_input.setText(title)
                self.content_input.setText(note[0])
                self.category_input.setText(note[1])
                self.note_preview.update_note_preview(title, note[0], note[1])
                self.note_preview.show()
        finally:
            conn.close()

    def save_note(self):
        title = self.title_input.text()
        content = self.content_input.toPlainText()
        category = self.category_input.text()

        if not title or not content:
            QMessageBox.warning(self, "Error", "Title and content cannot be empty.")
            return

        conn = pymysql.connect(**db_config)
        try:
            with conn.cursor() as c:
                c.execute("INSERT INTO notes (user_id, title, content, category) VALUES (%s, %s, %s, %s)",
                          (self.user_id, title, content, category))
                conn.commit()
            self.load_notes(self.user_id)
            self.load_categories(self.user_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def delete_note(self, title):
        conn = pymysql.connect(**db_config)
        try:
            with conn.cursor() as c:
                c.execute("DELETE FROM notes WHERE title = %s AND user_id = %s", (title, self.user_id))
                conn.commit()
            self.load_notes(self.user_id)
            self.load_categories(self.user_id)
            self.clear_fields()
        finally:
            conn.close()

    def clear_fields(self):
        self.title_input.clear()
        self.content_input.clear()
        self.category_input.clear()

    def search_notes(self, text):
        conn = pymysql.connect(**db_config)
        try:
            with conn.cursor() as c:
                c.execute("SELECT id, title FROM notes WHERE user_id = %s AND (title LIKE %s OR content LIKE %s)",
                          (self.user_id, f"%{text}%", f"%{text}%"))
                notes = c.fetchall()
            self.note_list.clear()
            for note in notes:
                self.note_list.addItem(f"{note[1]}")
        finally:
            conn.close()

    def filter_notes(self, category):
        conn = pymysql.connect(**db_config)
        try:
            with conn.cursor() as c:
                if category == "All categories":
                    c.execute("SELECT id, title FROM notes WHERE user_id = %s", (self.user_id,))
                else:
                    c.execute("SELECT id, title FROM notes WHERE user_id = %s AND category = %s", (self.user_id, category))
                notes = c.fetchall()
            self.note_list.clear()
            for note in notes:
                self.note_list.addItem(f"{note[1]}")
        finally:
            conn.close()

class NotePreview(QDialog):
    delete_note = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Note Preview")
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet("background-color: #212529; color: #FFFFFF; font-family: 'Segoe UI', Arial, sans-serif;")

        layout = QVBoxLayout()

        self.title_label = QLabel()
        self.title_label.setFont(QFont("Comfortaa", 20, QFont.Bold))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #2E2E2E;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: #555555;
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #777777;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self.content_label = QLabel()
        self.content_label.setFont(QFont("Comfortaa", 12))
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.RichText)
        self.content_label.setAlignment(Qt.AlignJustify)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.content_label.setStyleSheet("border: none; margin: 0px 5px;")
        self.scroll_area.setWidget(self.content_label)
        layout.addWidget(self.scroll_area)

        self.category_label = QLabel()
        self.category_label.setFont(QFont("Comfortaa", 10, QFont.Bold))
        layout.addWidget(self.category_label)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.delete_button.clicked.connect(self.delete_current_note)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

    def update_note_preview(self, title, content, category):
        self.title_label.setText(title)
        self.content_label.setText(content)
        self.category_label.setText(f"Category: {category}")
        self.content_label.setStyleSheet("border: none; margin: 0px 5px;")

    def delete_current_note(self):
        title = self.title_label.text()
        self.delete_note.emit(title)
        self.close()

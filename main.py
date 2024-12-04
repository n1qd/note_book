import sys
from PyQt5.QtWidgets import QApplication
from ui import NoteApp
from database import create_database

def main():
    create_database()  # Создание базы данных при запуске
    app = QApplication(sys.argv)
    ex = NoteApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

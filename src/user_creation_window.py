from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from database import get_connection, create_user, get_roles

class UserCreationWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Crear Usuario')
        self.layout = QVBoxLayout()

        self.username_label = QLabel('Username')
        self.username_input = QLineEdit()
        self.password_label = QLabel('Password')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_label = QLabel('Role')
        self.role_combobox = QComboBox()
        self.role_combobox.addItems(get_roles())
        self.create_button = QPushButton('Crear')
        self.create_button.clicked.connect(self.create_user)

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.role_label)
        self.layout.addWidget(self.role_combobox)
        self.layout.addWidget(self.create_button)
        self.setLayout(self.layout)

    def create_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combobox.currentText()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'El nombre de usuario y la contraseña no pueden estar vacíos')
            return
        
        try:
            connection = get_connection()
            cursor = connection.cursor()
            create_user(cursor, username, password, role)
            connection.close()
            QMessageBox.information(self, 'Éxito', 'Usuario creado exitosamente')
            self.username_input.clear()
            self.password_input.clear()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'No se pudo crear el usuario: {e}')

def open_user_creation_window():
    window = UserCreationWindow()
    return window

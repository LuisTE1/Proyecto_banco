from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from database import get_connection

def verify_login(username, password):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT U.id, R.role_name FROM Usuarios U JOIN Roles R ON U.role_id = R.id WHERE U.username = ? AND U.password = ?", (username, password))
                return cursor.fetchone()
    except Exception as e:
        QMessageBox.critical(None, 'Error de Conexión', f'Error al conectar con la base de datos: {str(e)}')
        return None

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setWindowTitle('Registro De Bancos')
        self.resize(800, 400)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.image_label = QLabel(self)
        pixmap = QPixmap('src/images/logo.jpg')
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(300, 400)

        self.username_label = QLabel('Usuario')
        self.username_label.setFont(QFont('Arial', 12))
        self.username_input = QLineEdit()
        self.username_input.setFixedSize(300, 30)
        self.username_input.textChanged.connect(self.check_input)

        self.password_label = QLabel('Password')
        self.password_label.setFont(QFont('Arial', 12))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedSize(300, 30)
        self.password_input.textChanged.connect(self.check_input)

        self.login_button = QPushButton('Ingresar')
        self.login_button.setFont(QFont('Arial', 12))
        self.login_button.setFixedSize(150, 40)
        self.login_button.setEnabled(False)
        self.login_button.clicked.connect(self.login)

        self.layout.addWidget(self.image_label, 0, 0, 3, 1)
        self.layout.addWidget(self.username_label, 0, 1)
        self.layout.addWidget(self.username_input, 0, 2)
        self.layout.addWidget(self.password_label, 1, 1)
        self.layout.addWidget(self.password_input, 1, 2)
        self.layout.addWidget(self.login_button, 2, 1, 1, 2)

    def check_input(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        self.login_button.setEnabled(bool(username and password))

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        result = verify_login(username, password)
        
        if result:
            self.user_id, role = result
            self.username = username  # Guardar el nombre de usuario
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Usuario o contraseña incorrectos')

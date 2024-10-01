from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database import create_role

class RoleManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gestionar Roles')
        self.layout = QVBoxLayout()

        self.role_label = QLabel('Nuevo Rol')
        self.role_input = QLineEdit()
        self.create_button = QPushButton('Crear Rol')
        self.create_button.clicked.connect(self.create_role)

        self.layout.addWidget(self.role_label)
        self.layout.addWidget(self.role_input)
        self.layout.addWidget(self.create_button)
        self.setLayout(self.layout)

    def create_role(self):
        role_name = self.role_input.text().strip()
        if not role_name:
            QMessageBox.warning(self, 'Error', 'El nombre del rol no puede estar vacío')
            return
        try:
            create_role(role_name)
            QMessageBox.information(self, 'Éxito', 'Rol creado exitosamente')
            self.role_input.clear()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'No se pudo crear el rol: {e}')

def open_role_management_window():
    window = RoleManagementWindow()
    return window

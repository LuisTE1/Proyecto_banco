from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QMessageBox
from database import get_users, obtener_permisos, actualizar_permisos

# Lista centralizada de todas las ventanas disponibles en la aplicación
ALL_WINDOWS = [
    ('admin_window', 'Ventana Admin'),
    ('user_management_window', 'Gestionar Usuarios'),
    ('role_management_window', 'Gestionar Roles'),
    ('user_creation_window', 'Crear Usuario'),
    ('permission_management_window', 'Gestionar Permisos'),
    ('cashier_window', 'Ventana Cajero'),
    # Agrega aquí cualquier nueva ventana que añadas a tu aplicación
]

class PermissionManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gestionar Permisos')
        self.layout = QVBoxLayout()

        self.user_label = QLabel('Seleccionar Usuario')
        self.user_combobox = QComboBox()
        self.user_combobox.addItems([f"{user[0]} - {user[1]}" for user in get_users()])
        self.user_combobox.currentIndexChanged.connect(self.load_permissions)

        # Crear checkboxes dinámicamente para todas las ventanas en ALL_WINDOWS
        self.permissions = {window[0]: QCheckBox(window[1]) for window in ALL_WINDOWS}

        self.save_button = QPushButton('Guardar Permisos')
        self.save_button.clicked.connect(self.save_permissions)

        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.user_combobox)
        for checkbox in self.permissions.values():
            self.layout.addWidget(checkbox)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

    def load_permissions(self):
        user_id = int(self.user_combobox.currentText().split(' - ')[0])
        permisos = obtener_permisos(user_id)
        for ventana, permitido in permisos:
            if ventana in self.permissions:
                self.permissions[ventana].setChecked(permitido)

    def save_permissions(self):
        user_id = int(self.user_combobox.currentText().split(' - ')[0])
        permisos = {ventana: checkbox.isChecked() for ventana, checkbox in self.permissions.items()}
        try:
            actualizar_permisos(user_id, permisos)
            QMessageBox.information(self, 'Éxito', 'Permisos actualizados exitosamente')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'No se pudieron actualizar los permisos: {e}')

def open_permission_management_window():
    window = PermissionManagementWindow()
    return window

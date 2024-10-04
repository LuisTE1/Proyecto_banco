from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from database import get_users, update_user, get_roles, eliminar_usuario, obtener_permisos, actualizar_permisos, create_user, get_connection

# Lista centralizada de todas las ventanas disponibles en la aplicación
ALL_WINDOWS = [
    ('user_management_window', 'Gestionar Usuarios'),
    ('cashier_window', 'Ventana Cajero'),
    ('table_cashier_window', 'Tabla Bancos'),
    # Agrega aquí cualquier nueva ventana que añadas a tu aplicación
]

class UserManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gestionar Usuarios')
        self.resize(800, 600)  # Establecer tamaño específico de la ventana
        self.layout = QVBoxLayout()

        # Tabla de usuarios
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Username', 'Password', 'Role'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self.load_permissions)
        self.table.keyPressEvent = self.handle_key_press
        self.load_users()

        # Botones de acción
        self.update_button = QPushButton('Actualizar Usuario')
        self.update_button.clicked.connect(self.update_user)
        
        self.save_button = QPushButton('Guardar Usuario')
        self.save_button.clicked.connect(self.save_user)

        self.delete_button = QPushButton('Eliminar Usuario')
        self.delete_button.clicked.connect(self.delete_user)

        # Layout para los botones
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)

        # Sección de gestión de permisos
        self.permission_label = QLabel('Gestionar Permisos')

        # Crear checkboxes dinámicamente para todas las ventanas en ALL_WINDOWS
        self.permissions = {window[0]: QCheckBox(window[1]) for window in ALL_WINDOWS}

        self.save_permissions_button = QPushButton('Guardar Permisos')
        self.save_permissions_button.clicked.connect(self.save_permissions)

        # Layout para la gestión de permisos
        permission_layout = QVBoxLayout()
        permission_layout.addWidget(self.permission_label)
        for checkbox in self.permissions.values():
            permission_layout.addWidget(checkbox)
        permission_layout.addWidget(self.save_permissions_button)

        # Agregar widgets al layout principal
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_layout)
        self.layout.addLayout(permission_layout)
        self.setLayout(self.layout)

    def load_users(self):
        users = get_users()
        self.table.setRowCount(len(users))
        for row_idx, user in enumerate(users):
            id_item = QTableWidgetItem(str(user[0]))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Hacer que el ID no sea editable
            self.table.setItem(row_idx, 0, id_item)
            self.table.setItem(row_idx, 1, QTableWidgetItem(user[1]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(user[2]))
            role_combobox = QComboBox()
            role_combobox.addItems(get_roles())
            role_combobox.setCurrentText(user[3])
            self.table.setCellWidget(row_idx, 3, role_combobox)

    def load_permissions(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            for checkbox in self.permissions.values():
                checkbox.setChecked(False)
            return

        user_id_item = self.table.item(self.table.currentRow(), 0)
        if user_id_item and user_id_item.text().isdigit():
            user_id = int(user_id_item.text())
            permisos_lista = obtener_permisos(user_id)
            
            # Convertir la lista de permisos en un diccionario
            permisos = {ventana: permiso for ventana, permiso in permisos_lista}
            
            for ventana, checkbox in self.permissions.items():
                checkbox.setChecked(permisos.get(ventana, False))

    def save_permissions(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Error', 'Selecciona un usuario para guardar permisos')
            return
        user_id_item = self.table.item(self.table.currentRow(), 0)
        if user_id_item and user_id_item.text().isdigit():
            user_id = int(user_id_item.text())
            permisos = {ventana: checkbox.isChecked() for ventana, checkbox in self.permissions.items()}
            try:
                actualizar_permisos(user_id, permisos)
                QMessageBox.information(self, 'Éxito', 'Permisos actualizados exitosamente')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'No se pudieron actualizar los permisos: {e}')
        else:
            QMessageBox.warning(self, 'Error', 'Selecciona un usuario válido para guardar permisos')

    def update_user(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Error', 'Selecciona un usuario para actualizar')
            return

        user_id_item = self.table.item(row, 0)
        if user_id_item and user_id_item.text().isdigit():
            user_id = int(user_id_item.text())
            username = self.table.item(row, 1).text().strip()
            password = self.table.item(row, 2).text().strip()
            role = self.table.cellWidget(row, 3).currentText()

            if not username or not password:
                QMessageBox.warning(self, 'Error', 'El nombre de usuario y la contraseña no pueden estar vacíos')
                return

            try:
                update_user(user_id, username, password, role)
                QMessageBox.information(self, 'Éxito', 'Usuario actualizado exitosamente')
                self.load_users()  # Recargar la tabla después de actualizar
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'No se pudo actualizar el usuario: {e}')
        else:
            QMessageBox.warning(self, 'Error', 'Selecciona un usuario válido para actualizar')

    def delete_user(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Error', 'Selecciona un usuario para eliminar')
            return

        user_id_item = self.table.item(row, 0)
        if user_id_item and user_id_item.text().isdigit():
            user_id = int(user_id_item.text())
            try:
                eliminar_usuario(user_id)
                QMessageBox.information(self, 'Éxito', 'Usuario eliminado exitosamente')
                self.load_users()  # Recargar la tabla después de eliminar
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'No se pudo eliminar el usuario: {e}')
        else:
            QMessageBox.warning(self, 'Error', 'Selecciona un usuario válido para eliminar')
    def handle_key_press(self, event):
        if event.key() == Qt.Key_Down:
            current_row = self.table.currentRow()
            if current_row == self.table.rowCount() - 1:
                self.add_blank_row()
        super(QTableWidget, self.table).keyPressEvent(event)

    def add_blank_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        new_id = self.generate_new_id()
        id_item = QTableWidgetItem(str(new_id))
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Hacer que el ID no sea editable
        self.table.setItem(row_count, 0, id_item)
        self.table.setItem(row_count, 1, QTableWidgetItem(''))
        self.table.setItem(row_count, 2, QTableWidgetItem(''))
        role_combobox = QComboBox()
        role_combobox.addItems(get_roles())
        self.table.setCellWidget(row_count, 3, role_combobox)
        self.table.selectRow(row_count)

    def get_role_id(self, role_name):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM Roles WHERE role_name = ?", (role_name,))
        result = cursor.fetchone()
        connection.close()
        if result:
            return result[0]
        else:
            raise ValueError(f'Rol no encontrado: {role_name}')

    def save_user(self):
        row = self.table.currentRow()
        user_id_item = self.table.item(row, 0)
        username = self.table.item(row, 1).text().strip()
        password = self.table.item(row, 2).text().strip()
        role = self.table.cellWidget(row, 3).currentText()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'El nombre de usuario y la contraseña no pueden estar vacíos')
            return

        if not any(checkbox.isChecked() for checkbox in self.permissions.values()):
            QMessageBox.warning(self, 'Error', 'Selecciona al menos un permiso antes de guardar')
            return
        
        try:
            connection = get_connection()
            cursor = connection.cursor()    
            role_id = self.get_role_id(role)
            
            cursor.execute("SET IDENTITY_INSERT Usuarios ON")
            cursor.execute("INSERT INTO Usuarios (id, username, password, role_id) VALUES (?, ?, ?, ?)", (int(user_id_item.text()), username, password, role_id))
            cursor.execute("SET IDENTITY_INSERT Usuarios OFF")
            
            connection.commit()
            
            # Guardar permisos
            permisos = {ventana: checkbox.isChecked() for ventana, checkbox in self.permissions.items()}
            actualizar_permisos(int(user_id_item.text()), permisos)
            
            connection.close()
            QMessageBox.information(self, 'Éxito', 'Usuario creado exitosamente')
            self.load_users()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'No se pudo crear el usuario: {e}')

    def generate_new_id(self):
        # Generar un nuevo ID basado en el último ID en la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(id) FROM Usuarios")  # Asegúrate de que 'Usuarios' es el nombre correcto de la tabla
        result = cursor.fetchone()
        connection.close()
        if result and result[0]:
            return result[0] + 1
        return 1

def open_user_management_window():
    window = UserManagementWindow()
    window.show()
    return window

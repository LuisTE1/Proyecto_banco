from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox
from database import obtener_permisos
from cashier_window import open_cashier_window
from user_management_window import open_user_management_window
from role_management_window import open_role_management_window
from table_cashier_window import open_table_cashier_window


class MainWindow(QMainWindow):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username  # Guardar el nombre de usuario
        self.permisos = obtener_permisos(self.user_id)
        self.initUI()
        self.windows = {}  # Diccionario para mantener referencias a las ventanas abiertas

    def initUI(self):
        self.setWindowTitle('Aplicación Principal')
        self.showMaximized()  # Mostrar la ventana maximizada al iniciar

        # Crear acciones para las diferentes ventanas
        ventana_cajero = QAction('Ventana Cajero', self)
        ventana_cajero.setEnabled(self.tiene_permiso('cashier_window'))
        ventana_cajero.triggered.connect(self.open_cashier_window)
        self.menuBar().addAction(ventana_cajero)

        ventana_gestion_usuarios = QAction('Gestionar Usuarios', self)
        ventana_gestion_usuarios.setEnabled(self.tiene_permiso('user_management_window'))
        ventana_gestion_usuarios.triggered.connect(self.open_user_management_window)
        self.menuBar().addAction(ventana_gestion_usuarios)

        ventana_gestion_roles = QAction('Gestionar Roles', self)
        ventana_gestion_roles.setEnabled(self.tiene_permiso('role_management_window'))
        ventana_gestion_roles.triggered.connect(self.open_role_management_window)
        self.menuBar().addAction(ventana_gestion_roles)

       
        # Crear acción para la nueva ventana table_cashier_window
        ventana_table_cashier = QAction('Tabla de bancos', self)
        ventana_table_cashier.setEnabled(self.tiene_permiso('table_cashier_window'))
        ventana_table_cashier.triggered.connect(self.open_table_cashier_window)
        self.menuBar().addAction(ventana_table_cashier)
        
    def tiene_permiso(self, ventana):
        for permiso in self.permisos:
            if permiso[0] == ventana:
                return permiso[1]
        return False

    def open_cashier_window(self):
        if self.tiene_permiso('cashier_window'):
            self.windows['cashier_window'] = open_cashier_window(self.username)  # Pasar el nombre de usuario
            self.windows['cashier_window'].show()
        else:
            QMessageBox.warning(self, 'Acceso Denegado', 'No tienes permiso para acceder a esta ventana.')

    def open_user_management_window(self):
        if self.tiene_permiso('user_management_window'):
            self.windows['user_management_window'] = open_user_management_window()
            self.windows['user_management_window'].show()
        else:
            QMessageBox.warning(self, 'Acceso Denegado', 'No tienes permiso para acceder a esta ventana.')

    def open_role_management_window(self):
        if self.tiene_permiso('role_management_window'):
            self.windows['role_management_window'] = open_role_management_window()
            self.windows['role_management_window'].show()
        else:
            QMessageBox.warning(self, 'Acceso Denegado', 'No tienes permiso para acceder a esta ventana.')


    def open_table_cashier_window(self):
        if self.tiene_permiso('table_cashier_window'):
            self.windows['table_cashier_window'] = open_table_cashier_window()
            self.windows['table_cashier_window'].show()
        else:
            QMessageBox.warning(self, 'Acceso Denegado', 'No tienes permiso para acceder a esta ventana.')


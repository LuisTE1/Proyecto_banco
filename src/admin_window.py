from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from user_creation_window import UserCreationWindow
from role_management_window import RoleManagementWindow
from user_management_window import UserManagementWindow
from permission_management_window import PermissionManagementWindow

def open_admin_window():
    admin_window = QMainWindow()
    admin_window.setWindowTitle('Administrador')
    admin_window.setGeometry(100, 100, 600, 400)
    
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    label = QLabel('Bienvenido, Administrador')
    create_user_button = QPushButton('Crear Usuario')
    create_user_button.clicked.connect(open_user_creation_window)
    manage_roles_button = QPushButton('Gestionar Roles')
    manage_roles_button.clicked.connect(open_role_management_window)
    manage_users_button = QPushButton('Gestionar Usuarios')
    manage_users_button.clicked.connect(open_user_management_window)
    manage_permissions_button = QPushButton('Gestionar Permisos')
    manage_permissions_button.clicked.connect(open_permission_management_window)
    
    layout.addWidget(label)
    layout.addWidget(create_user_button)
    layout.addWidget(manage_roles_button)
    layout.addWidget(manage_users_button)
    layout.addWidget(manage_permissions_button)
    central_widget.setLayout(layout)
    admin_window.setCentralWidget(central_widget)
    return admin_window

def open_user_creation_window():
    user_creation_window = UserCreationWindow()
    user_creation_window.exec_()

def open_role_management_window():
    role_management_window = RoleManagementWindow()
    role_management_window.exec_()

def open_user_management_window():
    user_management_window = UserManagementWindow()
    user_management_window.exec_()

def open_permission_management_window():
    permission_management_window = PermissionManagementWindow()
    permission_management_window.exec_()

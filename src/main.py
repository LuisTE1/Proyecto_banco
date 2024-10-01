from PyQt5.QtWidgets import QApplication, QDialog
import sys
from login import LoginWindow
from cashier_window import get_connection, open_cashier_window
from main_window import MainWindow  # Asegúrate de importar MainWindow

def get_user_role(user_id):
    # Función para obtener el rol del usuario desde la base de datos
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT R.role_name FROM Usuarios U JOIN Roles R ON U.role_id = R.id WHERE U.id = ?", (user_id,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Mostrar la ventana de inicio de sesión
    login_window = LoginWindow()
    if login_window.exec_() == QDialog.Accepted:
        # Obtener el ID y el nombre de usuario después de un inicio de sesión exitoso
        user_id = login_window.user_id
        username = login_window.username
        
        # Obtener el rol del usuario
        user_role = get_user_role(user_id)
        
        # Abrir la ventana correspondiente según el rol del usuario
        if user_role == 'cajero':
            cashier_window = open_cashier_window(username)
            cashier_window.show()
        else:
            main_window = MainWindow(user_id, username)  # Pasar el nombre de usuario
            main_window.show()
        
        # Ejecutar la aplicación
        sys.exit(app.exec_())

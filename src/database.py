import pyodbc

def get_connection():
    connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=Asus\\SQLEXPRESS;DATABASE=pruebabanco;UID=sa;PWD=15932'
    return pyodbc.connect(connection_string)

def get_roles():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT role_name FROM Roles")
            return [row[0] for row in cursor.fetchall()]

def create_user(username, password, role_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM Roles WHERE role_name = ?", (role_name,))
            role_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO Usuarios (username, password, role_id) VALUES (?, ?, ?)", (username, password, role_id))
            conn.commit()

def create_role(role_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO Roles (role_name) VALUES (?)", (role_name,))
            conn.commit()

def get_users():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT U.id, U.username, U.password, R.role_name FROM Usuarios U JOIN Roles R ON U.role_id = R.id")
            return cursor.fetchall()

def update_user(user_id, username, password, role_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM Roles WHERE role_name = ?", (role_name,))
            role_id = cursor.fetchone()[0]
            cursor.execute("UPDATE Usuarios SET username = ?, password = ?, role_id = ? WHERE id = ?", (username, password, role_id, user_id))
            conn.commit()

def eliminar_usuario(user_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM permisos WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM Usuarios WHERE id = ?", (user_id,))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

def obtener_permisos(user_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ventana, permitido FROM permisos WHERE user_id = ?", (user_id,))
            return cursor.fetchall()

def actualizar_permisos(user_id, permisos):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM permisos WHERE user_id = ?", (user_id,))
            for ventana, permitido in permisos.items():
                cursor.execute("INSERT INTO permisos (user_id, ventana, permitido) VALUES (?, ?, ?)", (user_id, ventana, permitido))
            conn.commit()

# src/cashier_management_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget
from database import get_users, update_user, eliminar_usuario

class CashierManagementWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Cajeros")
        self.setGeometry(100, 100, 600, 400)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Password", "Role"])
        
        self.load_data()
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        
        self.edit_button = QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_user)
        self.layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_user)
        self.layout.addWidget(self.delete_button)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
    
    def load_data(self):
        users = get_users()
        self.table.setRowCount(len(users))
        for row_idx, user in enumerate(users):
            for col_idx, data in enumerate(user):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
    
    def edit_user(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            user_id = int(self.table.item(selected_row, 0).text())
            username = self.table.item(selected_row, 1).text()
            password = self.table.item(selected_row, 2).text()
            role = self.table.item(selected_row, 3).text()
            update_user(user_id, username, password, role)
            self.load_data()
    
    def delete_user(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            user_id = int(self.table.item(selected_row, 0).text())
            eliminar_usuario(user_id)
            self.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CashierManagementWindow()
    window.show()
    sys.exit(app.exec_())

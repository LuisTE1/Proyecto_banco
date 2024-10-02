import sys
import pyodbc
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QComboBox, QDateEdit)
from PyQt5.QtCore import QDate
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

def get_connection():
    connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=Asus\\SQLEXPRESS;DATABASE=pruebabanco;UID=sa;PWD=15932'
    return pyodbc.connect(connection_string)

def preprocess_data(file_path):
    df = pd.read_excel(file_path)
    
    # Verificar que las columnas necesarias existan
    required_columns = ['fecha', 'descripcion', 'monto', 'numero_op']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"El archivo Excel no contiene la columna necesaria: {col}")
    
    # Imputar valores faltantes
    imputer = SimpleImputer(strategy='most_frequent')
    df[required_columns] = imputer.fit_transform(df[required_columns])
    
    # Escalar los datos numéricos
    scaler = StandardScaler()
    df['monto'] = scaler.fit_transform(df[['monto']])
    
    return df

class TableCashierWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Table Cashier Window')
        self.setGeometry(150, 150, 800, 600)
        
        central_widget = QWidget()
        layout = QGridLayout(central_widget)
        
        self.bank_combo = QComboBox()
        self.bank_combo.addItems(["Agente", "Recaudadora", "Interbank"])
        self.bank_combo.currentIndexChanged.connect(self.show_table)
        layout.addWidget(self.bank_combo, 0, 0)
        
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget, 1, 0, 1, 3)
        
        self.upload_button = QPushButton("Subir Data")
        self.upload_button.clicked.connect(self.upload_excel)
        layout.addWidget(self.upload_button, 2, 0)
        
        self.export_button = QPushButton("Exportar a Excel")
        self.export_button.clicked.connect(self.export_to_excel)
        layout.addWidget(self.export_button, 2, 1)
        
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit, 2, 2)
        
        self.setCentralWidget(central_widget)
    
    def show_table(self):
        bank_name = self.bank_combo.currentText()
        self.table_widget.clear()
        self.table_widget.setColumnCount(17)
        self.table_widget.setHorizontalHeaderLabels(['Factura', 'RUC', 'Razón Social', 'Pago Depósito', 'N° OP', 'Pago Visa', 'N° REF', 'Pago Efectivo', 'Agente', 'Recaudadora', 'Interbank', 'Comentarios', 'Usuario', 'Fecha', 'Descripción', 'Monto', 'Número OP'])

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COALESCE(t.Factura, '') AS Factura, 
                    COALESCE(t.RUC, '') AS RUC, 
                    COALESCE(t.RazonSocial, '') AS RazonSocial, 
                    COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoDeposito), 0) AS PagoDeposito, 
                    COALESCE(t.NOP, '') AS NOP, 
                    COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoVisa), 0) AS PagoVisa, 
                    COALESCE(t.NREF, '') AS NREF, 
                    COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoEfectivo), 0) AS PagoEfectivo, 
                    COALESCE(t.AgenteChecked, 0) AS AgenteChecked, 
                    COALESCE(t.RecaudadoraChecked, 0) AS RecaudadoraChecked, 
                    COALESCE(t.InterbankChecked, 0) AS InterbankChecked, 
                    COALESCE(t.Comentarios, '') AS Comentarios, 
                    COALESCE(t.Usuario, '') AS Usuario, 
                    COALESCE(b.fecha, '') AS fecha, 
                    COALESCE(b.descripcion, '') AS descripcion, 
                    COALESCE(TRY_CONVERT(numeric(10, 2), b.monto), 0) AS monto, 
                    COALESCE(b.numero_op, '') AS numero_op
                FROM Transactions t
                FULL OUTER JOIN BancoAgente b ON t.NOP = b.numero_op
                WHERE t.Banco = ? OR b.numero_op IS NOT NULL
            ''', (bank_name,))
            rows = cursor.fetchall()

            self.table_widget.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, item in enumerate(row):
                    self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

            cursor.close()
            conn.close()
        except pyodbc.Error as db_err:
            QMessageBox.critical(self, 'Error de Base de Datos', f'Error al obtener los datos: {str(db_err)}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Ocurrió un error inesperado: {str(e)}')

    def upload_excel(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_path:
            try:
                df = preprocess_data(file_path)
                
                conn = get_connection()
                cursor = conn.cursor()
                for index, row in df.iterrows():
                    cursor.execute('''
                        INSERT INTO BancoAgente (fecha, descripcion, monto, numero_op)
                        VALUES (?, ?, ?, ?)
                    ''', row['fecha'], row['descripcion'], row['monto'], row['numero_op'])
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, 'Éxito', 'Datos del Excel subidos exitosamente!')
            except ValueError as ve:
                QMessageBox.critical(self, 'Error de Validación', str(ve))
            except pyodbc.Error as db_err:
                QMessageBox.critical(self, 'Error de Base de Datos', f'Error al subir los datos: {str(db_err)}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Ocurrió un error inesperado: {str(e)}')
    
    def export_to_excel(self):
        date = self.date_edit.date().toString("yyyy-MM-dd")
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_path:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COALESCE(t.Factura, '') AS Factura, 
                        COALESCE(t.RUC, '') AS RUC, 
                        COALESCE(t.RazonSocial, '') AS RazonSocial, 
                        COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoDeposito), 0) AS PagoDeposito, 
                        COALESCE(t.NOP, '') AS NOP, 
                        COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoVisa), 0) AS PagoVisa, 
                        COALESCE(t.NREF, '') AS NREF, 
                        COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoEfectivo), 0) AS PagoEfectivo, 
                        COALESCE(t.AgenteChecked, 0) AS AgenteChecked, 
                        COALESCE(t.RecaudadoraChecked, 0) AS RecaudadoraChecked, 
                        COALESCE(t.InterbankChecked, 0) AS InterbankChecked, 
                        COALESCE(t.Comentarios, '') AS Comentarios, 
                        COALESCE(t.Usuario, '') AS Usuario, 
                        COALESCE(b.fecha, '') AS fecha, 
                        COALESCE(b.descripcion, '') AS descripcion, 
                        COALESCE(TRY_CONVERT(numeric(10, 2), b.monto), 0) AS monto, 
                        COALESCE(b.numero_op, '') AS numero_op
                    FROM Transactions t
                    FULL OUTER JOIN BancoAgente b ON t.NOP = b.numero_op
                    WHERE b.fecha = ?
                ''', (date,))
                rows = cursor.fetchall()
                
                df = pd.DataFrame(rows, columns=[
                    'Factura', 'RUC', 'Razón Social', 'Pago Depósito', 'N° OP', 'Pago Visa', 'N° REF', 
                    'Pago Efectivo', 'Agente', 'Recaudadora', 'Interbank', 'Comentarios', 'Usuario', 
                    'Fecha', 'Descripción', 'Monto', 'Número OP'
                ])
                df.to_excel(file_path, index=False)
                
                cursor.close()
                conn.close()
                QMessageBox.information(self, 'Éxito', 'Datos exportados exitosamente!')
            except pyodbc.Error as db_err:
                QMessageBox.critical(self, 'Error de Base de Datos', f'Error al exportar los datos: {str(db_err)}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Ocurrió un error inesperado: {str(e)}')

    def test_connection():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                print("Conexión exitosa")
            else:
                print("Conexión fallida")
        except pyodbc.Error as db_err:
            print(f"Error de Base de Datos: {str(db_err)}")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {str(e)}")


def open_table_cashier_window():
    window = TableCashierWindow()
    return window
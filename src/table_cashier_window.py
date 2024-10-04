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
        layout.addWidget(self.table_widget, 1, 0, 1, 4)
        
        self.upload_button = QPushButton("Subir Data")
        self.upload_button.clicked.connect(self.upload_excel)
        layout.addWidget(self.upload_button, 2, 0)
        
        self.export_button = QPushButton("Exportar a Excel")
        self.export_button.clicked.connect(self.export_to_excel)
        layout.addWidget(self.export_button, 2, 1)
        
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))  # Default to 30 days ago
        layout.addWidget(self.start_date_edit, 2, 2)
        
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.end_date_edit, 2, 3)
        
        # Ajustar el estiramiento de las filas y columnas
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        
        self.setCentralWidget(central_widget)
        self.show_table()

    def show_table(self):
        bank_name = self.bank_combo.currentText()
        self.table_widget.clear()
        self.table_widget.setColumnCount(14)  # Asegúrate de que este número coincida con el número de columnas en tu consulta SQL
        self.table_widget.setHorizontalHeaderLabels([
            'Fecha', 'Descripción', 'Monto', 'N° OP', 'Razón Social', 'Factura', 'Número OP',
            'Pago Depósito', 'Pago Visa', 'N° REF', 'Pago Efectivo', 'Tipo de Pago', 
            'Comentarios', 'Usuario'
        ])

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COALESCE(b.fecha, '') AS fecha, 
                    COALESCE(b.descripcion, '') AS descripcion, 
                    COALESCE(TRY_CONVERT(numeric(10, 2), b.monto), 0) AS monto, 
                    COALESCE(b.numero_op, '') AS numero_op,
                    COALESCE(t.RazonSocial, '') AS RazonSocial, 
                    COALESCE(t.Factura, '') AS Factura, 
                    COALESCE(t.NOP, '') AS NOP, 
                    COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoDeposito), 0) AS PagoDeposito, 
                    COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoVisa), 0) AS PagoVisa, 
                    COALESCE(t.NREF, '') AS NREF, 
                    COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoEfectivo), 0) AS PagoEfectivo, 
                    CASE 
                        WHEN t.AgenteChecked = 1 THEN 'Agente'
                        WHEN t.RecaudadoraChecked = 1 THEN 'Recaudadora'
                        WHEN t.InterbankChecked = 1 THEN 'Interbank'
                        ELSE ''
                    END AS TipoPago,
                    COALESCE(t.Comentarios, '') AS Comentarios, 
                    COALESCE(t.Usuario, '') AS Usuario
                FROM Transactions t
                FULL OUTER JOIN BancoAgente b ON t.NOP = b.numero_op
                WHERE 
                    (t.AgenteChecked = 1 AND ? = 'Agente') OR 
                    (t.RecaudadoraChecked = 1 AND ? = 'Recaudadora') OR 
                    (t.InterbankChecked = 1 AND ? = 'Interbank')
                ORDER BY b.fecha ASC
            ''', (bank_name, bank_name, bank_name))
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
        
        # Ajustar automáticamente las columnas y filas
        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()

        
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
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_path:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COALESCE(b.fecha, '') AS fecha, 
                        COALESCE(b.descripcion, '') AS descripcion, 
                        COALESCE(TRY_CONVERT(numeric(10, 2), b.monto), 0) AS monto, 
                        COALESCE(b.numero_op, '') AS numero_op,
                        COALESCE(t.RazonSocial, '') AS RazonSocial, 
                        COALESCE(t.Factura, '') AS Factura, 
                        COALESCE(t.NOP, '') AS NOP, 
                        COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoDeposito), 0) AS PagoDeposito, 
                        COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoVisa), 0) AS PagoVisa, 
                        COALESCE(t.NREF, '') AS NREF, 
                        COALESCE(TRY_CONVERT(numeric(10, 2), t.PagoEfectivo), 0) AS PagoEfectivo, 
                        CASE 
                            WHEN t.AgenteChecked = 1 THEN 'Agente'
                            WHEN t.RecaudadoraChecked = 1 THEN 'Recaudadora'
                            WHEN t.InterbankChecked = 1 THEN 'Interbank'
                            ELSE ''
                        END AS TipoPago,
                        COALESCE(t.Comentarios, '') AS Comentarios, 
                        COALESCE(t.Usuario, '') AS Usuario
                    FROM Transactions t
                    FULL OUTER JOIN BancoAgente b
                    ON t.NOP = b.numero_op
                    WHERE b.fecha BETWEEN ? AND ?
                    ORDER BY b.fecha ASC
                ''', (start_date, end_date))
                rows = cursor.fetchall()
                
                # Definir las columnas estáticas
                columns = [
                    'Fecha', 'Descripción', 'Monto', 'N° OP', 'Razón Social', 'Factura', 'Número OP',
                    'Pago Depósito', 'Pago Visa', 'N° REF', 'Pago Efectivo', 'Tipo de Pago', 
                    'Comentarios', 'Usuario'
                ]
                
                # Asegurarse de que cada fila tenga 14 columnas
                rows = [tuple(row) + ('',) * (len(columns) - len(row)) for row in rows]

                df = pd.DataFrame(rows, columns=columns)
                df.to_excel(file_path, index=False)
                cursor.close()
                conn.close()
                QMessageBox.information(self, 'Éxito', 'Datos exportados exitosamente!')
            except pyodbc.Error as db_err:
                QMessageBox.critical(self, 'Error de Base de Datos', f'Error al exportar los datos: {str(db_err)}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Ocurrió un error inesperado: {str(e)}')


def open_table_cashier_window():
    window = TableCashierWindow()
    return window




    




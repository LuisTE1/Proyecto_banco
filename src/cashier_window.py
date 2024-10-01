from msilib import add_data
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QWidget, QTextEdit, QMessageBox
import pyodbc
import requests

def get_connection():
    connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=Asus\\SQLEXPRESS;DATABASE=pruebabanco;UID=sa;PWD=15932'
    try:
        return pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        QMessageBox.critical(None, 'Error de Conexión', f'Error al conectar con la base de datos: {str(e)}')
        return None

def is_valid_ruc(ruc):
    return len(ruc) == 11 and ruc.isdigit()

def fetch_razon_social(ruc, razon_social_input):
    if len(ruc) < 11:
        return ''
    
    if not is_valid_ruc(ruc):
        QMessageBox.warning(None, 'Error', 'El RUC ingresado no es válido.')
        return ''
    
    try:
        response = requests.get(f'https://api.apis.net.pe/v2/sunat/ruc/full?numero={ruc}', headers={'Authorization': 'Bearer apis-token-10696.RHTymkjAAV2DlrllmVypAxw1oqp1rwsK'})
        if response.status_code == 200:
            data = response.json()
            razon_social = data.get('razonSocial', '')
            razon_social_input.setText(razon_social)
            return razon_social
        else:
            QMessageBox.warning(None, 'Error', f'No se pudo obtener la razón social. Código de respuesta: {response.status_code}')
            return ''
    except Exception as e:
        QMessageBox.critical(None, 'Error', f'Error al conectar con la API: {str(e)}')
        return ''

def open_cashier_window(username):
    cashier_window = QMainWindow()
    cashier_window.setWindowTitle('Cajero')
    cashier_window.setGeometry(100, 100, 800, 600)
    
    central_widget = QWidget()
    main_layout = QGridLayout(central_widget)
    
    deposit_button = QPushButton("DEPÓSITOS")
    bancarizacion_button = QPushButton("BANCARIZACIÓN")
    main_layout.addWidget(deposit_button, 0, 0)
    main_layout.addWidget(bancarizacion_button, 0, 1)
    
    comment_box_label = QLabel("Comentarios")
    comment_box_input = QTextEdit()
    comment_box_input.setFixedHeight(50)
    main_layout.addWidget(comment_box_label, 0, 2)
    main_layout.addWidget(comment_box_input, 0, 3, 1, 4)
    
    factura_label = QLabel("Factura")
    factura_input = QLineEdit()
    main_layout.addWidget(factura_label, 1, 0)
    main_layout.addWidget(factura_input, 1, 1)
    
    ruc_label = QLabel("RUC")
    ruc_input = QLineEdit()
    main_layout.addWidget(ruc_label, 2, 0)
    main_layout.addWidget(ruc_input, 2, 1)
    
    razon_social_label = QLabel("Razón Social")
    razon_social_input = QLineEdit()
    main_layout.addWidget(razon_social_label, 3, 0)
    main_layout.addWidget(razon_social_input, 3, 1, 1, 3)
    
    ruc_input.textChanged.connect(lambda: fetch_razon_social(ruc_input.text(), razon_social_input))
    
    pago_deposito_label = QLabel("Pago en Depósito")
    pago_deposito_input = QLineEdit()
    no_op_label = QLabel("N° OP")
    no_op_input = QLineEdit()
    main_layout.addWidget(pago_deposito_label, 4, 0)
    main_layout.addWidget(pago_deposito_input, 4, 1)
    main_layout.addWidget(no_op_label, 4, 2)
    main_layout.addWidget(no_op_input, 4, 3)
    
    pago_visa_label = QLabel("Pago en Visa")
    pago_visa_input = QLineEdit()
    no_ref_label = QLabel("N° REF")
    no_ref_input = QLineEdit()
    main_layout.addWidget(pago_visa_label, 5, 0)
    main_layout.addWidget(pago_visa_input, 5, 1)
    main_layout.addWidget(no_ref_label, 5, 2)
    main_layout.addWidget(no_ref_input, 5, 3)
    pago_efectivo_label = QLabel("Pago en Efectivo")
    pago_efectivo_input = QLineEdit()
    agent_checkbox = QCheckBox("AGENTE")
    recaudadora_checkbox = QCheckBox("RECAUDADORA")
    interbank_checkbox = QCheckBox("INTERBANK")
    main_layout.addWidget(pago_efectivo_label, 6, 0)
    main_layout.addWidget(pago_efectivo_input, 6, 1)
    main_layout.addWidget(agent_checkbox, 6, 2)
    main_layout.addWidget(recaudadora_checkbox, 6, 3)
    main_layout.addWidget(interbank_checkbox, 6, 4)
    
    guardar_button = QPushButton("GUARDAR")
    guardar_button.clicked.connect(lambda: save_data(
        factura_input.text(),
        ruc_input.text(),
        razon_social_input.text(),
        pago_deposito_input.text(),
        no_op_input.text(),
        pago_visa_input.text(),
        no_ref_input.text(),
        pago_efectivo_input.text(),
        agent_checkbox.isChecked(),
        recaudadora_checkbox.isChecked(),
        interbank_checkbox.isChecked(),
        comment_box_input.toPlainText(),
        username  # Pasar el nombre de usuario
    ))
    main_layout.addWidget(guardar_button, 7, 2, 1, 2)
    
    cashier_window.setCentralWidget(central_widget)
    
    return cashier_window

def save_data(factura, ruc, razon_social,
              pago_deposito, no_op,
              pago_visa, no_ref,
              pago_efectivo,
              agente_checked,
              recaudadora_checked,
              interbank_checked,
              comentarios,
              usuario):
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Transactions (Factura, RUC, RazonSocial, PagoDeposito, NOP, PagoVisa, NREF, PagoEfectivo,
                                      AgenteChecked, RecaudadoraChecked, InterbankChecked, Comentarios, Usuario) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (factura, ruc, razon_social, pago_deposito, no_op, pago_visa, no_ref, pago_efectivo,
              agente_checked, recaudadora_checked, interbank_checked, comentarios, usuario))

        conn.commit()
        cursor.close()
        conn.close()

        QMessageBox.information(None, 'Éxito', 'Datos guardados exitosamente!')

    except pyodbc.Error as db_err:
        QMessageBox.critical(None, 'Error de Base de Datos', f'Error al guardar los datos: {str(db_err)}')
    except Exception as e:
        QMessageBox.critical(None, 'Error', f'Ocurrió un error inesperado: {str(e)}')

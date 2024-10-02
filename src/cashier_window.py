from msilib import add_data
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QWidget, QTextEdit, QMessageBox
import pyodbc
import requests
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

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

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

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
        factura_input, ruc_input, razon_social_input,
        pago_deposito_input, no_op_input,
        pago_visa_input, no_ref_input,
        pago_efectivo_input,
        agent_checkbox, recaudadora_checkbox, interbank_checkbox,
        comment_box_input, username
    ))
    main_layout.addWidget(guardar_button, 7, 2, 1, 2)
    
    # Add button to show table
    show_table_button = QPushButton("Mostrar Tabla")
    show_table_button.clicked.connect(lambda: show_table(cashier_window, factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, pago_efectivo_input, agent_checkbox, recaudadora_checkbox, interbank_checkbox, comment_box_input))
    main_layout.addWidget(show_table_button, 7, 0, 1, 2)
    
    # Add button to update
    update_button = QPushButton("ACTUALIZAR")
    update_button.clicked.connect(lambda: update_data(
        factura_input, ruc_input, razon_social_input,
        pago_deposito_input, no_op_input,
        pago_visa_input, no_ref_input,
        pago_efectivo_input,
        agent_checkbox, recaudadora_checkbox, interbank_checkbox,
        comment_box_input, username
    ))
    main_layout.addWidget(update_button, 8, 2, 1, 2)
    
    cashier_window.setCentralWidget(central_widget)
    
    return cashier_window

def show_table(parent, factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, pago_efectivo_input, agent_checkbox, recaudadora_checkbox, interbank_checkbox, comment_box_input):
    table_window = QMainWindow(parent)
    table_window.setWindowTitle('Seleccionar Transacción')
    table_window.setGeometry(150, 150, 600, 400)
    
    table_widget = QTableWidget()
    table_widget.setColumnCount(13)
    table_widget.setHorizontalHeaderLabels(['Factura', 'RUC', 'Razón Social', 'Pago Depósito', 'N° OP', 'Pago Visa', 'N° REF', 'Pago Efectivo', 'Agente', 'Recaudadora', 'Interbank', 'Comentarios', 'Usuario'])
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT Factura, RUC, RazonSocial, PagoDeposito, NOP, PagoVisa, NREF, PagoEfectivo, AgenteChecked, RecaudadoraChecked, InterbankChecked, Comentarios, Usuario FROM Transactions')
        rows = cursor.fetchall()
        
        table_widget.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, item in enumerate(row):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
        
        cursor.close()
        conn.close()
    except pyodbc.Error as db_err:
        QMessageBox.critical(None, 'Error de Base de Datos', f'Error al obtener los datos: {str(db_err)}')
    except Exception as e:
        QMessageBox.critical(None, 'Error', f'Ocurrió un error inesperado: {str(e)}')
    
    table_widget.itemSelectionChanged.connect(lambda: populate_fields_from_selection(table_widget, factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, pago_efectivo_input, agent_checkbox, recaudadora_checkbox, interbank_checkbox, comment_box_input))
    
    table_window.setCentralWidget(table_widget)
    table_window.show()

def populate_fields_from_selection(table_widget, factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, pago_efectivo_input, agent_checkbox, recaudadora_checkbox, interbank_checkbox, comment_box_input):
    selected_row = table_widget.currentRow()
    factura_input.setText(table_widget.item(selected_row, 0).text())
    ruc_input.setText(table_widget.item(selected_row, 1).text())
    razon_social_input.setText(table_widget.item(selected_row, 2).text())
    pago_deposito_input.setText(table_widget.item(selected_row, 3).text())
    no_op_input.setText(table_widget.item(selected_row, 4).text())
    pago_visa_input.setText(table_widget.item(selected_row, 5).text())
    no_ref_input.setText(table_widget.item(selected_row, 6).text())
    pago_efectivo_input.setText(table_widget.item(selected_row, 7).text())
    agent_checkbox.setChecked(table_widget.item(selected_row, 8).text() == 'True')
    recaudadora_checkbox.setChecked(table_widget.item(selected_row, 9).text() == 'True')
    interbank_checkbox.setChecked(table_widget.item(selected_row, 10).text() == 'True')
    comment_box_input.setPlainText(table_widget.item(selected_row, 11).text())

    factura_input.setDisabled(True)
    ruc_input.setDisabled(True)
    razon_social_input.setDisabled(True)

def save_data(factura_input, ruc_input, razon_social_input,
              pago_deposito_input, no_op_input,
              pago_visa_input, no_ref_input,
              pago_efectivo_input,
              agent_checkbox, recaudadora_checkbox, interbank_checkbox,
              comment_box_input, usuario):
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Transactions (Factura, RUC, RazonSocial, PagoDeposito, NOP, PagoVisa, NREF, PagoEfectivo,
                                      AgenteChecked, RecaudadoraChecked, InterbankChecked, Comentarios, Usuario) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (factura_input.text(), ruc_input.text(), razon_social_input.text(), pago_deposito_input.text(), no_op_input.text(), 
              pago_visa_input.text(), no_ref_input.text(), pago_efectivo_input.text(), agent_checkbox.isChecked(), 
              recaudadora_checkbox.isChecked(), interbank_checkbox.isChecked(), comment_box_input.toPlainText(), usuario))

        conn.commit()
        cursor.close()
        conn.close()

        QMessageBox.information(None, 'Éxito', 'Datos guardados exitosamente!')
        clear_fields(factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, 
                     pago_efectivo_input, agent_checkbox, recaudadora_checkbox, interbank_checkbox, comment_box_input)

    except pyodbc.Error as db_err:
        QMessageBox.critical(None, 'Error de Base de Datos', f'Error al guardar los datos: {str(db_err)}')
    except Exception as e:
        QMessageBox.critical(None, 'Error', f'Ocurrió un error inesperado: {str(e)}')

def update_data(factura_input, ruc_input, razon_social_input,
                pago_deposito_input, no_op_input,
                pago_visa_input, no_ref_input,
                pago_efectivo_input,
                agent_checkbox, recaudadora_checkbox, interbank_checkbox,
                comment_box_input, usuario):
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE Transactions
            SET PagoDeposito = ?, NOP = ?, PagoVisa = ?, NREF = ?, PagoEfectivo = ?, AgenteChecked = ?, RecaudadoraChecked = ?, InterbankChecked = ?, Comentarios = ?, Usuario = ?
            WHERE Factura = ? AND RUC = ? AND RazonSocial = ?
        ''', (pago_deposito_input.text(), no_op_input.text(), pago_visa_input.text(), no_ref_input.text(), pago_efectivo_input.text(), 
              agent_checkbox.isChecked(), recaudadora_checkbox.isChecked(), interbank_checkbox.isChecked(), comment_box_input.toPlainText(), 
              usuario, factura_input.text(), ruc_input.text(), razon_social_input.text()))

        conn.commit()
        cursor.close()
        conn.close()

        QMessageBox.information(None, 'Éxito', 'Datos actualizados exitosamente!')
        clear_fields(factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, 
                     pago_efectivo_input, agent_checkbox, recaudadora_checkbox, interbank_checkbox, comment_box_input)

    except pyodbc.Error as db_err:
        QMessageBox.critical(None, 'Error de Base de Datos', f'Error al actualizar los datos: {str(db_err)}')
    except Exception as e:
        QMessageBox.critical(None, 'Error', f'Ocurrió un error inesperado: {str(e)}')

def clear_fields(factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, 
                 pago_efectivo_input, agent_checkbox, recaudadora_checkbox, interbank_checkbox, comment_box_input):
    factura_input.clear()
    ruc_input.clear()
    razon_social_input.clear()
    pago_deposito_input.clear()
    no_op_input.clear()
    pago_visa_input.clear()
    no_ref_input.clear()
    pago_efectivo_input.clear()
    agent_checkbox.setChecked(False)
    recaudadora_checkbox.setChecked(False)
    interbank_checkbox.setChecked(False)
    comment_box_input.clear()

    factura_input.setEnabled(True)
    ruc_input.setEnabled(True)
    razon_social_input.setEnabled(True)

def populate_fields_from_selection(table_widget, factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, 
                                   pago_visa_input, no_ref_input, pago_efectivo_input, agent_checkbox, recaudadora_checkbox, 
                                   interbank_checkbox, comment_box_input):
    selected_row = table_widget.currentRow()
    factura_input.setText(table_widget.item(selected_row, 0).text())
    ruc_input.setText(table_widget.item(selected_row, 1).text())
    razon_social_input.setText(table_widget.item(selected_row, 2).text())
    pago_deposito_input.setText(table_widget.item(selected_row, 3).text())
    no_op_input.setText(table_widget.item(selected_row, 4).text())
    pago_visa_input.setText(table_widget.item(selected_row, 5).text())
    no_ref_input.setText(table_widget.item(selected_row, 6).text())
    pago_efectivo_input.setText(table_widget.item(selected_row, 7).text())
    agent_checkbox.setChecked(table_widget.item(selected_row, 8).text() == 'True')
    recaudadora_checkbox.setChecked(table_widget.item(selected_row, 9).text() == 'True')
    interbank_checkbox.setChecked(table_widget.item(selected_row, 10).text() == 'True')
    comment_box_input.setPlainText(table_widget.item(selected_row, 11).text())

    factura_input.setDisabled(True)
    ruc_input.setDisabled(True)
    razon_social_input.setDisabled(True)

def show_table(parent, factura_input, ruc_input, razon_social_input, pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, 
               pago_efectivo_input, agent_checkbox, recaudadora_checkbox, interbank_checkbox, comment_box_input):
    table_window = QMainWindow(parent)
    table_window.setWindowTitle('Seleccionar Transacción')
    table_window.setGeometry(150, 150, 600, 400)
    
    table_widget = QTableWidget()
    table_widget.setColumnCount(13)
    table_widget.setHorizontalHeaderLabels(['Factura', 'RUC', 'Razón Social', 'Pago Depósito', 'N° OP', 'Pago Visa', 'N° REF', 
                                            'Pago Efectivo', 'Agente', 'Recaudadora', 'Interbank', 'Comentarios', 'Usuario'])
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT Factura, RUC, RazonSocial, PagoDeposito, NOP, PagoVisa, NREF, PagoEfectivo, AgenteChecked, RecaudadoraChecked, InterbankChecked, Comentarios, Usuario FROM Transactions')
        rows = cursor.fetchall()
        
        table_widget.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, item in enumerate(row):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
        
        cursor.close()
        conn.close()
    except pyodbc.Error as db_err:
        QMessageBox.critical(None, 'Error de Base de Datos', f'Error al obtener los datos: {str(db_err)}')
    except Exception as e:
        QMessageBox.critical(None, 'Error', f'Ocurrió un error inesperado: {str(e)}')
    
    table_widget.itemSelectionChanged.connect(lambda: populate_fields_from_selection(table_widget, factura_input, ruc_input, razon_social_input, 
                                                                                     pago_deposito_input, no_op_input, pago_visa_input, no_ref_input, 
                                                                                     pago_efectivo_input, agent_checkbox, recaudadora_checkbox, 
                                                                                     interbank_checkbox, comment_box_input))
    
    table_window.setCentralWidget(table_widget)
    table_window.show()

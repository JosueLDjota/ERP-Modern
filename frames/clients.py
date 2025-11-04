"""
frames/clients.py - Módulo de Gestión de Clientes Moderno
PySide6 con estilo Windows 11 profesional
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QTextEdit, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QGroupBox, QFormLayout, QMessageBox,
    QSplitter, QToolBar, QStatusBar, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QAction
import csv
import re
from datetime import datetime

class AnimatedButton(QPushButton):
    """Botón con animaciones suaves al estilo Windows 11"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)
        
    def set_primary_style(self):
        self.setStyleSheet("""
            AnimatedButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, stop:1 #60A5FA);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                font-size: 13px;
                padding: 8px 16px;
            }
            AnimatedButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563EB, stop:1 #3B82F6);
            }
            AnimatedButton:pressed {
                background: #1D4ED8;
            }
        """)
    
    def set_secondary_style(self):
        self.setStyleSheet("""
            AnimatedButton {
                background: transparent;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                color: #475569;
                font-weight: 500;
                font-size: 13px;
                padding: 8px 16px;
            }
            AnimatedButton:hover {
                background: #F1F5F9;
                border-color: #CBD5E1;
            }
        """)
    
    def set_danger_style(self):
        self.setStyleSheet("""
            AnimatedButton {
                background: transparent;
                border: 1.5px solid #FECACA;
                border-radius: 8px;
                color: #DC2626;
                font-weight: 500;
                font-size: 13px;
                padding: 8px 16px;
            }
            AnimatedButton:hover {
                background: #FEF2F2;
                border-color: #FCA5A5;
            }
        """)

class ModernTableWidget(QTableWidget):
    """Tabla moderna con estilo Windows 11"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
                outline: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
            }
            QTableWidget::item:selected {
                background: #DBEAFE;
                color: #1E293B;
            }
            QHeaderView::section {
                background: #F8FAFC;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                font-weight: 600;
                color: #374151;
            }
            QTableCornerButton::section {
                background: #F8FAFC;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                border-right: 1px solid #E2E8F0;
            }
        """)
        
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Configurar header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)

class ClientsFrame(QWidget):
    """Frame moderno para gestión completa de clientes con estilo Windows 11"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.db = parent.db if parent else None
        self.current_client_id = None
        
        self.setup_ui()
        self.load_clients()
        
        # Conectar señales
        self.search_input.textChanged.connect(self.search_clients)
        self.filter_combo.currentTextChanged.connect(self.load_clients)

    def setup_ui(self):
        """Configura la interfaz de usuario moderna"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Header section
        header_layout = self.create_header_section()
        main_layout.addLayout(header_layout)

        # Splitter para contenido principal
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Panel izquierdo - Formulario
        form_panel = self.create_form_panel()
        splitter.addWidget(form_panel)
        
        # Panel derecho - Lista y controles
        list_panel = self.create_list_panel()
        splitter.addWidget(list_panel)
        
        # Configurar proporciones del splitter
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter, 1)

    def create_header_section(self):
        """Crea la sección de header"""
        layout = QHBoxLayout()
        
        # Título y descripción
        title_section = QVBoxLayout()
        title_section.setSpacing(4)
        
        title = QLabel("👥 Gestión de Clientes")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1E293B;")
        
        subtitle = QLabel("Administre la base de datos de clientes de forma eficiente")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #64748B;")
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        layout.addLayout(title_section)
        layout.addStretch()
        
        # Botones de acción rápida
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        self.export_btn = AnimatedButton("📤 Exportar CSV")
        self.export_btn.set_secondary_style()
        self.export_btn.clicked.connect(self.export_to_csv)
        
        self.stats_btn = AnimatedButton("📊 Estadísticas")
        self.stats_btn.set_secondary_style()
        self.stats_btn.clicked.connect(self.show_statistics)
        
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.stats_btn)
        
        layout.addLayout(action_layout)
        
        return layout

    def create_form_panel(self):
        """Crea el panel del formulario"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Título del formulario
        form_title = QLabel("📝 Información del Cliente")
        form_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        form_title.setStyleSheet("color: #1E293B; margin-bottom: 8px;")
        layout.addWidget(form_title)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Campos del formulario
        self.nombre_input = self.create_styled_input("Nombre *")
        self.apellido_input = self.create_styled_input("Apellido *")
        self.dni_input = self.create_styled_input("DNI/Identidad")
        self.telefono_input = self.create_styled_input("Teléfono")
        self.email_input = self.create_styled_input("Email")
        
        # Dirección (QTextEdit)
        direccion_label = QLabel("Dirección:")
        direccion_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        direccion_label.setStyleSheet("color: #374151;")
        
        self.direccion_input = QTextEdit()
        self.direccion_input.setMaximumHeight(80)
        self.direccion_input.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
            }
            QTextEdit:focus {
                border-color: #3B82F6;
                background: #F8FAFF;
            }
        """)
        
        # Checkbox activo
        self.activo_check = QCheckBox("Cliente Activo")
        self.activo_check.setChecked(True)
        self.activo_check.setStyleSheet("""
            QCheckBox {
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #374151;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #CBD5E1;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #3B82F6;
                border-color: #3B82F6;
            }
        """)
        
        # Añadir campos al formulario
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Apellido:", self.apellido_input)
        form_layout.addRow("DNI:", self.dni_input)
        form_layout.addRow("Teléfono:", self.telefono_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow(direccion_label, self.direccion_input)
        form_layout.addRow("", self.activo_check)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.save_btn = AnimatedButton("💾 Guardar Cliente")
        self.save_btn.set_primary_style()
        self.save_btn.clicked.connect(self.save_client)
        
        self.edit_btn = AnimatedButton("✏️ Editar")
        self.edit_btn.set_secondary_style()
        self.edit_btn.clicked.connect(self.edit_client)
        
        self.delete_btn = AnimatedButton("🗑️ Eliminar")
        self.delete_btn.set_danger_style()
        self.delete_btn.clicked.connect(self.delete_client)
        
        self.clear_btn = AnimatedButton("🔄 Limpiar")
        self.clear_btn.set_secondary_style()
        self.clear_btn.clicked.connect(self.clear_form)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.clear_btn)
        
        layout.addLayout(buttons_layout)
        
        return panel

    def create_list_panel(self):
        """Crea el panel de lista y controles"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        
        # Panel de búsqueda y filtros
        search_panel = self.create_search_panel()
        layout.addWidget(search_panel)
        
        # Tabla de clientes
        table_panel = self.create_table_panel()
        layout.addWidget(table_panel, 1)
        
        return panel

    def create_search_panel(self):
        """Crea el panel de búsqueda"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Búsqueda
        search_label = QLabel("🔍 Buscar:")
        search_label.setFont(QFont("Segoe UI", 11))
        search_label.setStyleSheet("color: #374151;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre, apellido, DNI, teléfono...")
        self.search_input.setMinimumHeight(36)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
                background: #F8FAFF;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        
        # Filtro
        filter_label = QLabel("Filtrar:")
        filter_label.setFont(QFont("Segoe UI", 11))
        filter_label.setStyleSheet("color: #374151;")
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos los clientes", "Solo activos", "Solo inactivos"])
        self.filter_combo.setMinimumHeight(36)
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
                min-width: 140px;
            }
            QComboBox:focus {
                border-color: #3B82F6;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64748B;
                width: 0px;
                height: 0px;
            }
        """)
        
        layout.addWidget(search_label)
        layout.addWidget(self.search_input, 1)
        layout.addSpacing(12)
        layout.addWidget(filter_label)
        layout.addWidget(self.filter_combo)
        
        return panel

    def create_table_panel(self):
        """Crea el panel de la tabla"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Título de la tabla
        table_title = QLabel("📋 Lista de Clientes")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        table_title.setStyleSheet("color: #1E293B;")
        layout.addWidget(table_title)
        
        # Tabla
        self.clients_table = ModernTableWidget()
        self.setup_table()
        layout.addWidget(self.clients_table, 1)
        
        # Conectar doble click para editar
        self.clients_table.doubleClicked.connect(self.on_double_click)
        
        return panel

    def setup_table(self):
        """Configura la tabla de clientes"""
        headers = ["ID", "Nombre", "Apellido", "DNI", "Teléfono", "Email", "Estado"]
        self.clients_table.setColumnCount(len(headers))
        self.clients_table.setHorizontalHeaderLabels(headers)
        
        # Configurar anchos de columnas
        self.clients_table.setColumnWidth(0, 60)   # ID
        self.clients_table.setColumnWidth(1, 120)  # Nombre
        self.clients_table.setColumnWidth(2, 120)  # Apellido
        self.clients_table.setColumnWidth(3, 100)  # DNI
        self.clients_table.setColumnWidth(4, 110)  # Teléfono
        self.clients_table.setColumnWidth(5, 150)  # Email
        self.clients_table.setColumnWidth(6, 80)   # Estado

    def create_styled_input(self, placeholder):
        """Crea un QLineEdit con estilo moderno"""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setMinimumHeight(38)
        input_field.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
                background: #F8FAFF;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        return input_field

    def load_clients(self):
        """Carga la lista de clientes desde la base de datos"""
        if not self.db:
            return
            
        try:
            # Determinar filtro
            filter_text = self.filter_combo.currentText()
            if filter_text == "Solo activos":
                query = "SELECT * FROM Clientes WHERE activo = 1 ORDER BY apellido, nombre"
            elif filter_text == "Solo inactivos":
                query = "SELECT * FROM Clientes WHERE activo = 0 ORDER BY apellido, nombre"
            else:
                query = "SELECT * FROM Clientes ORDER BY apellido, nombre"
            
            clientes = self.db.fetch(query)
            self.populate_table(clientes)
            
        except Exception as e:
            print(f"Error cargando clientes: {e}")

    def populate_table(self, clientes):
        """Llena la tabla con los datos de clientes"""
        self.clients_table.setRowCount(0)
        
        for cliente in clientes:
            (id_cliente, nombre, apellido, dni, telefono, email, direccion, 
             fecha_registro, activo) = cliente
            
            row = self.clients_table.rowCount()
            self.clients_table.insertRow(row)
            
            estado = "Activo" if activo else "Inactivo"
            
            # Crear items
            items = [
                QTableWidgetItem(str(id_cliente)),
                QTableWidgetItem(nombre),
                QTableWidgetItem(apellido),
                QTableWidgetItem(dni or "N/A"),
                QTableWidgetItem(telefono or "N/A"),
                QTableWidgetItem(email or "N/A"),
                QTableWidgetItem(estado)
            ]
            
            # Aplicar estilo según estado
            if not activo:
                for item in items:
                    item.setForeground(QColor("#94A3B8"))  # Color gris para inactivos
            
            # Añadir items a la tabla
            for col, item in enumerate(items):
                self.clients_table.setItem(row, col, item)

    def search_clients(self):
        """Busca clientes en tiempo real"""
        search_term = self.search_input.text().strip().lower()
        
        if not search_term:
            self.load_clients()
            return
            
        try:
            query = """
                SELECT * FROM Clientes 
                WHERE LOWER(nombre) LIKE ? 
                OR LOWER(apellido) LIKE ? 
                OR LOWER(dni) LIKE ? 
                OR LOWER(telefono) LIKE ? 
                OR LOWER(email) LIKE ?
                ORDER BY apellido, nombre
            """
            search_pattern = f"%{search_term}%"
            clientes = self.db.fetch(
                query,
                (search_pattern, search_pattern, search_pattern, 
                 search_pattern, search_pattern)
            )
            
            self.populate_table(clientes)
            
        except Exception as e:
            print(f"Error buscando clientes: {e}")

    def on_double_click(self, index):
        """Maneja el doble click en la tabla"""
        row = index.row()
        client_id = int(self.clients_table.item(row, 0).text())
        self.load_client_details(client_id)

    def load_client_details(self, client_id):
        """Carga los detalles de un cliente en el formulario"""
        try:
            cliente = self.db.fetch("SELECT * FROM Clientes WHERE id = ?", (client_id,))
            if cliente:
                cliente_data = cliente[0]
                (id_cliente, nombre, apellido, dni, telefono, email, 
                 direccion, fecha_registro, activo) = cliente_data
                
                # Llenar formulario
                self.nombre_input.setText(nombre)
                self.apellido_input.setText(apellido)
                self.dni_input.setText(dni or "")
                self.telefono_input.setText(telefono or "")
                self.email_input.setText(email or "")
                self.direccion_input.setPlainText(direccion or "")
                self.activo_check.setChecked(bool(activo))
                
                self.current_client_id = client_id
                
        except Exception as e:
            print(f"Error cargando detalles del cliente: {e}")

    def validate_form(self):
        """Valida los datos del formulario"""
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        email = self.email_input.text().strip()
        dni = self.dni_input.text().strip()
        
        if not nombre:
            self.show_error("Error de Validación", "El nombre es obligatorio")
            self.nombre_input.setFocus()
            return False
            
        if not apellido:
            self.show_error("Error de Validación", "El apellido es obligatorio")
            self.apellido_input.setFocus()
            return False
            
        # Validar email si se proporciona
        if email and not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            self.show_error("Error de Validación", "Formato de email inválido")
            self.email_input.setFocus()
            return False
            
        # Validar DNI si se proporciona
        if dni and not re.match(r"^[0-9]{13}$", dni):
            self.show_error("Error de Validación", "El DNI debe tener 13 dígitos")
            self.dni_input.setFocus()
            return False
            
        return True

    def save_client(self):
        """Guarda un nuevo cliente o actualiza uno existente"""
        if not self.validate_form():
            return
            
        try:
            nombre = self.nombre_input.text().strip()
            apellido = self.apellido_input.text().strip()
            dni = self.dni_input.text().strip() or None
            telefono = self.telefono_input.text().strip() or None
            email = self.email_input.text().strip() or None
            direccion = self.direccion_input.toPlainText().strip() or None
            activo = 1 if self.activo_check.isChecked() else 0
            
            if self.current_client_id:
                # Actualizar cliente existente
                query = """
                    UPDATE Clientes 
                    SET nombre=?, apellido=?, dni=?, telefono=?, email=?, direccion=?, activo=?
                    WHERE id=?
                """
                self.db.execute(
                    query,
                    (nombre, apellido, dni, telefono, email, direccion, activo, self.current_client_id)
                )
                self.show_success("Cliente Actualizado", "Cliente actualizado correctamente")
            else:
                # Crear nuevo cliente
                fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                query = """
                    INSERT INTO Clientes (nombre, apellido, dni, telefono, email, direccion, fecha_registro, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.db.execute(
                    query,
                    (nombre, apellido, dni, telefono, email, direccion, fecha_registro, activo)
                )
                self.show_success("Cliente Registrado", "Cliente registrado correctamente")
            
            self.clear_form()
            self.load_clients()
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                self.show_error("Error", "El DNI ya está registrado para otro cliente")
            else:
                self.show_error("Error", f"Error al guardar cliente: {e}")

    def edit_client(self):
        """Prepara la edición del cliente seleccionado"""
        if not self.current_client_id:
            self.show_warning("Advertencia", "Seleccione un cliente para editar")
            return
            
        self.show_info("Modo Edición", 
                      "Modifique los campos y presione 'Guardar' para confirmar los cambios")

    def delete_client(self):
        """Elimina el cliente seleccionado"""
        if not self.current_client_id:
            self.show_warning("Advertencia", "Seleccione un cliente para eliminar")
            return
            
        try:
            # Verificar si el cliente tiene ventas asociadas
            ventas = self.db.fetch(
                "SELECT COUNT(*) FROM Ventas WHERE id_cliente = ?",
                (self.current_client_id,)
            )
            tiene_ventas = ventas[0][0] > 0 if ventas else False
            
            if tiene_ventas:
                reply = self.show_question(
                    "Cliente con Ventas",
                    "Este cliente tiene ventas registradas.\n¿Desea desactivarlo en lugar de eliminarlo?\n\n"
                    "Sí = Desactivar (recomendado)\nNo = Eliminar permanentemente"
                )
                
                if reply == QMessageBox.Yes:
                    # Desactivar cliente
                    self.db.execute(
                        "UPDATE Clientes SET activo = 0 WHERE id = ?",
                        (self.current_client_id,)
                    )
                    self.show_success("Cliente Desactivado", "Cliente desactivado correctamente")
                else:
                    # Confirmar eliminación definitiva
                    reply2 = self.show_question(
                        "Confirmación",
                        "⚠️ ADVERTENCIA: Se eliminarán también todas las ventas asociadas.\n¿Continuar?"
                    )
                    
                    if reply2 == QMessageBox.Yes:
                        self.db.execute(
                            "DELETE FROM DetalleVenta WHERE venta_id IN (SELECT id FROM Ventas WHERE id_cliente = ?)",
                            (self.current_client_id,)
                        )
                        self.db.execute(
                            "DELETE FROM Ventas WHERE id_cliente = ?",
                            (self.current_client_id,)
                        )
                        self.db.execute(
                            "DELETE FROM Clientes WHERE id = ?",
                            (self.current_client_id,)
                        )
                        self.show_success("Cliente Eliminado", "Cliente y ventas asociadas eliminados")
            else:
                # Cliente sin ventas
                reply = self.show_question(
                    "Confirmación",
                    "¿Está seguro de eliminar este cliente?"
                )
                
                if reply == QMessageBox.Yes:
                    self.db.execute(
                        "DELETE FROM Clientes WHERE id = ?",
                        (self.current_client_id,)
                    )
                    self.show_success("Cliente Eliminado", "Cliente eliminado correctamente")
            
            self.clear_form()
            self.load_clients()
            
        except Exception as e:
            self.show_error("Error", f"Error al eliminar cliente: {e}")

    def clear_form(self):
        """Limpia el formulario"""
        self.nombre_input.clear()
        self.apellido_input.clear()
        self.dni_input.clear()
        self.telefono_input.clear()
        self.email_input.clear()
        self.direccion_input.clear()
        self.activo_check.setChecked(True)
        self.current_client_id = None
        
        # Limpiar selección en la tabla
        self.clients_table.clearSelection()

    def export_to_csv(self):
        """Exporta la lista de clientes a CSV"""
        # Implementación simplificada - en producción usar filedialog
        try:
            clientes = self.db.fetch(
                "SELECT * FROM Clientes ORDER BY apellido, nombre"
            )
            
            # Aquí iría la lógica para guardar el archivo
            self.show_info("Exportar CSV", 
                          f"Preparado para exportar {len(clientes)} clientes a CSV")
            
        except Exception as e:
            self.show_error("Error", f"Error al exportar: {e}")

    def show_statistics(self):
        """Muestra estadísticas de clientes"""
        try:
            total_clientes = self.db.fetch("SELECT COUNT(*) FROM Clientes")[0][0]
            clientes_activos = self.db.fetch(
                "SELECT COUNT(*) FROM Clientes WHERE activo = 1"
            )[0][0]
            clientes_inactivos = total_clientes - clientes_activos

            clientes_con_ventas = self.db.fetch(
                "SELECT COUNT(DISTINCT id_cliente) FROM Ventas WHERE id_cliente IS NOT NULL"
            )[0][0]

            fecha_inicio_mes = datetime.now().strftime("%Y-%m-01")
            clientes_este_mes = self.db.fetch(
                "SELECT COUNT(*) FROM Clientes WHERE fecha_registro >= ?",
                (fecha_inicio_mes,)
            )[0][0]

            stats_text = f"""
📊 ESTADÍSTICAS DE CLIENTES

👥 Total de clientes: {total_clientes}
✅ Clientes activos: {clientes_activos}
❌ Clientes inactivos: {clientes_inactivos}
🛒 Clientes con ventas: {clientes_con_ventas}
📅 Registrados este mes: {clientes_este_mes}

💼 Porcentaje de actividad: {(clientes_activos/total_clientes*100):.1f}% (activos)
🛍️ Porcentaje con compras: {(clientes_con_ventas/total_clientes*100):.1f}% (compradores)
            """.strip()

            self.show_info("Estadísticas de Clientes", stats_text)

        except Exception as e:
            self.show_error("Error", f"Error al calcular estadísticas: {e}")

    # Métodos auxiliares para mostrar mensajes
    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)
    
    def show_info(self, title, message):
        QMessageBox.information(self, title, message)
    
    def show_success(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    def show_question(self, title, message):
        reply = QMessageBox.question(self, title, message, 
                                   QMessageBox.Yes | QMessageBox.No)
        return reply
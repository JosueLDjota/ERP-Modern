"""
frames/suppliers.py
Gestión completa de proveedores - Windows 11 Style
CRUD avanzado, categorías, evaluaciones y métricas
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QTabWidget,
    QFormLayout, QMessageBox, QFileDialog, QScrollArea, QSplitter,
    QProgressBar, QListWidget, QListWidgetItem, QInputDialog,
    QHeaderView, QDateEdit, QSlider
)
from PySide6.QtCore import Qt, QTimer, QDate, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QLinearGradient, QPainter
import csv
import json
from datetime import datetime, timedelta

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

class SupplierFrame(QWidget):
    """Frame moderno para gestión completa de proveedores"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.db = parent.db if parent and hasattr(parent, 'db') else None
        self.current_supplier_id = None
        self.supplier_categories = []
        
        self.setup_ui()
        self.load_suppliers()
        self.load_categories()

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
        
        # Panel izquierdo - Lista de proveedores
        list_panel = self.create_list_panel()
        splitter.addWidget(list_panel)
        
        # Panel derecho - Formulario y detalles
        form_panel = self.create_form_panel()
        splitter.addWidget(form_panel)
        
        # Configurar proporciones del splitter
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([600, 400])
        
        main_layout.addWidget(splitter, 1)

    def create_header_section(self):
        """Crea la sección de header"""
        layout = QHBoxLayout()
        
        # Título y descripción
        title_section = QVBoxLayout()
        title_section.setSpacing(4)
        
        title = QLabel("🏢 Gestión de Proveedores")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1E293B;")
        
        subtitle = QLabel("Administre la base de proveedores y evalúe su desempeño")
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
        self.export_btn.clicked.connect(self.export_suppliers)
        
        self.stats_btn = AnimatedButton("📊 Estadísticas")
        self.stats_btn.set_secondary_style()
        self.stats_btn.clicked.connect(self.show_statistics)
        
        self.categories_btn = AnimatedButton("🏷️ Gestionar Categorías")
        self.categories_btn.set_secondary_style()
        self.categories_btn.clicked.connect(self.manage_categories)
        
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.stats_btn)
        action_layout.addWidget(self.categories_btn)
        
        layout.addLayout(action_layout)
        
        return layout

    def create_list_panel(self):
        """Crea el panel de lista de proveedores"""
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
        
        # Panel de búsqueda y filtros
        search_panel = self.create_search_panel()
        layout.addWidget(search_panel)
        
        # Título de la tabla
        table_title = QLabel("📋 Directorio de Proveedores")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        table_title.setStyleSheet("color: #1E293B;")
        layout.addWidget(table_title)
        
        # Tabla de proveedores
        self.suppliers_table = ModernTableWidget()
        self.setup_suppliers_table()
        layout.addWidget(self.suppliers_table, 1)
        
        # Conectar señales
        self.suppliers_table.doubleClicked.connect(self.on_supplier_double_click)
        self.search_input.textChanged.connect(self.filter_suppliers)
        self.category_filter.currentTextChanged.connect(self.filter_suppliers)
        self.status_filter.currentTextChanged.connect(self.filter_suppliers)
        
        return panel

    def create_search_panel(self):
        """Crea el panel de búsqueda y filtros"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Búsqueda
        search_layout = QHBoxLayout()
        
        search_label = QLabel("🔍 Buscar:")
        search_label.setFont(QFont("Segoe UI", 11))
        search_label.setStyleSheet("color: #374151;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre, contacto, email...")
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
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        
        # Filtros
        filters_layout = QHBoxLayout()
        
        category_label = QLabel("Categoría:")
        category_label.setFont(QFont("Segoe UI", 11))
        category_label.setStyleSheet("color: #374151;")
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("Todas las categorías")
        self.category_filter.setMinimumHeight(36)
        self.category_filter.setStyleSheet(self.get_combo_style())
        
        status_label = QLabel("Estado:")
        status_label.setFont(QFont("Segoe UI", 11))
        status_label.setStyleSheet("color: #374151;")
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Activos", "Inactivos", "Suspendidos"])
        self.status_filter.setMinimumHeight(36)
        self.status_filter.setStyleSheet(self.get_combo_style())
        
        filters_layout.addWidget(category_label)
        filters_layout.addWidget(self.category_filter)
        filters_layout.addWidget(status_label)
        filters_layout.addWidget(self.status_filter)
        filters_layout.addStretch()
        
        layout.addLayout(search_layout)
        layout.addLayout(filters_layout)
        
        return panel

    def create_form_panel(self):
        """Crea el panel del formulario y detalles"""
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
        
        # Tabs para formulario y detalles
        self.form_tabs = QTabWidget()
        self.form_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: transparent;
                border: none;
                padding: 8px 16px;
                font-weight: 500;
                color: #64748B;
            }
            QTabBar::tab:selected {
                color: #3B82F6;
                border-bottom: 2px solid #3B82F6;
            }
        """)
        
        # Tab de información básica
        basic_tab = self.create_basic_info_tab()
        self.form_tabs.addTab(basic_tab, "📝 Información Básica")
        
        # Tab de detalles adicionales
        details_tab = self.create_additional_details_tab()
        self.form_tabs.addTab(details_tab, "📊 Detalles Adicionales")
        
        # Tab de evaluación
        evaluation_tab = self.create_evaluation_tab()
        self.form_tabs.addTab(evaluation_tab, "⭐ Evaluación")
        
        layout.addWidget(self.form_tabs)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.save_btn = AnimatedButton("💾 Guardar Proveedor")
        self.save_btn.set_primary_style()
        self.save_btn.clicked.connect(self.save_supplier)
        
        self.new_btn = AnimatedButton("🆕 Nuevo")
        self.new_btn.set_secondary_style()
        self.new_btn.clicked.connect(self.reset_form)
        
        self.delete_btn = AnimatedButton("🗑️ Eliminar")
        self.delete_btn.set_danger_style()
        self.delete_btn.clicked.connect(self.delete_supplier)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.new_btn)
        buttons_layout.addWidget(self.delete_btn)
        
        layout.addLayout(buttons_layout)
        
        return panel

    def create_basic_info_tab(self):
        """Crea el tab de información básica"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Campos básicos
        self.supplier_name = self.create_styled_input("Nombre de la empresa *")
        self.contact_person = self.create_styled_input("Persona de contacto")
        self.contact_position = self.create_styled_input("Cargo")
        
        # Teléfono y email
        self.phone = self.create_styled_input("Teléfono principal")
        self.email = self.create_styled_input("Email")
        self.website = self.create_styled_input("Sitio web")
        
        # Categoría
        self.category = QComboBox()
        self.category.setMinimumHeight(38)
        self.category.setStyleSheet(self.get_combo_style())
        
        # Estado
        self.status = QComboBox()
        self.status.addItems(["Activo", "Inactivo", "Suspendido", "En evaluación"])
        self.status.setMinimumHeight(38)
        self.status.setStyleSheet(self.get_combo_style())
        
        form_layout.addRow("Nombre Empresa *:", self.supplier_name)
        form_layout.addRow("Contacto:", self.contact_person)
        form_layout.addRow("Cargo:", self.contact_position)
        form_layout.addRow("Teléfono:", self.phone)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("Sitio Web:", self.website)
        form_layout.addRow("Categoría:", self.category)
        form_layout.addRow("Estado:", self.status)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        return widget

    def create_additional_details_tab(self):
        """Crea el tab de detalles adicionales"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        
        # Dirección
        self.address = self.create_styled_textedit("Dirección completa")
        
        # Información fiscal
        self.tax_id = self.create_styled_input("RUC/NIT")
        self.business_type = QComboBox()
        self.business_type.addItems(["Persona Natural", "Persona Jurídica", "Autónomo"])
        self.business_type.setStyleSheet(self.get_combo_style())
        
        # Términos de pago
        self.payment_terms = QComboBox()
        self.payment_terms.addItems(["Contado", "15 días", "30 días", "60 días", "90 días"])
        self.payment_terms.setStyleSheet(self.get_combo_style())
        
        # Límite de crédito
        self.credit_limit = QDoubleSpinBox()
        self.credit_limit.setRange(0, 1000000)
        self.credit_limit.setPrefix("$ ")
        self.credit_limit.setDecimals(2)
        self.credit_limit.setStyleSheet(self.get_spinbox_style())
        
        # Notas
        self.notes = self.create_styled_textedit("Notas adicionales")
        
        form_layout.addRow("Dirección:", self.address)
        form_layout.addRow("RUC/NIT:", self.tax_id)
        form_layout.addRow("Tipo Negocio:", self.business_type)
        form_layout.addRow("Términos Pago:", self.payment_terms)
        form_layout.addRow("Límite Crédito:", self.credit_limit)
        form_layout.addRow("Notas:", self.notes)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        return widget

    def create_evaluation_tab(self):
        """Crea el tab de evaluación del proveedor"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # Calificación general
        rating_group = QGroupBox("⭐ Calificación General")
        rating_group.setStyleSheet(self.get_group_style())
        rating_layout = QVBoxLayout(rating_group)
        
        self.rating_slider = QSlider(Qt.Horizontal)
        self.rating_slider.setRange(1, 5)
        self.rating_slider.setTickPosition(QSlider.TicksBelow)
        self.rating_slider.setTickInterval(1)
        
        self.rating_label = QLabel("3/5")
        self.rating_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.rating_label.setStyleSheet("color: #3B82F6; text-align: center;")
        
        rating_layout.addWidget(self.rating_slider)
        rating_layout.addWidget(self.rating_label, alignment=Qt.AlignCenter)
        
        # Métricas específicas
        metrics_group = QGroupBox("📊 Métricas de Desempeño")
        metrics_group.setStyleSheet(self.get_group_style())
        metrics_layout = QFormLayout(metrics_group)
        
        self.quality_rating = QComboBox()
        self.quality_rating.addItems(["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        self.quality_rating.setStyleSheet(self.get_combo_style())
        
        self.delivery_rating = QComboBox()
        self.delivery_rating.addItems(["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        self.delivery_rating.setStyleSheet(self.get_combo_style())
        
        self.price_rating = QComboBox()
        self.price_rating.addItems(["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        self.price_rating.setStyleSheet(self.get_combo_style())
        
        self.service_rating = QComboBox()
        self.service_rating.addItems(["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        self.service_rating.setStyleSheet(self.get_combo_style())
        
        metrics_layout.addRow("Calidad:", self.quality_rating)
        metrics_layout.addRow("Entrega:", self.delivery_rating)
        metrics_layout.addRow("Precio:", self.price_rating)
        metrics_layout.addRow("Servicio:", self.service_rating)
        
        # Última evaluación
        self.last_evaluation = QDateEdit()
        self.last_evaluation.setDate(QDate.currentDate())
        self.last_evaluation.setStyleSheet(self.get_spinbox_style())
        metrics_layout.addRow("Última Evaluación:", self.last_evaluation)
        
        layout.addWidget(rating_group)
        layout.addWidget(metrics_group)
        layout.addStretch()
        
        # Conectar señal del slider
        self.rating_slider.valueChanged.connect(self.update_rating_label)
        
        return widget

    def setup_suppliers_table(self):
        """Configura la tabla de proveedores"""
        headers = ["ID", "Nombre", "Contacto", "Teléfono", "Email", "Categoría", "Estado", "Calificación"]
        self.suppliers_table.setColumnCount(len(headers))
        self.suppliers_table.setHorizontalHeaderLabels(headers)
        
        # Configurar anchos de columnas
        self.suppliers_table.setColumnWidth(0, 60)   # ID
        self.suppliers_table.setColumnWidth(1, 200)  # Nombre
        self.suppliers_table.setColumnWidth(2, 120)  # Contacto
        self.suppliers_table.setColumnWidth(3, 100)  # Teléfono
        self.suppliers_table.setColumnWidth(4, 150)  # Email
        self.suppliers_table.setColumnWidth(5, 120)  # Categoría
        self.suppliers_table.setColumnWidth(6, 80)   # Estado
        self.suppliers_table.setColumnWidth(7, 80)   # Calificación
        
        # Configurar header
        header = self.suppliers_table.horizontalHeader()
        header.setStretchLastSection(True)

    # Métodos de utilidad para estilos
    def get_group_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1E293B;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
    
    def get_combo_style(self):
        return """
            QComboBox {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
                min-height: 38px;
            }
            QComboBox:focus {
                border-color: #3B82F6;
            }
        """
    
    def get_spinbox_style(self):
        return """
            QSpinBox, QDoubleSpinBox {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
                min-height: 38px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #3B82F6;
            }
        """
    
    def create_styled_input(self, placeholder):
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
        """)
        return input_field
    
    def create_styled_textedit(self, placeholder):
        textedit = QTextEdit()
        textedit.setPlaceholderText(placeholder)
        textedit.setMaximumHeight(80)
        textedit.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
            }
            QTextEdit:focus {
                border-color: #3B82F6;
                background: #F8FAFF;
            }
        """)
        return textedit

    # Métodos de funcionalidad
    def load_suppliers(self):
        """Carga los proveedores desde la base de datos"""
        if not self.db:
            return
            
        try:
            suppliers = self.db.fetch("""
                SELECT id, nombre, contacto, telefono, email, categoria, estado, calificacion
                FROM Proveedores 
                ORDER BY nombre
            """)
            
            self.populate_suppliers_table(suppliers)
            
        except Exception as e:
            print(f"Error cargando proveedores: {e}")

    def load_categories(self):
        """Carga las categorías de proveedores"""
        try:
            categories = self.db.fetch("SELECT DISTINCT categoria FROM Proveedores WHERE categoria IS NOT NULL")
            self.supplier_categories = [cat[0] for cat in categories if cat[0]]
            
            # Actualizar combobox de categorías
            self.category.clear()
            self.category.addItem("Seleccionar categoría")
            for cat in self.supplier_categories:
                self.category.addItem(cat)
            
            # Actualizar filtro de categorías
            self.category_filter.clear()
            self.category_filter.addItem("Todas las categorías")
            for cat in self.supplier_categories:
                self.category_filter.addItem(cat)
                
        except Exception as e:
            print(f"Error cargando categorías: {e}")

    def populate_suppliers_table(self, suppliers):
        """Llena la tabla con los datos de proveedores"""
        self.suppliers_table.setRowCount(0)
        
        for supplier in suppliers:
            row = self.suppliers_table.rowCount()
            self.suppliers_table.insertRow(row)
            
            # Crear items
            items = [
                QTableWidgetItem(str(supplier[0])),  # ID
                QTableWidgetItem(supplier[1]),       # Nombre
                QTableWidgetItem(supplier[2] or ""), # Contacto
                QTableWidgetItem(supplier[3] or ""), # Teléfono
                QTableWidgetItem(supplier[4] or ""), # Email
                QTableWidgetItem(supplier[5] or ""), # Categoría
                QTableWidgetItem(supplier[6] or ""), # Estado
                QTableWidgetItem(str(supplier[7]) if supplier[7] else "0")  # Calificación
            ]
            
            # Color según estado
            estado = supplier[6] or ""
            if estado == "Inactivo":
                for item in items:
                    item.setForeground(QColor("#94A3B8"))
            elif estado == "Suspendido":
                for item in items:
                    item.setForeground(QColor("#EF4444"))
            
            # Añadir items a la tabla
            for col, item in enumerate(items):
                self.suppliers_table.setItem(row, col, item)

    def filter_suppliers(self):
        """Filtra proveedores según búsqueda y filtros"""
        search_term = self.search_input.text().strip().lower()
        category_filter = self.category_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        try:
            query = """
                SELECT id, nombre, contacto, telefono, email, categoria, estado, calificacion
                FROM Proveedores 
                WHERE 1=1
            """
            params = []
            
            if search_term:
                query += " AND (LOWER(nombre) LIKE ? OR LOWER(contacto) LIKE ? OR LOWER(email) LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
            
            if category_filter != "Todas las categorías":
                query += " AND categoria = ?"
                params.append(category_filter)
            
            if status_filter != "Todos":
                query += " AND estado = ?"
                params.append(status_filter)
            
            query += " ORDER BY nombre"
            
            suppliers = self.db.fetch(query, params)
            self.populate_suppliers_table(suppliers)
            
        except Exception as e:
            print(f"Error filtrando proveedores: {e}")

    def on_supplier_double_click(self, index):
        """Maneja el doble click en la tabla"""
        row = index.row()
        supplier_id = int(self.suppliers_table.item(row, 0).text())
        self.load_supplier_details(supplier_id)

    def load_supplier_details(self, supplier_id):
        """Carga los detalles de un proveedor en el formulario"""
        try:
            supplier = self.db.fetch(
                "SELECT * FROM Proveedores WHERE id = ?",
                (supplier_id,)
            )
            
            if supplier:
                supplier_data = supplier[0]
                
                # Información básica
                self.supplier_name.setText(supplier_data[1])
                self.contact_person.setText(supplier_data[2] or "")
                self.contact_position.setText(supplier_data[3] or "")
                self.phone.setText(supplier_data[4] or "")
                self.email.setText(supplier_data[5] or "")
                self.website.setText(supplier_data[6] or "")
                
                # Categoría y estado
                if supplier_data[7]:
                    index = self.category.findText(supplier_data[7])
                    if index >= 0:
                        self.category.setCurrentIndex(index)
                
                if supplier_data[8]:
                    index = self.status.findText(supplier_data[8])
                    if index >= 0:
                        self.status.setCurrentIndex(index)
                
                # Detalles adicionales
                self.address.setPlainText(supplier_data[9] or "")
                self.tax_id.setText(supplier_data[10] or "")
                
                if supplier_data[11]:
                    index = self.business_type.findText(supplier_data[11])
                    if index >= 0:
                        self.business_type.setCurrentIndex(index)
                
                if supplier_data[12]:
                    index = self.payment_terms.findText(supplier_data[12])
                    if index >= 0:
                        self.payment_terms.setCurrentIndex(index)
                
                self.credit_limit.setValue(float(supplier_data[13] or 0))
                self.notes.setPlainText(supplier_data[14] or "")
                
                # Evaluación
                if supplier_data[15]:
                    self.rating_slider.setValue(int(supplier_data[15]))
                
                self.current_supplier_id = supplier_id
                
        except Exception as e:
            print(f"Error cargando detalles del proveedor: {e}")

    def update_rating_label(self, value):
        """Actualiza la etiqueta de calificación"""
        self.rating_label.setText(f"{value}/5")

    def validate_form(self):
        """Valida los datos del formulario"""
        nombre = self.supplier_name.text().strip()
        
        if not nombre:
            self.show_error("Error de Validación", "El nombre de la empresa es obligatorio")
            self.supplier_name.setFocus()
            return False
            
        return True

    def save_supplier(self):
        """Guarda un nuevo proveedor o actualiza uno existente"""
        if not self.validate_form():
            return
            
        try:
            # Recopilar datos del formulario
            nombre = self.supplier_name.text().strip()
            contacto = self.contact_person.text().strip()
            cargo = self.contact_position.text().strip()
            telefono = self.phone.text().strip()
            email = self.email.text().strip()
            website = self.website.text().strip()
            categoria = self.category.currentText() if self.category.currentIndex() > 0 else None
            estado = self.status.currentText()
            
            direccion = self.address.toPlainText().strip()
            ruc = self.tax_id.text().strip()
            tipo_negocio = self.business_type.currentText() if self.business_type.currentIndex() > 0 else None
            terminos_pago = self.payment_terms.currentText() if self.payment_terms.currentIndex() > 0 else None
            limite_credito = self.credit_limit.value()
            notas = self.notes.toPlainText().strip()
            
            calificacion = self.rating_slider.value()
            
            if self.current_supplier_id:
                # Actualizar proveedor existente
                query = """
                    UPDATE Proveedores 
                    SET nombre=?, contacto=?, cargo=?, telefono=?, email=?, website=?,
                        categoria=?, estado=?, direccion=?, ruc=?, tipo_negocio=?,
                        terminos_pago=?, limite_credito=?, notas=?, calificacion=?
                    WHERE id=?
                """
                self.db.execute(
                    query,
                    (nombre, contacto, cargo, telefono, email, website,
                     categoria, estado, direccion, ruc, tipo_negocio,
                     terminos_pago, limite_credito, notas, calificacion,
                     self.current_supplier_id)
                )
                self.show_success("Proveedor Actualizado", "Proveedor actualizado correctamente")
            else:
                # Crear nuevo proveedor
                query = """
                    INSERT INTO Proveedores 
                    (nombre, contacto, cargo, telefono, email, website, categoria, estado,
                     direccion, ruc, tipo_negocio, terminos_pago, limite_credito, notas, calificacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.db.execute(
                    query,
                    (nombre, contacto, cargo, telefono, email, website,
                     categoria, estado, direccion, ruc, tipo_negocio,
                     terminos_pago, limite_credito, notas, calificacion)
                )
                self.show_success("Proveedor Registrado", "Proveedor registrado correctamente")
            
            self.reset_form()
            self.load_suppliers()
            self.load_categories()
            
        except Exception as e:
            self.show_error("Error", f"Error al guardar proveedor: {e}")

    def delete_supplier(self):
        """Elimina el proveedor seleccionado"""
        if not self.current_supplier_id:
            self.show_warning("Advertencia", "Seleccione un proveedor para eliminar")
            return
            
        try:
            # Verificar si el proveedor tiene productos asociados
            productos = self.db.fetch(
                "SELECT COUNT(*) FROM Productos WHERE proveedor_id = ?",
                (self.current_supplier_id,)
            )
            
            tiene_productos = productos[0][0] > 0 if productos else False
            
            if tiene_productos:
                reply = self.show_question(
                    "Proveedor con Productos",
                    "Este proveedor tiene productos asociados.\n\n"
                    "¿Desea eliminarlo de todas formas?\n\n"
                    "Los productos quedarán sin proveedor asignado.",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            
            reply = self.show_question(
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar el proveedor '{self.supplier_name.text()}'?"
            )
            
            if reply == QMessageBox.Yes:
                self.db.execute("DELETE FROM Proveedores WHERE id = ?", (self.current_supplier_id,))
                self.show_success("Proveedor Eliminado", "Proveedor eliminado correctamente")
                self.reset_form()
                self.load_suppliers()
                
        except Exception as e:
            self.show_error("Error", f"Error al eliminar proveedor: {e}")

    def reset_form(self):
        """Limpia el formulario"""
        self.supplier_name.clear()
        self.contact_person.clear()
        self.contact_position.clear()
        self.phone.clear()
        self.email.clear()
        self.website.clear()
        self.category.setCurrentIndex(0)
        self.status.setCurrentIndex(0)
        self.address.clear()
        self.tax_id.clear()
        self.business_type.setCurrentIndex(0)
        self.payment_terms.setCurrentIndex(0)
        self.credit_limit.setValue(0)
        self.notes.clear()
        self.rating_slider.setValue(3)
        self.quality_rating.setCurrentIndex(2)
        self.delivery_rating.setCurrentIndex(2)
        self.price_rating.setCurrentIndex(2)
        self.service_rating.setCurrentIndex(2)
        self.last_evaluation.setDate(QDate.currentDate())
        
        self.current_supplier_id = None
        
        # Limpiar selección en la tabla
        self.suppliers_table.clearSelection()

    def export_suppliers(self):
        """Exporta los proveedores a CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exportar Proveedores",
                f"proveedores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                suppliers = self.db.fetch("""
                    SELECT nombre, contacto, cargo, telefono, email, website, categoria, estado,
                           direccion, ruc, tipo_negocio, terminos_pago, limite_credito, calificacion
                    FROM Proveedores
                    ORDER BY nombre
                """)
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # Encabezados
                    writer.writerow([
                        'Nombre', 'Contacto', 'Cargo', 'Teléfono', 'Email', 'Website',
                        'Categoría', 'Estado', 'Dirección', 'RUC/NIT', 'Tipo Negocio',
                        'Términos Pago', 'Límite Crédito', 'Calificación'
                    ])
                    
                    # Datos
                    for supplier in suppliers:
                        writer.writerow(supplier)
                
                self.show_success("Exportación Exitosa", f"Proveedores exportados a:\n{filename}")
                
        except Exception as e:
            self.show_error("Error", f"Error al exportar proveedores: {e}")

    def show_statistics(self):
        """Muestra estadísticas de proveedores"""
        try:
            total_proveedores = self.db.fetch("SELECT COUNT(*) FROM Proveedores")[0][0]
            proveedores_activos = self.db.fetch("SELECT COUNT(*) FROM Proveedores WHERE estado = 'Activo'")[0][0]
            categorias_count = self.db.fetch("SELECT COUNT(DISTINCT categoria) FROM Proveedores WHERE categoria IS NOT NULL")[0][0]
            
            # Proveedor mejor calificado
            mejor_calificado = self.db.fetch("SELECT nombre, calificacion FROM Proveedores ORDER BY calificacion DESC LIMIT 1")
            mejor_nombre = mejor_calificado[0][0] if mejor_calificado else "N/A"
            mejor_calif = mejor_calificado[0][1] if mejor_calificado else 0
            
            stats_text = f"""
📊 ESTADÍSTICAS DE PROVEEDORES

🏢 Total de proveedores: {total_proveedores}
✅ Proveedores activos: {proveedores_activos}
🏷️ Categorías diferentes: {categorias_count}
⭐ Mejor calificado: {mejor_nombre} ({mejor_calif}/5)

📈 Porcentaje de actividad: {(proveedores_activos/total_proveedores*100):.1f}%
            """.strip()

            self.show_info("Estadísticas de Proveedores", stats_text)

        except Exception as e:
            self.show_error("Error", f"Error al calcular estadísticas: {e}")

    def manage_categories(self):
        """Gestiona las categorías de proveedores"""
        nueva_categoria, ok = QInputDialog.getText(
            self, "Gestionar Categorías",
            "Ingrese una nueva categoría:",
            text=""
        )
        
        if ok and nueva_categoria.strip():
            try:
                # Verificar si ya existe
                existe = self.db.fetch(
                    "SELECT COUNT(*) FROM Proveedores WHERE categoria = ?",
                    (nueva_categoria.strip(),)
                )[0][0] > 0
                
                if not existe:
                    # Actualizar un proveedor temporalmente para crear la categoría
                    self.db.execute(
                        "UPDATE Proveedores SET categoria = ? WHERE id = (SELECT id FROM Proveedores LIMIT 1)",
                        (nueva_categoria.strip(),)
                    )
                
                self.load_categories()
                self.show_success("Categoría Agregada", "Categoría agregada correctamente")
                
            except Exception as e:
                self.show_error("Error", f"Error agregando categoría: {e}")

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
    
    def show_question(self, title, message, buttons=QMessageBox.Yes | QMessageBox.No):
        reply = QMessageBox.question(self, title, message, buttons)
        return reply

# Función para crear la tabla de proveedores si no existe
def create_suppliers_table(db):
    """Crea la tabla de proveedores si no existe"""
    db.execute("""
        CREATE TABLE IF NOT EXISTS Proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            cargo TEXT,
            telefono TEXT,
            email TEXT,
            website TEXT,
            categoria TEXT,
            estado TEXT DEFAULT 'Activo',
            direccion TEXT,
            ruc TEXT,
            tipo_negocio TEXT,
            terminos_pago TEXT,
            limite_credito REAL DEFAULT 0,
            notas TEXT,
            calificacion INTEGER DEFAULT 3,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
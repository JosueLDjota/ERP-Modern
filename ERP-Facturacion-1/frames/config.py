"""
frames/config.py
Sistema de Configuración Profesional ERP - Windows 11 Style
Configuración global, empresa, facturación, seguridad, backup, y más.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QTabWidget,
    QFormLayout, QMessageBox, QFileDialog, QScrollArea, QSplitter,
    QProgressBar, QListWidget, QListWidgetItem, QInputDialog
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QFont, QColor, QPalette, QIcon
import json
import os
import shutil
from datetime import datetime
import sqlite3

class AnimatedButton(QPushButton):
    """Botón con animaciones suaves al estilo Windows 11"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)

class ConfigFrame(QWidget):
    """Sistema de Configuración Profesional ERP - Windows 11 Style"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        self.db = parent.db if parent and hasattr(parent, 'db') else None
        self.current_settings = {}
        self.backup_timer = QTimer()
        
        self.setup_ui()
        self.load_all_settings()

    def setup_ui(self):
        """Configura la interfaz de usuario moderna"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("⚙️ Configuración del Sistema ERP")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1E293B;")
        
        subtitle = QLabel("Configuración global y parámetros del sistema")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #64748B;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Botones de acción rápida
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        self.save_btn = AnimatedButton("💾 Guardar Todo")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10B981, stop:1 #34D399);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #10B981);
            }
        """)
        self.save_btn.clicked.connect(self.save_all_settings)
        
        self.reset_btn = AnimatedButton("🔄 Restablecer")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                color: #475569;
                font-weight: 500;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: #F1F5F9;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.reset_btn)
        
        header_layout.addLayout(action_layout)
        main_layout.addLayout(header_layout)

        # Tabs principales
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background: #F1F5F9;
            }
        """)
        
        # Crear todas las pestañas
        self.create_company_tab()
        self.create_invoicing_tab()
        self.create_discounts_tab()
        self.create_receipt_tab()
        self.create_security_tab()
        self.create_backup_tab()
        self.create_system_tab()
        
        main_layout.addWidget(self.tabs)

    def create_company_tab(self):
        """Pestaña de configuración de empresa"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Información de la Empresa
        company_group = QGroupBox("🏢 Información de la Empresa")
        company_group.setStyleSheet(self.get_group_style())
        company_layout = QFormLayout(company_group)
        
        self.company_name = self.create_styled_input("Nombre de la empresa")
        self.company_ruc = self.create_styled_input("RUC/NIT")
        self.company_address = self.create_styled_textedit("Dirección fiscal")
        self.company_phone = self.create_styled_input("Teléfono")
        self.company_email = self.create_styled_input("Email")
        self.company_website = self.create_styled_input("Sitio web")
        
        company_layout.addRow("Nombre Legal *:", self.company_name)
        company_layout.addRow("RUC/NIT *:", self.company_ruc)
        company_layout.addRow("Dirección:", self.company_address)
        company_layout.addRow("Teléfono:", self.company_phone)
        company_layout.addRow("Email:", self.company_email)
        company_layout.addRow("Sitio Web:", self.company_website)
        
        # Información de Contacto
        contact_group = QGroupBox("📞 Información de Contacto")
        contact_group.setStyleSheet(self.get_group_style())
        contact_layout = QFormLayout(contact_group)
        
        self.contact_name = self.create_styled_input("Nombre del contacto principal")
        self.contact_position = self.create_styled_input("Cargo")
        self.contact_mobile = self.create_styled_input("Teléfono móvil")
        
        contact_layout.addRow("Contacto Principal:", self.contact_name)
        contact_layout.addRow("Cargo:", self.contact_position)
        contact_layout.addRow("Teléfono Móvil:", self.contact_mobile)
        
        # Configuración Regional
        regional_group = QGroupBox("🌍 Configuración Regional")
        regional_group.setStyleSheet(self.get_group_style())
        regional_layout = QFormLayout(regional_group)
        
        self.currency = QComboBox()
        self.currency.addItems(["USD - Dólar Americano", "EUR - Euro", "MXN - Peso Mexicano", 
                               "COP - Peso Colombiano", "PEN - Sol Peruano"])
        self.currency.setStyleSheet(self.get_combo_style())
        
        self.language = QComboBox()
        self.language.addItems(["Español", "English", "Português"])
        self.language.setStyleSheet(self.get_combo_style())
        
        self.timezone = QComboBox()
        self.timezone.addItems(["America/Mexico_City", "America/Bogota", "America/Lima", 
                               "America/New_York", "UTC"])
        self.timezone.setStyleSheet(self.get_combo_style())
        
        regional_layout.addRow("Moneda:", self.currency)
        regional_layout.addRow("Idioma:", self.language)
        regional_layout.addRow("Zona Horaria:", self.timezone)
        
        content_layout.addWidget(company_group)
        content_layout.addWidget(contact_group)
        content_layout.addWidget(regional_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(widget, "Empresa")

    def create_invoicing_tab(self):
        """Pestaña de configuración de facturación"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Configuración de Facturación
        invoice_group = QGroupBox("🧾 Configuración de Facturación")
        invoice_group.setStyleSheet(self.get_group_style())
        invoice_layout = QFormLayout(invoice_group)
        
        self.invoice_series = self.create_styled_input("Serie de facturación")
        self.invoice_start = QSpinBox()
        self.invoice_start.setRange(1, 999999)
        self.invoice_start.setStyleSheet(self.get_spinbox_style())
        
        self.default_iva = QDoubleSpinBox()
        self.default_iva.setRange(0, 50)
        self.default_iva.setSuffix(" %")
        self.default_iva.setDecimals(2)
        self.default_iva.setStyleSheet(self.get_spinbox_style())
        
        self.invoice_terms = self.create_styled_textedit("Términos y condiciones")
        
        invoice_layout.addRow("Serie de Facturación:", self.invoice_series)
        invoice_layout.addRow("Número Inicial:", self.invoice_start)
        invoice_layout.addRow("IVA por Defecto:", self.default_iva)
        invoice_layout.addRow("Términos y Condiciones:", self.invoice_terms)
        
        # Resoluciones DIAN/SAT
        resolution_group = QGroupBox("📄 Resoluciones Tributarias")
        resolution_group.setStyleSheet(self.get_group_style())
        resolution_layout = QFormLayout(resolution_group)
        
        self.resolution_number = self.create_styled_input("Número de resolución")
        self.resolution_date = self.create_styled_input("Fecha de resolución (YYYY-MM-DD)")
        self.resolution_from = self.create_styled_input("Número desde")
        self.resolution_to = self.create_styled_input("Número hasta")
        
        resolution_layout.addRow("Número Resolución:", self.resolution_number)
        resolution_layout.addRow("Fecha Resolución:", self.resolution_date)
        resolution_layout.addRow("Numeración Desde:", self.resolution_from)
        resolution_layout.addRow("Numeración Hasta:", self.resolution_to)
        
        content_layout.addWidget(invoice_group)
        content_layout.addWidget(resolution_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(widget, "Facturación")

    def create_discounts_tab(self):
        """Pestaña de gestión de descuentos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Lista de descuentos
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        list_header = QLabel("📋 Descuentos Configurados")
        list_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        list_header.setStyleSheet("color: #1E293B; margin-bottom: 10px;")
        list_layout.addWidget(list_header)
        
        self.discounts_table = QTableWidget()
        self.discounts_table.setColumnCount(4)
        self.discounts_table.setHorizontalHeaderLabels(["ID", "Nombre", "Tipo", "Porcentaje"])
        self.discounts_table.setStyleSheet(self.get_table_style())
        self.discounts_table.horizontalHeader().setStretchLastSection(True)
        self.discounts_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        list_layout.addWidget(self.discounts_table)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        self.new_discount_btn = AnimatedButton("➕ Nuevo Descuento")
        self.new_discount_btn.setStyleSheet(self.get_secondary_button_style())
        self.new_discount_btn.clicked.connect(self.reset_discount_form)
        
        self.delete_discount_btn = AnimatedButton("🗑️ Eliminar")
        self.delete_discount_btn.setStyleSheet(self.get_danger_button_style())
        self.delete_discount_btn.clicked.connect(self.delete_discount)
        
        btn_layout.addWidget(self.new_discount_btn)
        btn_layout.addWidget(self.delete_discount_btn)
        btn_layout.addStretch()
        
        list_layout.addLayout(btn_layout)
        
        # Formulario de descuentos
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        form_header = QLabel("📝 Configurar Descuento")
        form_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        form_header.setStyleSheet("color: #1E293B; margin-bottom: 20px;")
        form_layout.addWidget(form_header)
        
        discount_form = QFormLayout()
        
        self.discount_id = QLineEdit()
        self.discount_id.setVisible(False)
        
        self.discount_name = self.create_styled_input("Nombre del descuento")
        self.discount_percentage = QDoubleSpinBox()
        self.discount_percentage.setRange(0, 100)
        self.discount_percentage.setSuffix(" %")
        self.discount_percentage.setDecimals(2)
        self.discount_percentage.setStyleSheet(self.get_spinbox_style())
        
        self.discount_type = QComboBox()
        self.discount_type.addItems(["General", "Volumen", "Cliente Frecuente", "Temporada", "Producto"])
        self.discount_type.setStyleSheet(self.get_combo_style())
        
        self.discount_min_amount = QDoubleSpinBox()
        self.discount_min_amount.setRange(0, 1000000)
        self.discount_min_amount.setPrefix("$ ")
        self.discount_min_amount.setStyleSheet(self.get_spinbox_style())
        
        self.discount_active = QCheckBox("Descuento activo")
        self.discount_active.setChecked(True)
        self.discount_active.setStyleSheet("QCheckBox { spacing: 8px; }")
        
        discount_form.addRow("Nombre *:", self.discount_name)
        discount_form.addRow("Porcentaje *:", self.discount_percentage)
        discount_form.addRow("Tipo:", self.discount_type)
        discount_form.addRow("Monto Mínimo:", self.discount_min_amount)
        discount_form.addRow("", self.discount_active)
        
        form_layout.addLayout(discount_form)
        form_layout.addStretch()
        
        self.save_discount_btn = AnimatedButton("💾 Guardar Descuento")
        self.save_discount_btn.setStyleSheet(self.get_primary_button_style())
        self.save_discount_btn.clicked.connect(self.save_discount)
        form_layout.addWidget(self.save_discount_btn)
        
        splitter.addWidget(list_widget)
        splitter.addWidget(form_widget)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
        self.tabs.addTab(widget, "Descuentos")

    def create_receipt_tab(self):
        """Pestaña de plantillas de recibos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header informativo
        info_label = QLabel(
            "📄 Editor de Plantillas de Recibos\n"
            "Variables disponibles: {{numero_factura}}, {{fecha}}, {{cliente}}, {{total}}, {{iva}}, {{subtotal}}"
        )
        info_label.setStyleSheet("color: #64748B; background: #F8FAFC; padding: 12px; border-radius: 6px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Editor de plantilla
        self.receipt_template = QTextEdit()
        self.receipt_template.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Courier New';
                font-size: 12px;
            }
            QTextEdit:focus {
                border-color: #3B82F6;
            }
        """)
        layout.addWidget(self.receipt_template, 1)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        
        self.preview_btn = AnimatedButton("👁️ Vista Previa")
        self.preview_btn.setStyleSheet(self.get_secondary_button_style())
        self.preview_btn.clicked.connect(self.preview_receipt)
        
        self.save_template_btn = AnimatedButton("💾 Guardar Plantilla")
        self.save_template_btn.setStyleSheet(self.get_primary_button_style())
        self.save_template_btn.clicked.connect(self.save_receipt_template)
        
        self.restore_template_btn = AnimatedButton("🔄 Restaurar Original")
        self.restore_template_btn.setStyleSheet(self.get_secondary_button_style())
        self.restore_template_btn.clicked.connect(self.restore_default_template)
        
        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.save_template_btn)
        btn_layout.addWidget(self.restore_template_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.tabs.addTab(widget, "Recibos")

    def create_security_tab(self):
        """Pestaña de configuración de seguridad"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Configuración de Contraseñas
        password_group = QGroupBox("🔐 Políticas de Contraseñas")
        password_group.setStyleSheet(self.get_group_style())
        password_layout = QFormLayout(password_group)
        
        self.min_password_length = QSpinBox()
        self.min_password_length.setRange(4, 20)
        self.min_password_length.setStyleSheet(self.get_spinbox_style())
        
        self.require_special_chars = QCheckBox("Requerir caracteres especiales")
        self.require_uppercase = QCheckBox("Requerir mayúsculas")
        self.require_numbers = QCheckBox("Requerir números")
        self.password_expiry = QSpinBox()
        self.password_expiry.setRange(0, 365)
        self.password_expiry.setSuffix(" días (0 = nunca expira)")
        self.password_expiry.setStyleSheet(self.get_spinbox_style())
        
        password_layout.addRow("Longitud Mínima:", self.min_password_length)
        password_layout.addRow("", self.require_special_chars)
        password_layout.addRow("", self.require_uppercase)
        password_layout.addRow("", self.require_numbers)
        password_layout.addRow("Caducidad:", self.password_expiry)
        
        # Configuración de Sesiones
        session_group = QGroupBox("💻 Configuración de Sesiones")
        session_group.setStyleSheet(self.get_group_style())
        session_layout = QFormLayout(session_group)
        
        self.session_timeout = QSpinBox()
        self.session_timeout.setRange(5, 480)
        self.session_timeout.setSuffix(" minutos")
        self.session_timeout.setStyleSheet(self.get_spinbox_style())
        
        self.max_login_attempts = QSpinBox()
        self.max_login_attempts.setRange(1, 10)
        self.max_login_attempts.setStyleSheet(self.get_spinbox_style())
        
        self.lockout_duration = QSpinBox()
        self.lockout_duration.setRange(1, 60)
        self.lockout_duration.setSuffix(" minutos")
        self.lockout_duration.setStyleSheet(self.get_spinbox_style())
        
        session_layout.addRow("Tiempo de Espera:", self.session_timeout)
        session_layout.addRow("Intentos de Login:", self.max_login_attempts)
        session_layout.addRow("Duración Bloqueo:", self.lockout_duration)
        
        content_layout.addWidget(password_group)
        content_layout.addWidget(session_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.tabs.addTab(widget, "Seguridad")

    def create_backup_tab(self):
        """Pestaña de configuración de backup"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Configuración de Backup Automático
        auto_backup_group = QGroupBox("🛡️ Backup Automático")
        auto_backup_group.setStyleSheet(self.get_group_style())
        auto_backup_layout = QFormLayout(auto_backup_group)
        
        self.auto_backup_enabled = QCheckBox("Habilitar backup automático")
        self.auto_backup_enabled.setChecked(True)
        
        self.backup_interval = QComboBox()
        self.backup_interval.addItems(["Diario", "Semanal", "Mensual"])
        self.backup_interval.setStyleSheet(self.get_combo_style())
        
        self.backup_time = QComboBox()
        times = [f"{h:02d}:00" for h in range(24)]
        self.backup_time.addItems(times)
        self.backup_time.setStyleSheet(self.get_combo_style())
        
        self.backup_retention = QSpinBox()
        self.backup_retention.setRange(1, 365)
        self.backup_retention.setSuffix(" días")
        self.backup_retention.setStyleSheet(self.get_spinbox_style())
        
        auto_backup_layout.addRow("", self.auto_backup_enabled)
        auto_backup_layout.addRow("Frecuencia:", self.backup_interval)
        auto_backup_layout.addRow("Hora:", self.backup_time)
        auto_backup_layout.addRow("Retención:", self.backup_retention)
        
        # Backup Manual
        manual_backup_group = QGroupBox("💾 Backup Manual")
        manual_backup_group.setStyleSheet(self.get_group_style())
        manual_backup_layout = QVBoxLayout(manual_backup_group)
        
        backup_btn_layout = QHBoxLayout()
        self.backup_now_btn = AnimatedButton("📦 Crear Backup Ahora")
        self.backup_now_btn.setStyleSheet(self.get_primary_button_style())
        self.backup_now_btn.clicked.connect(self.create_backup)
        
        self.restore_btn = AnimatedButton("🔄 Restaurar Backup")
        self.restore_btn.setStyleSheet(self.get_secondary_button_style())
        self.restore_btn.clicked.connect(self.restore_backup)
        
        backup_btn_layout.addWidget(self.backup_now_btn)
        backup_btn_layout.addWidget(self.restore_btn)
        backup_btn_layout.addStretch()
        
        manual_backup_layout.addLayout(backup_btn_layout)
        
        # Lista de backups
        self.backup_list = QListWidget()
        self.backup_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
            }
        """)
        manual_backup_layout.addWidget(self.backup_list)
        
        layout.addWidget(auto_backup_group)
        layout.addWidget(manual_backup_group)
        layout.addStretch()
        
        self.tabs.addTab(widget, "Backup")

    def create_system_tab(self):
        """Pestaña de configuración del sistema"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Configuración de Rendimiento
        performance_group = QGroupBox("🚀 Configuración de Rendimiento")
        performance_group.setStyleSheet(self.get_group_style())
        performance_layout = QFormLayout(performance_group)
        
        self.cache_size = QSpinBox()
        self.cache_size.setRange(10, 1000)
        self.cache_size.setSuffix(" MB")
        self.cache_size.setStyleSheet(self.get_spinbox_style())
        
        self.auto_refresh = QCheckBox("Actualización automática de datos")
        self.auto_refresh.setChecked(True)
        
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(1, 60)
        self.refresh_interval.setSuffix(" segundos")
        self.refresh_interval.setStyleSheet(self.get_spinbox_style())
        
        performance_layout.addRow("Tamaño de Cache:", self.cache_size)
        performance_layout.addRow("", self.auto_refresh)
        performance_layout.addRow("Intervalo Actualización:", self.refresh_interval)
        
        # Configuración de Base de Datos
        database_group = QGroupBox("🗄️ Configuración de Base de Datos")
        database_group.setStyleSheet(self.get_group_style())
        database_layout = QFormLayout(database_group)
        
        self.db_optimize = QCheckBox("Optimizar base de datos al iniciar")
        self.db_clean_logs = QCheckBox("Limpiar logs antiguos automáticamente")
        self.log_retention = QSpinBox()
        self.log_retention.setRange(1, 365)
        self.log_retention.setSuffix(" días")
        self.log_retention.setStyleSheet(self.get_spinbox_style())
        
        database_layout.addRow("", self.db_optimize)
        database_layout.addRow("", self.db_clean_logs)
        database_layout.addRow("Retención de Logs:", self.log_retention)
        
        content_layout.addWidget(performance_group)
        content_layout.addWidget(database_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.tabs.addTab(widget, "Sistema")

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
    
    def get_primary_button_style(self):
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, stop:1 #60A5FA);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563EB, stop:1 #3B82F6);
            }
        """
    
    def get_secondary_button_style(self):
        return """
            QPushButton {
                background: transparent;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                color: #475569;
                font-weight: 500;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: #F1F5F9;
                border-color: #CBD5E1;
            }
        """
    
    def get_danger_button_style(self):
        return """
            QPushButton {
                background: transparent;
                border: 1.5px solid #FECACA;
                border-radius: 8px;
                color: #DC2626;
                font-weight: 500;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: #FEF2F2;
                border-color: #FCA5A5;
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
    
    def get_table_style(self):
        return """
            QTableWidget {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
            }
            QHeaderView::section {
                background: #F8FAFC;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
            }
        """

    # Métodos de funcionalidad
    def load_all_settings(self):
        """Carga todas las configuraciones desde la base de datos"""
        try:
            # Cargar configuración de empresa
            settings = self.db.fetch("SELECT clave, valor FROM Configuracion")
            for clave, valor in settings:
                self.current_settings[clave] = valor
            
            # Aplicar configuraciones a los campos
            self.apply_settings_to_ui()
            
            # Cargar descuentos
            self.load_discounts_list()
            
        except Exception as e:
            print(f"Error cargando configuraciones: {e}")

    def apply_settings_to_ui(self):
        """Aplica las configuraciones cargadas a la interfaz"""
        # Empresa
        self.company_name.setText(self.current_settings.get('empresa_nombre', ''))
        self.company_ruc.setText(self.current_settings.get('empresa_ruc', ''))
        # ... aplicar más configuraciones

    def load_discounts_list(self):
        """Carga la lista de descuentos"""
        try:
            discounts = self.db.fetch("SELECT id, nombre, tipo, porcentaje FROM Descuentos")
            self.discounts_table.setRowCount(len(discounts))
            
            for row, discount in enumerate(discounts):
                for col, value in enumerate(discount):
                    item = QTableWidgetItem(str(value))
                    self.discounts_table.setItem(row, col, item)
                    
        except Exception as e:
            print(f"Error cargando descuentos: {e}")

    def save_all_settings(self):
        """Guarda todas las configuraciones"""
        try:
            # Recopilar configuraciones de todos los tabs
            settings_to_save = {
                'empresa_nombre': self.company_name.text(),
                'empresa_ruc': self.company_ruc.text(),
                # ... recopilar más configuraciones
            }
            
            # Guardar en base de datos
            for clave, valor in settings_to_save.items():
                self.db.set_config(clave, valor)
            
            QMessageBox.information(self, "Configuración Guardada", 
                                  "Todas las configuraciones han sido guardadas correctamente.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando configuraciones: {e}")

    def reset_to_defaults(self):
        """Restablece todas las configuraciones a los valores por defecto"""
        reply = QMessageBox.question(
            self, "Confirmar Restablecimiento",
            "¿Está seguro de que desea restablecer todas las configuraciones a sus valores por defecto?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Implementar lógica de restablecimiento
                QMessageBox.information(self, "Configuración Restablecida", 
                                      "Todas las configuraciones han sido restablecidas.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error restableciendo configuraciones: {e}")

    def save_discount(self):
        """Guarda un descuento"""
        try:
            nombre = self.discount_name.text().strip()
            porcentaje = self.discount_percentage.value()
            tipo = self.discount_type.currentText()
            
            if not nombre:
                QMessageBox.warning(self, "Validación", "El nombre del descuento es obligatorio.")
                return
            
            if self.discount_id.text():  # Actualizar
                query = "UPDATE Descuentos SET nombre=?, tipo=?, porcentaje=? WHERE id=?"
                self.db.execute(query, (nombre, tipo, porcentaje/100, self.discount_id.text()))
            else:  # Insertar
                query = "INSERT INTO Descuentos (nombre, tipo, porcentaje) VALUES (?, ?, ?)"
                self.db.execute(query, (nombre, tipo, porcentaje/100))
            
            self.load_discounts_list()
            self.reset_discount_form()
            QMessageBox.information(self, "Éxito", "Descuento guardado correctamente.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando descuento: {e}")

    def delete_discount(self):
        """Elimina el descuento seleccionado"""
        current_row = self.discounts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selección", "Seleccione un descuento para eliminar.")
            return
        
        discount_id = self.discounts_table.item(current_row, 0).text()
        discount_name = self.discounts_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de eliminar el descuento '{discount_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute("DELETE FROM Descuentos WHERE id = ?", (discount_id,))
                self.load_discounts_list()
                self.reset_discount_form()
                QMessageBox.information(self, "Éxito", "Descuento eliminado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error eliminando descuento: {e}")

    def reset_discount_form(self):
        """Limpia el formulario de descuentos"""
        self.discount_id.clear()
        self.discount_name.clear()
        self.discount_percentage.setValue(0)
        self.discount_type.setCurrentIndex(0)
        self.discount_min_amount.setValue(0)
        self.discount_active.setChecked(True)

    def preview_receipt(self):
        """Muestra vista previa del recibo"""
        QMessageBox.information(self, "Vista Previa", 
                              "Función de vista previa de recibo en desarrollo.")

    def save_receipt_template(self):
        """Guarda la plantilla de recibo"""
        template = self.receipt_template.toPlainText()
        if not template.strip():
            QMessageBox.warning(self, "Validación", "La plantilla no puede estar vacía.")
            return
        
        try:
            self.db.set_config('recibo_template', template)
            QMessageBox.information(self, "Éxito", "Plantilla guardada correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando plantilla: {e}")

    def restore_default_template(self):
        """Restaura la plantilla por defecto"""
        reply = QMessageBox.question(
            self, "Confirmar Restauración",
            "¿Restaurar la plantilla de recibo por defecto?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                default_template = self.get_default_receipt_template()
                self.receipt_template.setPlainText(default_template)
                QMessageBox.information(self, "Éxito", "Plantilla restaurada correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error restaurando plantilla: {e}")

    def get_default_receipt_template(self):
        """Retorna la plantilla de recibo por defecto"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Recibo {{numero_factura}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { text-align: center; margin-bottom: 20px; }
        .info { margin-bottom: 15px; }
        .items { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .items th, .items td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .total { text-align: right; font-weight: bold; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>{{empresa_nombre}}</h2>
        <p>RUC: {{empresa_ruc}}</p>
        <p>{{empresa_direccion}}</p>
    </div>
    
    <div class="info">
        <p><strong>Factura:</strong> {{numero_factura}}</p>
        <p><strong>Fecha:</strong> {{fecha}}</p>
        <p><strong>Cliente:</strong> {{cliente_nombre}}</p>
    </div>
    
    <table class="items">
        <thead>
            <tr>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Precio</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {{items}}
        </tbody>
    </table>
    
    <div class="total">
        <p>Subtotal: ${{subtotal}}</p>
        <p>IVA: ${{iva}}</p>
        <p><strong>Total: ${{total}}</strong></p>
    </div>
</body>
</html>"""

    def create_backup(self):
        """Crea un backup de la base de datos"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar Backup", 
                f"backup_erp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                "Database Files (*.db)"
            )
            
            if filename:
                # Copiar archivo de base de datos
                shutil.copy2('erp_database.db', filename)
                QMessageBox.information(self, "Backup Completado", 
                                      f"Backup guardado en:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creando backup: {e}")

    def restore_backup(self):
        """Restaura un backup de la base de datos"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar Backup", 
                "", "Database Files (*.db)"
            )
            
            if filename:
                reply = QMessageBox.warning(
                    self, "Confirmar Restauración",
                    "⚠️ ADVERTENCIA: Esta acción sobreescribirá la base de datos actual.\n\n"
                    "¿Está seguro de continuar?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Crear backup de la base actual antes de restaurar
                    backup_name = f"backup_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy2('erp_database.db', backup_name)
                    
                    # Restaurar backup
                    shutil.copy2(filename, 'erp_database.db')
                    
                    QMessageBox.information(self, "Restauración Completada", 
                                          "Base de datos restaurada correctamente.\n\n"
                                          f"Backup anterior guardado como: {backup_name}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error restaurando backup: {e}")

# Función para crear la tabla de configuración si no existe
def create_config_table(db):
    """Crea la tabla de configuración si no existe"""
    db.execute("""
        CREATE TABLE IF NOT EXISTS Configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT,
            descripcion TEXT,
            categoria TEXT,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insertar configuraciones por defecto
    default_configs = [
        ('empresa_nombre', 'Mi Empresa ERP', 'Nombre legal de la empresa', 'empresa'),
        ('empresa_ruc', '', 'RUC o NIT de la empresa', 'empresa'),
        ('empresa_direccion', '', 'Dirección fiscal', 'empresa'),
        ('empresa_telefono', '', 'Teléfono de contacto', 'empresa'),
        ('empresa_email', '', 'Email de contacto', 'empresa'),
        ('iva_por_defecto', '0.16', 'IVA por defecto para facturas', 'facturacion'),
        ('moneda', 'USD', 'Moneda principal del sistema', 'regional'),
        ('idioma', 'es', 'Idioma del sistema', 'regional'),
        ('zona_horaria', 'America/Mexico_City', 'Zona horaria', 'regional'),
    ]
    
    for clave, valor, descripcion, categoria in default_configs:
        db.execute("""
            INSERT OR IGNORE INTO Configuracion (clave, valor, descripcion, categoria)
            VALUES (?, ?, ?, ?)
        """, (clave, valor, descripcion, categoria))
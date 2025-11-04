"""
frames/products.py
Gestión completa de productos compatible con main.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QFormLayout, QMessageBox,
    QComboBox, QDoubleSpinBox, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import csv
import os

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

class StyledLineEdit(QLineEdit):
    """QLineEdit con estilo moderno"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(38)
        self.setStyleSheet("""
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

class StyledTextEdit(QTextEdit):
    """QTextEdit con estilo moderno"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(100)
        self.setStyleSheet("""
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

class ProductFrame(QWidget):
    """Frame moderno para gestión de productos - Compatible con main.py"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Tu main.py pasa 'app' como parámetro, pero lo necesitamos como parent
        self.app = parent
        if hasattr(parent, 'db'):
            self.db = parent.db
        else:
            # Fallback si no encuentra la db
            self.db = None
            
        self.current_product_id = None
        
        self.setup_ui()
        self.load_products()
        self.load_suppliers()

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
        
        # Panel izquierdo - Lista de productos
        list_panel = self.create_list_panel()
        splitter.addWidget(list_panel)
        
        # Panel derecho - Formulario
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
        
        title = QLabel("📦 Gestión de Productos")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1E293B;")
        
        subtitle = QLabel("Administre el inventario y catálogo de productos")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #64748B;")
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        layout.addLayout(title_section)
        layout.addStretch()
        
        # Botones de acción rápida
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        self.import_btn = AnimatedButton("📥 Importar CSV")
        self.import_btn.set_secondary_style()
        self.import_btn.clicked.connect(self.import_products)
        
        self.export_btn = AnimatedButton("📤 Exportar CSV")
        self.export_btn.set_secondary_style()
        self.export_btn.clicked.connect(self.export_products)
        
        action_layout.addWidget(self.import_btn)
        action_layout.addWidget(self.export_btn)
        
        layout.addLayout(action_layout)
        
        return layout

    def create_list_panel(self):
        """Crea el panel de lista de productos"""
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
        
        # Panel de búsqueda
        search_panel = self.create_search_panel()
        layout.addWidget(search_panel)
        
        # Título de la tabla
        table_title = QLabel("📋 Inventario de Productos")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        table_title.setStyleSheet("color: #1E293B;")
        layout.addWidget(table_title)
        
        # Tabla de productos
        self.products_table = ModernTableWidget()
        self.setup_products_table()
        layout.addWidget(self.products_table, 1)
        
        # Conectar señales
        self.products_table.doubleClicked.connect(self.on_product_double_click)
        self.search_input.textChanged.connect(self.filter_products)
        
        return panel

    def create_search_panel(self):
        """Crea el panel de búsqueda"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Búsqueda
        search_label = QLabel("🔍 Buscar:")
        search_label.setFont(QFont("Segoe UI", 11))
        search_label.setStyleSheet("color: #374151;")
        
        self.search_input = StyledLineEdit("Buscar productos por nombre...")
        
        layout.addWidget(search_label)
        layout.addWidget(self.search_input, 1)
        
        return panel

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
        form_title = QLabel("📝 Información del Producto")
        form_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        form_title.setStyleSheet("color: #1E293B; margin-bottom: 8px;")
        layout.addWidget(form_title)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Campos del formulario
        self.nombre_input = StyledLineEdit("Nombre del producto")
        
        # Precio con QDoubleSpinBox
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setMinimum(0.0)
        self.precio_input.setMaximum(999999.99)
        self.precio_input.setDecimals(2)
        self.precio_input.setPrefix("$ ")
        self.precio_input.setMinimumHeight(38)
        self.precio_input.setStyleSheet("""
            QDoubleSpinBox {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
            }
            QDoubleSpinBox:focus {
                border-color: #3B82F6;
                background: #F8FAFF;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: none;
                background: #F1F5F9;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background: #E2E8F0;
            }
        """)
        
        # Stock con QSpinBox
        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(999999)
        self.stock_input.setMinimumHeight(38)
        self.stock_input.setStyleSheet(self.precio_input.styleSheet())
        
        # Proveedor (ComboBox)
        self.proveedor_combo = QComboBox()
        self.proveedor_combo.setMinimumHeight(38)
        self.proveedor_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: #1E293B;
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
        
        # Descripción
        self.desc_input = StyledTextEdit()
        
        # Añadir campos al formulario
        form_layout.addRow("Nombre *:", self.nombre_input)
        form_layout.addRow("Precio *:", self.precio_input)
        form_layout.addRow("Stock *:", self.stock_input)
        form_layout.addRow("Proveedor *:", self.proveedor_combo)
        form_layout.addRow("Descripción:", self.desc_input)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.save_btn = AnimatedButton("💾 Guardar Producto")
        self.save_btn.set_primary_style()
        self.save_btn.clicked.connect(self.save_product)
        
        self.new_btn = AnimatedButton("🆕 Nuevo")
        self.new_btn.set_secondary_style()
        self.new_btn.clicked.connect(self.reset_form)
        
        self.delete_btn = AnimatedButton("🗑️ Eliminar")
        self.delete_btn.set_danger_style()
        self.delete_btn.clicked.connect(self.delete_product)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.new_btn)
        buttons_layout.addWidget(self.delete_btn)
        
        layout.addLayout(buttons_layout)
        
        return panel

    def setup_products_table(self):
        """Configura la tabla de productos"""
        headers = ["ID", "Nombre", "Precio", "Stock", "Proveedor"]
        self.products_table.setColumnCount(len(headers))
        self.products_table.setHorizontalHeaderLabels(headers)
        
        # Configurar anchos de columnas
        self.products_table.setColumnWidth(0, 60)   # ID
        self.products_table.setColumnWidth(1, 250)  # Nombre
        self.products_table.setColumnWidth(2, 100)  # Precio
        self.products_table.setColumnWidth(3, 80)   # Stock
        self.products_table.setColumnWidth(4, 120)  # Proveedor
        
        # Configurar header
        header = self.products_table.horizontalHeader()
        header.setStretchLastSection(True)

    def load_products(self):
        """Carga los productos desde la base de datos"""
        if not self.db:
            print("Error: No hay conexión a la base de datos")
            return
            
        try:
            products = self.db.fetch(
                """SELECT p.id, p.nombre, p.precio, p.stock, prov.nombre 
                   FROM Productos p 
                   LEFT JOIN Proveedores prov ON p.proveedor_id = prov.id 
                   ORDER BY p.id DESC"""
            )
            
            self.populate_products_table(products)
            
        except Exception as e:
            print(f"Error cargando productos: {e}")

    def load_suppliers(self):
        """Carga los proveedores para el ComboBox"""
        if not self.db:
            print("Error: No hay conexión a la base de datos")
            return
            
        try:
            suppliers = self.db.fetch("SELECT id, nombre FROM Proveedores ORDER BY nombre")
            self.proveedor_combo.clear()
            
            for supplier in suppliers:
                self.proveedor_combo.addItem(supplier[1], supplier[0])
                
        except Exception as e:
            print(f"Error cargando proveedores: {e}")

    def populate_products_table(self, products):
        """Llena la tabla con los datos de productos"""
        self.products_table.setRowCount(0)
        
        for product in products:
            row = self.products_table.rowCount()
            self.products_table.insertRow(row)
            
            # Crear items
            items = [
                QTableWidgetItem(str(product[0])),  # ID
                QTableWidgetItem(product[1]),       # Nombre
                QTableWidgetItem(f"${product[2]:.2f}"),  # Precio
                QTableWidgetItem(str(product[3])),  # Stock
                QTableWidgetItem(product[4] or "N/A")  # Proveedor
            ]
            
            # Resaltar stock bajo
            if product[3] <= 10:
                for item in items:
                    item.setForeground(QColor("#DC2626"))  # Rojo para stock bajo
            elif product[3] <= 20:
                for item in items:
                    item.setForeground(QColor("#F59E0B"))  # Amarillo para stock medio
            
            # Añadir items a la tabla
            for col, item in enumerate(items):
                self.products_table.setItem(row, col, item)

    def filter_products(self):
        """Filtra productos según búsqueda"""
        search_term = self.search_input.text().strip().lower()
        
        if not search_term:
            self.load_products()
            return
            
        try:
            products = self.db.fetch(
                """SELECT p.id, p.nombre, p.precio, p.stock, prov.nombre 
                   FROM Productos p 
                   LEFT JOIN Proveedores prov ON p.proveedor_id = prov.id 
                   WHERE LOWER(p.nombre) LIKE ? 
                   ORDER BY p.id DESC""",
                (f"%{search_term}%",)
            )
            
            self.populate_products_table(products)
            
        except Exception as e:
            print(f"Error filtrando productos: {e}")

    def on_product_double_click(self, index):
        """Maneja el doble click en la tabla"""
        row = index.row()
        product_id = int(self.products_table.item(row, 0).text())
        self.load_product_details(product_id)

    def load_product_details(self, product_id):
        """Carga los detalles de un producto en el formulario"""
        try:
            product = self.db.fetch(
                "SELECT nombre, precio, stock, descripcion, proveedor_id FROM Productos WHERE id = ?",
                (product_id,)
            )
            
            if product:
                product_data = product[0]
                
                # Llenar formulario
                self.nombre_input.setText(product_data[0])
                self.precio_input.setValue(float(product_data[1]))
                self.stock_input.setValue(int(product_data[2]))
                self.desc_input.setPlainText(product_data[3] or "")
                
                # Seleccionar proveedor
                supplier_id = product_data[4]
                index = self.proveedor_combo.findData(supplier_id)
                if index >= 0:
                    self.proveedor_combo.setCurrentIndex(index)
                
                self.current_product_id = product_id
                
        except Exception as e:
            print(f"Error cargando detalles del producto: {e}")

    def validate_form(self):
        """Valida los datos del formulario"""
        nombre = self.nombre_input.text().strip()
        
        if not nombre:
            self.show_error("Error de Validación", "El nombre del producto es obligatorio")
            self.nombre_input.setFocus()
            return False
            
        if self.precio_input.value() <= 0:
            self.show_error("Error de Validación", "El precio debe ser mayor a 0")
            self.precio_input.setFocus()
            return False
            
        if self.stock_input.value() < 0:
            self.show_error("Error de Validación", "El stock no puede ser negativo")
            self.stock_input.setFocus()
            return False
            
        if self.proveedor_combo.currentIndex() < 0:
            self.show_error("Error de Validación", "Seleccione un proveedor")
            self.proveedor_combo.setFocus()
            return False
            
        return True

    def save_product(self):
        """Guarda un nuevo producto o actualiza uno existente"""
        if not self.validate_form():
            return
            
        try:
            nombre = self.nombre_input.text().strip()
            precio = self.precio_input.value()
            stock = self.stock_input.value()
            descripcion = self.desc_input.toPlainText().strip()
            proveedor_id = self.proveedor_combo.currentData()
            
            if self.current_product_id:
                # Actualizar producto existente
                query = """
                    UPDATE Productos 
                    SET nombre=?, precio=?, stock=?, descripcion=?, proveedor_id=?
                    WHERE id=?
                """
                self.db.execute(
                    query,
                    (nombre, precio, stock, descripcion, proveedor_id, self.current_product_id)
                )
                self.show_success("Producto Actualizado", "Producto actualizado correctamente")
            else:
                # Crear nuevo producto
                query = """
                    INSERT INTO Productos (nombre, precio, stock, descripcion, proveedor_id)
                    VALUES (?, ?, ?, ?, ?)
                """
                self.db.execute(
                    query,
                    (nombre, precio, stock, descripcion, proveedor_id)
                )
                self.show_success("Producto Registrado", "Producto registrado correctamente")
            
            self.reset_form()
            self.load_products()
            
        except Exception as e:
            self.show_error("Error", f"Error al guardar producto: {e}")

    def delete_product(self):
        """Elimina el producto seleccionado"""
        if not self.current_product_id:
            self.show_warning("Advertencia", "Seleccione un producto para eliminar")
            return
            
        try:
            reply = self.show_question(
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar el producto '{self.nombre_input.text()}'?"
            )
            
            if reply == QMessageBox.Yes:
                self.db.execute("DELETE FROM Productos WHERE id = ?", (self.current_product_id,))
                self.show_success("Producto Eliminado", "Producto eliminado correctamente")
                self.reset_form()
                self.load_products()
                
        except Exception as e:
            self.show_error("Error", f"Error al eliminar producto: {e}")

    def reset_form(self):
        """Limpia el formulario"""
        self.nombre_input.clear()
        self.precio_input.setValue(0.0)
        self.stock_input.setValue(0)
        self.desc_input.clear()
        if self.proveedor_combo.count() > 0:
            self.proveedor_combo.setCurrentIndex(0)
        self.current_product_id = None
        
        # Limpiar selección en la tabla
        self.products_table.clearSelection()

    def import_products(self):
        """Importa productos desde CSV"""
        # Para compatibilidad con file_manager del main.py
        if hasattr(self.app, 'file_manager'):
            self.app.file_manager.import_products(self)
        else:
            self.show_info("Importar CSV", "Funcionalidad de importación CSV")

    def export_products(self):
        """Exporta productos a CSV"""
        # Para compatibilidad con file_manager del main.py
        if hasattr(self.app, 'file_manager'):
            self.app.file_manager.export_data("Productos")
        else:
            try:
                products = self.db.fetch(
                    "SELECT id, nombre, precio, stock, descripcion, proveedor_id FROM Productos"
                )
                self.show_info("Exportar CSV", 
                              f"Preparado para exportar {len(products)} productos a CSV")
            except Exception as e:
                self.show_error("Error", f"Error al exportar: {e}")

    def refresh_products(self):
        """Método público para refrescar la lista (compatibilidad)"""
        self.load_products()

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
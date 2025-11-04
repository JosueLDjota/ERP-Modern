import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QSpacerItem, QSizePolicy, QComboBox
)
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import Qt

# --- 1. Hoja de Estilo (QSS) para un Look Profesional y Claro (Material Design) ---
# Define un tema claro con acentos de púrpura/índigo, siguiendo el estilo de la imagen.
LIGHT_QSS = """
    QWidget {
        background-color: #f5f5f7; /* Fondo principal gris claro */
        color: #333333; /* Texto oscuro */
        font-family: 'Roboto', 'Segoe UI', sans-serif;
    }

    /* Estilo del Sidebar */
    #Sidebar {
        background-color: #ffffff; /* Sidebar blanco */
        border-right: 1px solid #e0e0e0;
        padding: 10px 0;
    }
    
    /* Botones de Navegación */
    QPushButton {
        background-color: transparent;
        border: none;
        padding: 10px 20px;
        text-align: left;
        font-size: 10pt;
        color: #555555;
        border-radius: 0; /* Sin bordes redondeados en sidebar */
    }
    QPushButton:hover {
        background-color: #eeeeee; /* Gris muy claro al pasar el ratón */
    }
    QPushButton:checked {
        background-color: #e8eaf6; /* Fondo azul claro para activo */
        color: #673ab7; /* Color de acento (Indigo) */
        font-weight: 500;
        border-left: 3px solid #673ab7;
    }
    
    /* Título de la Aplicación en la Sidebar */
    #AppHeader {
        font-size: 16pt;
        font-weight: 500;
        color: #333333;
        margin-bottom: 25px;
        padding: 0 20px;
    }
    
    /* Títulos de Grupo en Sidebar */
    .SidebarGroupTitle {
        font-size: 9pt;
        font-weight: 500;
        color: #9e9e9e;
        padding: 15px 20px 5px 20px;
        text-transform: uppercase;
    }
    
    /* Widgets de Tarjeta (General: KPI, Gráfico, etc.) */
    .Card {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* Sombra muy sutil */
        padding: 20px;
    }
    
    .KPICard {
        /* Estilo específico para los KPI, se aplicará .Card al contenedor */
    }
    .KPICard #kpiValue {
        color: #333333;
        font-size: 24pt;
        font-weight: 500;
    }
    .KPICard #kpiTitle {
        font-size: 10pt;
        color: #757575;
        font-weight: normal;
    }
    .KPICard #kpiChange {
        font-size: 10pt;
        color: #4caf50; /* Color de cambio positivo (verde) */
    }

    /* Placeholder de Título de Dashboard */
    #dashboardTitle {
        font-size: 24pt;
        font-weight: 400;
        color: #333333;
    }
    
    /* Área de Gráficos (Mockup) */
    #chartArea {
        min-height: 350px;
    }
    #chartArea QLabel {
        font-size: 14pt;
        color: #757575;
    }
    
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 5px;
        min-width: 120px;
    }
"""

# --- 2. Componente: Tarjeta de Indicador Clave de Rendimiento (KPI) ---
class KPICard(QWidget):
    def __init__(self, title, value, change, icon_color, icon_text, parent=None):
        super().__init__(parent)
        self.setObjectName("KPICard")
        
        # Envuelve el contenido en un QWidget con el estilo Card
        self.container = QWidget()
        self.container.setObjectName("Card")
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Contenedor para Icono, Valor y Título
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        # Texto/Título
        title_label = QLabel(title)
        title_label.setObjectName("kpiTitle")
        top_row.addWidget(title_label)
        top_row.addStretch()
        
        # Icono (Círculo de color)
        icon_circle = QLabel(icon_text)
        icon_circle.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        icon_circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_circle.setFixedSize(30, 30)
        icon_circle.setStyleSheet(f"background-color: {icon_color}; border-radius: 15px; color: white;")
        top_row.addWidget(icon_circle)

        layout.addLayout(top_row)
        
        # Valor
        value_label = QLabel(value)
        value_label.setObjectName("kpiValue")
        layout.addWidget(value_label)
        
        # Cambio
        change_label = QLabel(change)
        change_label.setObjectName("kpiChange")
        layout.addWidget(change_label)
        
        # Layout principal del KPICard para que el contenedor ocupe todo el espacio
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)


# --- 3. Componente: Sidebar de Navegación ---
class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo/Título del ERP
        logo = QLabel("MATERIAL ADMIN PRO")
        logo.setObjectName("AppHeader")
        layout.addWidget(logo)

        # --- Grupo INTERFACE ---
        layout.addWidget(self._create_group_title("INTERFACE"))
        self._create_nav_button(layout, "Overview", False)
        self._create_nav_button(layout, "Dashboards", True)
        self._create_nav_button(layout, "Analytics", False)
        self._create_nav_button(layout, "Accounting", False)
        
        # --- Grupo NEGOCIO ---
        layout.addWidget(self._create_group_title("NEGOCIO"))
        self._create_nav_button(layout, "Orders", False)
        self._create_nav_button(layout, "Projects", False)
        self._create_nav_button(layout, "Layouts", False)
        self._create_nav_button(layout, "Pages", False)

        # --- Grupo UI TOOLKIT ---
        layout.addWidget(self._create_group_title("UI TOOLKIT"))
        self._create_nav_button(layout, "Components", False)
        self._create_nav_button(layout, "Content", False)
        self._create_nav_button(layout, "Forms", False)
        self._create_nav_button(layout, "Utilities", False)

        # Espaciador
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Usuario Actual (Mockup)
        user_info = QLabel("Logged in as\nSmart Business App")
        user_info.setStyleSheet("font-size: 9pt; color: #757575; padding: 10px 20px;")
        layout.addWidget(user_info)

    def _create_group_title(self, text):
        title = QLabel(text)
        title.setObjectName("SidebarGroupTitle")
        return title

    def _create_nav_button(self, layout, text, is_checked=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_checked)
        layout.addWidget(btn)

# --- 4. Componente: Vista Principal del Dashboard ---
class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)

        # 1. Título y Filtros
        header_layout = QHBoxLayout()
        
        title = QLabel("Dashboard")
        title.setObjectName("dashboardTitle")
        subtitle = QLabel("Sales overview & summary")
        subtitle.setStyleSheet("font-size: 10pt; color: #757575;")
        
        # Contenedor para Título y Subtítulo
        title_container = QVBoxLayout()
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        title_container.setSpacing(0)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()

        # Filtros (Mockup)
        header_layout.addWidget(QLabel("View by:"))
        view_combo = QComboBox()
        view_combo.addItems(["Order type", "Product type"])
        header_layout.addWidget(view_combo)
        
        header_layout.addWidget(QLabel("Sale from:"))
        sale_combo = QComboBox()
        sale_combo.addItems(["Last year", "This year"])
        header_layout.addWidget(sale_combo)

        layout.addLayout(header_layout)

        # 2. Fila de Indicadores Clave (KPIs)
        kpi_layout = QHBoxLayout()
        
        # Colores de acento tomados de la imagen: Púrpura, Amarillo, Rojo, Turquesa
        kpi_layout.addWidget(KPICard("Downloads", "101.1K", "↓ 5% last month", "#673ab7", "⬇"))
        kpi_layout.addWidget(KPICard("Purchases", "12.2K", "↑ 2% last month", "#ffc107", "⬆"))
        kpi_layout.addWidget(KPICard("Customers", "5.3K", "↑ 7% last month", "#f44336", "👤"))
        kpi_layout.addWidget(KPICard("Channels", "7", "↑ 0.4% last month", "#00bcd4", "⚙️"))
        
        layout.addLayout(kpi_layout)

        # 3. Fila de Gráficos (Revenue Breakdown y Segments)
        chart_grid = QGridLayout()
        chart_grid.setHorizontalSpacing(25)
        
        # Revenue Breakdown (Gráfico de Barras Mockup)
        revenue_card = QWidget()
        revenue_card.setObjectName("Card")
        revenue_card_layout = QVBoxLayout(revenue_card)
        
        revenue_card_layout.addWidget(QLabel("Revenue Breakdown"), 0, Qt.AlignmentFlag.AlignTop)
        revenue_card_layout.addWidget(QLabel("Compared to previous year"), 0, Qt.AlignmentFlag.AlignTop)
        revenue_card_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # Mockup de Contenido de Gráfico
        graph_mockup = QLabel("$$$$ 59,402\n$ 50,000 Target\n119% YTD\n\nGRÁFICO DE BARRAS\n(Simulación de PySide6 QChart)")
        graph_mockup.setObjectName("chartArea")
        graph_mockup.setAlignment(Qt.AlignmentFlag.AlignCenter)
        revenue_card_layout.addWidget(graph_mockup)
        revenue_card_layout.addWidget(QPushButton("OPEN REPORT"), 0, Qt.AlignmentFlag.AlignRight)
        
        chart_grid.addWidget(revenue_card, 0, 0)

        # Segments (Gráfico Circular Mockup)
        segments_card = QWidget()
        segments_card.setObjectName("Card")
        segments_card_layout = QVBoxLayout(segments_card)
        
        segments_card_layout.addWidget(QLabel("Segments"), 0, Qt.AlignmentFlag.AlignTop)
        segments_card_layout.addWidget(QLabel("Revenue sources"), 0, Qt.AlignmentFlag.AlignTop)
        segments_card_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # Mockup de Contenido de Gráfico
        pie_mockup = QLabel("GRÁFICO CIRCULAR\n(Simulación de PySide6 QChart)")
        pie_mockup.setObjectName("chartArea")
        pie_mockup.setAlignment(Qt.AlignmentFlag.AlignCenter)
        segments_card_layout.addWidget(pie_mockup)
        segments_card_layout.addWidget(QPushButton("OPEN REPORT"), 0, Qt.AlignmentFlag.AlignRight)
        
        chart_grid.addWidget(segments_card, 0, 1)

        chart_grid.setColumnStretch(0, 2) # Revenue Breakdown más grande
        chart_grid.setColumnStretch(1, 1) # Segments más pequeño

        layout.addLayout(chart_grid)

        # 4. Fila de Tarjetas de Información
        bottom_row = QHBoxLayout()

        # Privacy Suggestions (Tarjeta de Información 1)
        privacy_card = QWidget()
        privacy_card.setObjectName("Card")
        privacy_layout = QHBoxLayout(privacy_card)
        privacy_layout.addWidget(QLabel("Privacy Suggestions\nTake our privacy checklist to choose which settings are right for you."))
        icon_label = QLabel("🔒")
        icon_label.setFont(QFont("Arial", 30))
        privacy_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignRight)
        bottom_row.addWidget(privacy_card, 1)

        # Account Storage (Tarjeta de Información 2)
        storage_card = QWidget()
        storage_card.setObjectName("Card")
        storage_layout = QHBoxLayout(storage_card)
        storage_layout.addWidget(QLabel("Account Storage\nYour account storage is shared across all devices\n18 GB of 30 GB used"))
        icon_label = QLabel("☁️")
        icon_label.setFont(QFont("Arial", 30))
        storage_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignRight)
        bottom_row.addWidget(storage_card, 1)

        layout.addLayout(bottom_row)
        layout.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)) # Empuja todo hacia arriba

    def _create_activity_item(self, text):
        # Esta función ya no se usa, pero la mantengo como placeholder si fuera necesaria
        item = QWidget()
        item.setObjectName("ActivityItem")
        layout = QHBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(text))
        layout.addWidget(QLabel("5m ago"), 0, Qt.AlignmentFlag.AlignRight)
        return item


# --- 5. Ventana Principal de la Aplicación ---
class ERPWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERP Avanzado | Panel Material Design")
        self.setGeometry(100, 100, 1400, 900) # Tamaño considerable

        # Aplicar Hoja de Estilo Global
        self.setStyleSheet(LIGHT_QSS)

        # Contenedor Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout Principal (Sidebar y Contenido)
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        # 1. Sidebar
        self.sidebar = Sidebar()
        main_h_layout.addWidget(self.sidebar)

        # 2. Contenido Principal
        self.main_content_area = QWidget()
        self.content_layout = QVBoxLayout(self.main_content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(DashboardView()) # Carga la vista por defecto (Dashboard)

        main_h_layout.addWidget(self.main_content_area)


# --- 6. Inicialización de la Aplicación ---
if __name__ == "__main__":
    # La aplicación de PySide6 necesita cargarse antes de crear la ventana
    app = QApplication(sys.argv)
    
    # El uso de QFontDatabase se deja comentado ya que puede fallar sin el recurso de fuente adecuado.
    # Usamos emojis y estilos para simular los iconos.
    # try:
    #     QFontDatabase.addApplicationFont(":/fonts/fontawesome-solid.otf")
    # except:
    #     pass

    window = ERPWindow()
    window.show()
    sys.exit(app.exec())

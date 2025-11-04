# frames/dashboard.py
"""
Dashboard Profesional Windows 11 Style
KPIs animados, gráficas interactivas, diseño fluido con efectos modernos
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, 
    QFrame, QSizePolicy, QToolTip, QGridLayout
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont, QLinearGradient, QColor, QPainter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import numpy as np
from datetime import datetime, timedelta

class AnimatedKPICard(QFrame):
    """Tarjeta KPI con animaciones y efectos hover profesionales"""
    
    def __init__(self, title, value, subtitle, color, icon, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.color = color
        self.icon = icon
        self._animation_progress = 0
        
        self.setFixedSize(280, 140)
        self.setStyleSheet("""
            AnimatedKPICard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
            AnimatedKPICard:hover {
                border: 1px solid #CBD5E1;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F1F5F9);
            }
        """)
        
        # Animación
        self.animation = QPropertyAnimation(self, b"animation_progress")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.setup_ui()
        
    def get_animation_progress(self):
        return self._animation_progress
        
    def set_animation_progress(self, value):
        self._animation_progress = value
        self.update()
        
    animation_progress = Property(float, get_animation_progress, set_animation_progress)
    
    def enterEvent(self, event):
        self.animation.setDirection(QPropertyAnimation.Forward)
        if self.animation.state() != QPropertyAnimation.Running:
            self.animation.setStartValue(self._animation_progress)
            self.animation.setEndValue(1.0)
            self.animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.animation.setDirection(QPropertyAnimation.Backward)
        if self.animation.state() != QPropertyAnimation.Running:
            self.animation.setStartValue(self._animation_progress)
            self.animation.setEndValue(0.0)
            self.animation.start()
        super().leaveEvent(event)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Header con icono y título
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setStyleSheet(f"color: {self.color};")
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet("color: #64748B; font-weight: 500;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Valor principal
        self.value_label = QLabel("0")
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {self.color};")
        
        # Subtitle
        subtitle_label = QLabel(self.subtitle)
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #94A3B8;")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()
        
        # Barra de progreso decorativa
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QFrame {{
                background: #E2E8F0;
                border-radius: 2px;
            }}
        """)
        layout.addWidget(self.progress_bar)
    
    def start_counter_animation(self, final_value, duration=1500):
        """Animación contador para valores numéricos"""
        try:
            if isinstance(final_value, (int, float)):
                self.animate_numeric_value(final_value, duration)
            else:
                self.value_label.setText(str(final_value))
        except:
            self.value_label.setText(str(final_value))
    
    def animate_numeric_value(self, final_value, duration):
        """Animar valor numérico con incremento gradual"""
        self.counter_timer = QTimer()
        self.counter_timer.timeout.connect(lambda: None)
        
        steps = 60
        interval = duration // steps
        step_value = final_value / steps
        current_value = 0
        
        def update_value():
            nonlocal current_value
            current_value += step_value
            if current_value >= final_value:
                self.value_label.setText(f"{final_value:,.0f}")
                self.counter_timer.stop()
            else:
                self.value_label.setText(f"{current_value:,.0f}")
        
        self.counter_timer.timeout.connect(update_value)
        self.counter_timer.start(interval)

class ModernChartWidget(QFrame):
    """Widget de gráfica moderna con estilo Windows 11"""
    
    def __init__(self, title, chart_type="line", parent=None):
        super().__init__(parent)
        self.title = title
        self.chart_type = chart_type
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            ModernChartWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #1E293B;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Canvas para la gráfica
        self.figure = Figure(figsize=(8, 4), dpi=100, facecolor='none')
        self.figure.set_facecolor('none')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: transparent;")
        self.canvas.setMinimumHeight(300)
        
        layout.addWidget(self.canvas)
    
    def create_line_chart(self, data, labels, color="#3B82F6"):
        """Crear gráfica de líneas moderna"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('none')
        
        # Estilo moderno
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E2E8F0')
        ax.spines['bottom'].set_color('#E2E8F0')
        
        # Gráfica de área con gradiente
        x = np.arange(len(data))
        line = ax.plot(x, data, color=color, linewidth=3, marker='o', markersize=6, 
                      markerfacecolor='white', markeredgecolor=color, markeredgewidth=2)[0]
        
        # Relleno con gradiente
        ax.fill_between(x, data, alpha=0.2, color=color)
        
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.tick_params(colors='#64748B')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        self.canvas.draw()
    
    def create_bar_chart(self, data, labels, colors=None):
        """Crear gráfica de barras moderna"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('none')
        
        # Colores por defecto
        if colors is None:
            colors = ['#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
        
        # Estilo moderno
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E2E8F0')
        ax.spines['bottom'].set_color('#E2E8F0')
        
        bars = ax.bar(range(len(data)), data, color=colors, alpha=0.8, 
                     edgecolor='white', linewidth=2)
        
        # Añadir valores en las barras
        for i, (bar, value) in enumerate(zip(bars, data)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(data)*0.01,
                   f'{value:,.0f}', ha='center', va='bottom', fontweight='bold', color='#1E293B')
        
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.tick_params(colors='#64748B')
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        self.canvas.draw()
    
    def create_pie_chart(self, data, labels, colors=None):
        """Crear gráfica circular moderna"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('none')
        
        if colors is None:
            colors = ['#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE']
        
        # Gráfica circular con efectos
        wedges, texts, autotexts = ax.pie(data, labels=labels, colors=colors, 
                                         autopct='%1.1f%%', startangle=90,
                                         wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        
        # Estilo de textos
        for text in texts:
            text.set_color('#1E293B')
            text.set_fontweight('500')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.axis('equal')
        self.canvas.draw()

class DashboardFrame(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.db = app.db
        
        # Configurar estilo
        self.setStyleSheet("background: #F8FAFC;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Área de scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(24)
        
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Cargar datos y renderizar
        self.load_data()
        self.render_dashboard()
        
        # Timer para actualizaciones automáticas
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_data)
        self.auto_refresh_timer.start(30000)  # Actualizar cada 30 segundos

    def load_data(self):
        """Cargar datos para el dashboard"""
        try:
            # Ventas
            self.total_sales = self.db.fetch("SELECT SUM(total) FROM Ventas")[0][0] or 0
            self.daily_sales = self.db.fetch("SELECT SUM(total) FROM Ventas WHERE DATE(fecha)=DATE('now')")[0][0] or 0
            self.monthly_sales = self.db.fetch("SELECT SUM(total) FROM Ventas WHERE strftime('%m', fecha)=strftime('%m','now')")[0][0] or 0
            
            # Productos e inventario
            self.low_stock = self.db.fetch("SELECT nombre, stock FROM Productos WHERE stock <= 10 ORDER BY stock ASC")
            self.total_products = self.db.fetch("SELECT COUNT(*) FROM Productos")[0][0] or 0
            self.out_of_stock = self.db.fetch("SELECT COUNT(*) FROM Productos WHERE stock = 0")[0][0] or 0
            
            # Mejor producto
            best_seller_data = self.db.fetch("""
                SELECT nombre_producto, SUM(cantidad)
                FROM DetalleVenta
                GROUP BY nombre_producto
                ORDER BY SUM(cantidad) DESC
                LIMIT 1
            """)
            self.best_seller = best_seller_data[0] if best_seller_data else ("Ninguno", 0)
            
            # Datos para gráficas
            self.ventas_por_mes = self.db.fetch("""
                SELECT strftime('%m', fecha), SUM(total)
                FROM Ventas
                GROUP BY strftime('%m', fecha)
                ORDER BY strftime('%m', fecha)
            """) or []
            
            self.ventas_por_dia = self.db.fetch("""
                SELECT strftime('%d', fecha), SUM(total)
                FROM Ventas
                WHERE strftime('%m', fecha)=strftime('%m','now')
                GROUP BY strftime('%d', fecha)
                ORDER BY strftime('%d', fecha)
            """) or []
            
            # Clientes
            self.total_clients = self.db.fetch("SELECT COUNT(*) FROM Clientes")[0][0] or 0
            self.new_clients_month = self.db.fetch("""
                SELECT COUNT(*) FROM Clientes 
                WHERE strftime('%m', fecha_registro)=strftime('%m','now')
            """)[0][0] or 0
            
        except Exception as e:
            print(f"Error cargando datos del dashboard: {e}")
            # Valores por defecto en caso de error
            self.total_sales = 0
            self.daily_sales = 0
            self.monthly_sales = 0
            self.low_stock = []
            self.total_products = 0
            self.out_of_stock = 0
            self.best_seller = ("N/A", 0)
            self.ventas_por_mes = []
            self.ventas_por_dia = []
            self.total_clients = 0
            self.new_clients_month = 0

    def render_dashboard(self):
        """Renderizar interfaz del dashboard"""
        # Título principal
        title_section = self.create_title_section()
        self.content_layout.addLayout(title_section)
        
        # Sección de KPIs principales
        kpi_section = self.create_kpi_section()
        self.content_layout.addLayout(kpi_section)
        
        # Sección de gráficas
        charts_section = self.create_charts_section()
        self.content_layout.addLayout(charts_section)
        
        # Sección inferior (alertas y acciones rápidas)
        bottom_section = self.create_bottom_section()
        self.content_layout.addLayout(bottom_section)
        
        self.content_layout.addStretch()

    def create_title_section(self):
        """Crear sección de título y controles"""
        layout = QHBoxLayout()
        
        # Título y subtítulo
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel("Panel de Control")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #1E293B;")
        
        subtitle = QLabel("Resumen ejecutivo y métricas clave del negocio")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #64748B;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Botones de acción
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedSize(120, 36)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, stop:1 #60A5FA);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563EB, stop:1 #3B82F6);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_dashboard)
        
        export_btn = QPushButton("📊 Exportar")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setFixedSize(120, 36)
        export_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                color: #64748B;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #F1F5F9;
                border-color: #CBD5E1;
            }
        """)
        
        action_layout.addWidget(refresh_btn)
        action_layout.addWidget(export_btn)
        
        layout.addLayout(action_layout)
        
        return layout

    def create_kpi_section(self):
        """Crear sección de KPIs con tarjetas animadas"""
        layout = QGridLayout()
        layout.setSpacing(16)
        
        # Definir KPIs
        kpis = [
            ("💰", "Ventas Totales", f"${self.total_sales:,.0f}", "Ingresos acumulados", "#10B981"),
            ("📈", "Ventas Mensuales", f"${self.monthly_sales:,.0f}", "Total del mes actual", "#3B82F6"),
            ("🎯", "Ventas Diarias", f"${self.daily_sales:,.0f}", "Ingresos de hoy", "#F59E0B"),
            ("📦", "Total Productos", f"{self.total_products}", "En inventario", "#8B5CF6"),
            ("⚠️", "Stock Bajo", f"{len(self.low_stock)}", "Productos críticos", "#EF4444"),
            ("👑", "Producto Top", f"{self.best_seller[1]}", f"{self.best_seller[0][:15]}...", "#06B6D4"),
            ("👥", "Total Clientes", f"{self.total_clients}", "Clientes registrados", "#84CC16"),
            ("🆕", "Clientes Nuevos", f"{self.new_clients_month}", "Este mes", "#F97316")
        ]
        
        # Crear tarjetas KPI
        for i, (icon, title, value, subtitle, color) in enumerate(kpis):
            row = i // 4
            col = i % 4
            card = AnimatedKPICard(title, value, subtitle, color, icon)
            card.start_counter_animation(self.get_numeric_value(value))
            layout.addWidget(card, row, col)
        
        return layout

    def create_charts_section(self):
        """Crear sección de gráficas"""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Gráfica de ventas mensuales
        if self.ventas_por_mes:
            chart1 = ModernChartWidget("📈 Tendencia de Ventas Mensuales")
            meses = [f"Mes {d[0]}" for d in self.ventas_por_mes]
            ventas = [d[1] for d in self.ventas_por_mes]
            chart1.create_line_chart(ventas, meses)
            layout.addWidget(chart1, 2)
        
        # Gráfica de productos con stock bajo
        if self.low_stock:
            chart2 = ModernChartWidget("🚨 Alertas de Stock")
            productos = [d[0][:15] + "..." for d in self.low_stock]
            stocks = [d[1] for d in self.low_stock]
            chart2.create_bar_chart(stocks, productos)
            layout.addWidget(chart2, 1)
        else:
            # Gráfica alternativa si no hay stock bajo
            chart2 = ModernChartWidget("📊 Distribución de Ventas")
            # Datos de ejemplo para gráfica circular
            chart2.create_pie_chart([40, 30, 20, 10], ['Electrónicos', 'Ropa', 'Hogar', 'Otros'])
            layout.addWidget(chart2, 1)
        
        return layout

    def create_bottom_section(self):
        """Crear sección inferior con alertas y acciones"""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Panel de alertas
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        alerts_frame.setFixedWidth(400)
        
        alerts_layout = QVBoxLayout(alerts_frame)
        alerts_layout.setContentsMargins(20, 16, 20, 16)
        
        alerts_title = QLabel("🚨 Alertas y Notificaciones")
        alerts_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        alerts_title.setStyleSheet("color: #1E293B; margin-bottom: 12px;")
        alerts_layout.addWidget(alerts_title)
        
        # Alertas dinámicas
        alerts = []
        if len(self.low_stock) > 0:
            alerts.append(f"• {len(self.low_stock)} productos con stock bajo")
        if self.out_of_stock > 0:
            alerts.append(f"• {self.out_of_stock} productos agotados")
        if self.daily_sales == 0:
            alerts.append("• No hay ventas registradas hoy")
        
        if alerts:
            for alert in alerts:
                alert_label = QLabel(alert)
                alert_label.setStyleSheet("color: #DC2626; font-size: 12px; padding: 4px 0;")
                alerts_layout.addWidget(alert_label)
        else:
            no_alerts = QLabel("✅ Todo en orden")
            no_alerts.setStyleSheet("color: #10B981; font-size: 12px; padding: 4px 0;")
            alerts_layout.addWidget(no_alerts)
        
        alerts_layout.addStretch()
        layout.addWidget(alerts_frame)
        
        # Panel de acciones rápidas
        actions_frame = QFrame()
        actions_frame.setStyleSheet(alerts_frame.styleSheet())
        
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(20, 16, 20, 16)
        
        actions_title = QLabel("⚡ Acciones Rápidas")
        actions_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        actions_title.setStyleSheet("color: #1E293B; margin-bottom: 12px;")
        actions_layout.addWidget(actions_title)
        
        # Botones de acción rápida
        quick_actions = [
            ("➕ Nueva Venta", "Ir al módulo de ventas POS"),
            ("📦 Gestionar Inventario", "Revisar y actualizar productos"),
            ("👥 Administrar Clientes", "Gestionar base de clientes"),
            ("📊 Generar Reporte", "Exportar reporte ejecutivo")
        ]
        
        for action, desc in quick_actions:
            btn = QPushButton(action)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: 1.5px solid #E2E8F0;
                    border-radius: 8px;
                    color: #475569;
                    font-weight: 500;
                    text-align: left;
                    padding: 0 16px;
                }
                QPushButton:hover {
                    background: #F1F5F9;
                    border-color: #CBD5E1;
                }
            """)
            btn.setToolTip(desc)
            actions_layout.addWidget(btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_frame)
        
        return layout

    def get_numeric_value(self, value_str):
        """Extraer valor numérico de string formateado"""
        try:
            if value_str.startswith('$'):
                return float(value_str.replace('$', '').replace(',', ''))
            else:
                return int(value_str)
        except:
            return 0

    def refresh_data(self):
        """Actualizar datos sin recargar toda la interfaz"""
        self.load_data()
        # Aquí se podrían agregar actualizaciones específicas de componentes

    def refresh_dashboard(self):
        """Recargar completamente el dashboard"""
        # Limpiar layout actual
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item.layout():
                self.clear_layout(item.layout())
            elif item.widget():
                item.widget().deleteLater()
        
        # Recargar y renderizar
        self.load_data()
        self.render_dashboard()

    def clear_layout(self, layout):
        """Limpiar layout recursivamente"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
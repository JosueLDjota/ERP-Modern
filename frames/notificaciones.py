# -*- coding: utf-8 -*-
"""
notificaciones.py
Sistema de notificaciones avanzado estilo Windows 11 para ERP (PySide6)
- Notificaciones flotantes animadas con diseño moderno
- Centro de notificaciones completo
- Gestión de cola y límites
- Configuración persistente
- Efectos visuales profesionales
"""

from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget,
    QProgressBar, QApplication, QFrame, QTabWidget, QTextEdit, QCheckBox,
    QScrollArea, QGroupBox, QGridLayout, QMessageBox, QListWidget, QListWidgetItem,
    QSplitter, QToolBar, QStatusBar, QComboBox, QSpinBox, QSlider
)
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, Signal, QObject, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QIcon
from datetime import datetime, timedelta
import typing
import json
import os

class AnimatedButton(QPushButton):
    """Botón con animaciones suaves al estilo Windows 11"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)

class NotificationManager(QObject):
    """Administra la cola de notificaciones y el centro de notificaciones."""
    
    notification_shown = Signal(dict)
    config_changed = Signal()

    def __init__(self, parent: QWidget, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.db = db_manager

        self.notification_widgets: typing.List[NotificationWidget] = []
        self.notification_history: typing.List[dict] = []
        self.notification_queue: typing.List[typing.Tuple[dict, int]] = []
        self.is_animating = False
        self.max_notifications = 5
        self.notification_duration = 5000  # ms

        # Configuración por defecto
        self.config = {
            "stock_alerts": True,
            "sales_alerts": True,
            "login_alerts": True,
            "system_alerts": True,
            "sound_enabled": False,
            "auto_clear_days": 30,
            "position": "top-right",
            "animation_style": "slide"
        }

        # Cargar configuración guardada
        self.load_config()

        # Temporizador para verificar stock
        self.stock_check_timer = QTimer(self.parent)
        self.stock_check_timer.setInterval(300000)  # 5 minutos
        self.stock_check_timer.timeout.connect(self.check_stock_alerts)

        # Temporizador para limpieza automática
        self.auto_clean_timer = QTimer(self.parent)
        self.auto_clean_timer.setInterval(3600000)  # 1 hora
        self.auto_clean_timer.timeout.connect(self.auto_clean_history)

    def load_config(self):
        """Carga la configuración desde archivo"""
        try:
            config_path = "notification_config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except Exception:
            pass

    def save_config(self):
        """Guarda la configuración en archivo"""
        try:
            config_path = "notification_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.config_changed.emit()
        except Exception:
            pass

    # ---------------- Métodos de notificación ----------------
    def show_notification(self, title: str, message: str, type_: str = "info",
                          duration: typing.Optional[int] = None,
                          action_callback: typing.Callable = None,
                          action_data=None,
                          icon: str = "🔔"):
        """Muestra una notificación con estilo Windows 11"""
        duration = duration or self.notification_duration
        data = {
            "title": title,
            "message": message,
            "type": type_,
            "timestamp": datetime.now(),
            "action_callback": action_callback,
            "action_data": action_data,
            "icon": icon,
            "read": False
        }

        # Guardar en historial
        self.notification_history.insert(0, data)
        if len(self.notification_history) > 200:
            self.notification_history.pop()

        # Encolar y mostrar
        self.notification_queue.append((data, duration))
        if not self.is_animating:
            self.show_next_notification()

    def show_next_notification(self):
        """Muestra la siguiente notificación en cola"""
        if not self.notification_queue:
            self.is_animating = False
            return

        if len(self.notification_widgets) >= self.max_notifications:
            QTimer.singleShot(500, self.show_next_notification)
            return

        self.is_animating = True
        data, duration = self.notification_queue.pop(0)

        notif = NotificationWidget(self.parent, data, duration, self._on_widget_closed)
        self.notification_widgets.append(notif)
        self.reposition_notifications()
        self.notification_shown.emit(data)

        QTimer.singleShot(150, lambda: setattr(self, "is_animating", False) or self.show_next_notification())

    def _on_widget_closed(self, widget: "NotificationWidget"):
        """Callback cuando se cierra una notificación"""
        if widget in self.notification_widgets:
            try:
                self.notification_widgets.remove(widget)
            except ValueError:
                pass
        self.reposition_notifications()

    def reposition_notifications(self):
        """Reposiciona las notificaciones en pantalla"""
        screen_geom = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geom.width()
        screen_height = screen_geom.height()
        
        position = self.config.get("position", "top-right")
        
        if position == "top-right":
            start_x = screen_width - 380
            start_y = 80
            spacing = 10
        elif position == "bottom-right":
            start_x = screen_width - 380
            start_y = screen_height - 150
            spacing = -10
        else:  # top-left
            start_x = 20
            start_y = 80
            spacing = 10

        y = start_y
        for w in self.notification_widgets:
            w.animate_to(start_x, y)
            y += (w.height + spacing) * (1 if spacing > 0 else -1)

    # ---------------- Notificaciones específicas ----------------
    def check_stock_alerts(self):
        """Verifica y notifica sobre stock bajo"""
        if not self.config.get("stock_alerts", True):
            return
        try:
            rows = self.db.fetch("""
                SELECT nombre, stock, stock_minimo 
                FROM Productos 
                WHERE stock <= stock_minimo AND stock_minimo > 0
                OR stock <= 10
            """)
        except Exception:
            rows = []
            
        for nombre, stock, stock_minimo in rows:
            self.show_notification(
                "⚠️ Stock Crítico",
                f"Producto: {nombre}\nStock actual: {stock}\nStock mínimo: {stock_minimo}",
                type_="warning",
                duration=6000,
                action_callback=self.open_low_stock_product,
                action_data=nombre,
                icon="📦"
            )

    def open_low_stock_product(self, product_name):
        """Abre el módulo de productos para stock bajo"""
        QMessageBox.information(
            self.parent,
            "Producto con Stock Bajo",
            f"El producto '{product_name}' tiene stock bajo. Por favor, actualice el inventario."
        )
        
        if hasattr(self.parent, "show_frame"):
            try:
                self.parent.show_frame("Productos")
            except Exception:
                pass

    def notify_login(self, username, role):
        """Notificación de inicio de sesión"""
        if self.config.get("login_alerts", True):
            self.show_notification(
                "👋 Sesión Iniciada",
                f"Bienvenido {username}\nRol: {role}\n{datetime.now().strftime('%d/%m/%Y %H:%M')}",
                type_="success",
                duration=4000,
                icon="🔐"
            )

    def notify_sale_success(self, venta_id, total, cliente=None):
        """Notificación de venta exitosa"""
        if self.config.get("sales_alerts", True):
            cliente_text = f"Cliente: {cliente}\n" if cliente else ""
            self.show_notification(
                "💰 Venta Exitosa",
                f"{cliente_text}Venta #: {venta_id}\nTotal: ${total:.2f}",
                type_="success",
                duration=5000,
                icon="💳"
            )

    def notify_sale_cancelled(self, motivo=""):
        """Notificación de venta cancelada"""
        if self.config.get("sales_alerts", True):
            motivo_text = f"\nMotivo: {motivo}" if motivo else ""
            self.show_notification(
                "❌ Venta Cancelada",
                f"La venta fue cancelada{motivo_text}",
                type_="error",
                duration=4000,
                icon="🚫"
            )

    def notify_system_info(self, app_version: str):
        """Notificación de información del sistema"""
        if self.config.get("system_alerts", True):
            self.show_notification(
                "🚀 Sistema ERP Iniciado",
                f"Versión: {app_version}\nSistema listo para operar\n{datetime.now().strftime('%d/%m/%Y %H:%M')}",
                type_="info",
                duration=5000,
                icon="⚙️"
            )

    def notify_backup_completed(self, filename: str):
        """Notificación de backup completado"""
        self.show_notification(
            "💾 Backup Completado",
            f"Respaldo guardado como:\n{filename}",
            type_="success",
            duration=4000,
            icon="🛡️"
        )

    def notify_error(self, title: str, message: str):
        """Notificación de error genérico"""
        self.show_notification(
            f"❌ {title}",
            message,
            type_="error",
            duration=6000,
            icon="⚠️"
        )

    def auto_clean_history(self):
        """Limpia automáticamente el historial antiguo"""
        auto_clear_days = self.config.get("auto_clear_days", 30)
        cutoff_date = datetime.now() - timedelta(days=auto_clear_days)
        
        self.notification_history = [
            notif for notif in self.notification_history 
            if notif['timestamp'] > cutoff_date
        ]

    def show_notification_center(self):
        """Muestra el centro de notificaciones"""
        dlg = NotificationCenter(self.parent, self)
        dlg.exec()

    def get_unread_count(self):
        """Retorna el número de notificaciones no leídas"""
        return sum(1 for notif in self.notification_history if not notif.get('read', False))

    def mark_all_as_read(self):
        """Marca todas las notificaciones como leídas"""
        for notif in self.notification_history:
            notif['read'] = True

    def handle_notification_click(self, notif: dict):
        """Maneja el click en una notificación del historial"""
        notif['read'] = True
        callback = notif.get("action_callback")
        data = notif.get("action_data")
        if callable(callback):
            try:
                callback(data) if data is not None else callback()
            except Exception:
                pass

class NotificationWidget(QDialog):
    """Widget de notificación flotante estilo Windows 11"""
    closed = Signal(object)

    def __init__(self, parent: QWidget, data: dict, duration: int, close_callback: typing.Callable):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setModal(False)

        self.parent_widget = parent
        self.data = data
        self.duration = duration
        self.close_callback = close_callback

        # Tamaño fijo
        self.width = 360
        self.height = 120
        self.resize(self.width, self.height)

        # Esquema de colores Windows 11
        self.colors = {
            "info": {"bg": "#0f62fe", "fg": "#ffffff", "accent": "#4589ff"},
            "success": {"bg": "#198038", "fg": "#ffffff", "accent": "#42be65"},
            "warning": {"bg": "#ff832b", "fg": "#ffffff", "accent": "#ff832b"},
            "error": {"bg": "#da1e28", "fg": "#ffffff", "accent": "#fa4d56"},
        }
        self.color_scheme = self.colors.get(data.get("type", "info"), self.colors["info"])

        # Construir UI
        self._build_ui()

        # Posición inicial
        screen_geom = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geom.width()
        start_x = screen_width
        start_y = 80
        self.move(int(start_x), int(start_y))
        self.current_x = start_x
        self.current_y = start_y

        # Animaciones
        self.anim = QPropertyAnimation(self, b"pos", self)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setDuration(400)

        # Barra de progreso
        self.progress_value = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(50)
        self.progress_timer.timeout.connect(self._update_progress)
        steps = max(1, int(self.duration / 50))
        self.progress_step = 100.0 / steps

        # Hacer clickeable si tiene acción
        if callable(self.data.get("action_callback")):
            self.setCursor(Qt.PointingHandCursor)

        # Mostrar y animar
        self.show()
        self._animate_in()
        self.progress_timer.start()

        # Auto-cierre
        QTimer.singleShot(self.duration, self.close)

    def _build_ui(self):
        """Construye la interfaz de la notificación"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Marco principal con sombra y bordes redondeados
        container = QFrame()
        container.setObjectName("notification")
        container.setFixedSize(self.width, self.height)
        container.setStyleSheet(f"""
            #notification {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.color_scheme['bg']}, stop:1 {self.color_scheme['accent']});
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 12, 12, 8)
        container_layout.setSpacing(8)

        # Header con icono, título y botón cerrar
        header_layout = QHBoxLayout()
        
        # Icono
        icon_label = QLabel(self.data.get("icon", "🔔"))
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        icon_label.setStyleSheet("color: white;")
        
        # Título
        title_label = QLabel(self.data.get("title", ""))
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        # Espacio
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Botón cerrar
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
        """)
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(close_btn)
        container_layout.addLayout(header_layout)

        # Mensaje
        message_label = QLabel(self.data.get("message", ""))
        message_label.setFont(QFont("Segoe UI", 10))
        message_label.setStyleSheet("color: white; line-height: 1.4;")
        message_label.setWordWrap(True)
        message_label.setFixedHeight(40)
        container_layout.addWidget(message_label)

        # Footer con tiempo y progreso
        footer_layout = QHBoxLayout()
        
        # Tiempo
        time_label = QLabel(self.data.get("timestamp").strftime("%H:%M"))
        time_label.setFont(QFont("Segoe UI", 9))
        time_label.setStyleSheet("color: rgba(255,255,255,0.8);")
        
        footer_layout.addWidget(time_label)
        footer_layout.addStretch()
        
        container_layout.addLayout(footer_layout)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 1px;
            }
            QProgressBar::chunk {
                background: white;
                border-radius: 1px;
            }
        """)
        container_layout.addWidget(self.progress_bar)

        layout.addWidget(container)

    def _animate_in(self):
        """Animación de entrada"""
        screen_geom = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geom.width()
        target_x = screen_width - self.width - 20
        
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(int(target_x), int(self.current_y)))
        self.anim.start()
        self.current_x = target_x

    def animate_to(self, target_x: int, target_y: int):
        """Anima a nueva posición"""
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(int(target_x), int(target_y)))
        self.anim.start()
        self.current_x = target_x
        self.current_y = target_y

    def _update_progress(self):
        """Actualiza la barra de progreso"""
        self.progress_value += self.progress_step
        if self.progress_value >= 100:
            self.progress_bar.setValue(100)
            self.progress_timer.stop()
        else:
            self.progress_bar.setValue(int(self.progress_value))

    def mousePressEvent(self, event):
        """Maneja clicks en la notificación"""
        if callable(self.data.get("action_callback")):
            callback = self.data.get("action_callback")
            action_data = self.data.get("action_data")
            try:
                callback(action_data) if action_data is not None else callback()
            except Exception:
                pass
        self.close()
        super().mousePressEvent(event)

    def closeEvent(self, event):
        """Maneja el cierre de la notificación"""
        self.close_callback(self)
        event.accept()

class NotificationCenter(QDialog):
    """Centro de notificaciones estilo Windows 11"""
    
    def __init__(self, parent: QWidget, manager: NotificationManager):
        super().__init__(parent)
        self.manager = manager
        self.setup_ui()
        self.load_notifications()

    def setup_ui(self):
        """Configura la interfaz del centro de notificaciones"""
        self.setWindowTitle("Centro de Notificaciones")
        self.resize(800, 600)
        self.setMinimumSize(700, 500)
        
        # Estilo principal
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F8FAFC, stop:1 #FFFFFF);
            }
            QListWidget {
                background: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #F1F5F9;
                padding: 12px;
            }
            QListWidget::item:selected {
                background: #DBEAFE;
            }
            QListWidget::item:hover {
                background: #F1F5F9;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🔔 Centro de Notificaciones")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1E293B;")
        
        self.unread_badge = QLabel(f"{self.manager.get_unread_count()} no leídas")
        self.unread_badge.setFont(QFont("Segoe UI", 11))
        self.unread_badge.setStyleSheet("""
            QLabel {
                background: #3B82F6;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: 600;
            }
        """)
        self.unread_badge.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.unread_badge)
        
        main_layout.addLayout(header_layout)

        # Contenido principal con tabs
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
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
            }
        """)
        
        # Tab de notificaciones
        self.notif_tab = self.create_notifications_tab()
        self.tabs.addTab(self.notif_tab, "Todas las Notificaciones")
        
        # Tab de configuración
        self.config_tab = self.create_config_tab()
        self.tabs.addTab(self.config_tab, "Configuración")
        
        main_layout.addWidget(self.tabs)

        # Footer con botones
        footer_layout = QHBoxLayout()
        
        self.mark_read_btn = AnimatedButton("📝 Marcar Todas como Leídas")
        self.mark_read_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                color: #475569;
                font-weight: 500;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #F1F5F9;
            }
        """)
        self.mark_read_btn.clicked.connect(self.mark_all_read)
        
        self.clear_btn = AnimatedButton("🗑️ Limpiar Historial")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1.5px solid #FECACA;
                border-radius: 8px;
                color: #DC2626;
                font-weight: 500;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #FEF2F2;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_history)
        
        self.close_btn = AnimatedButton("Cerrar")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                padding: 8px 24px;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        footer_layout.addWidget(self.mark_read_btn)
        footer_layout.addWidget(self.clear_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(footer_layout)

    def create_notifications_tab(self):
        """Crea el tab de listado de notificaciones"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Lista de notificaciones
        self.notif_list = QListWidget()
        self.notif_list.itemDoubleClicked.connect(self.on_notification_click)
        
        layout.addWidget(self.notif_list)
        
        return widget

    def create_config_tab(self):
        """Crea el tab de configuración"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Grupo de configuraciones
        config_group = QGroupBox("⚙️ Configuración de Notificaciones")
        config_group.setStyleSheet("""
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
        """)
        
        config_layout = QVBoxLayout(config_group)
        
        # Checkboxes de configuración
        self.stock_cb = QCheckBox("Alertas de stock bajo")
        self.stock_cb.setChecked(self.manager.config.get("stock_alerts", True))
        
        self.sales_cb = QCheckBox("Notificaciones de ventas")
        self.sales_cb.setChecked(self.manager.config.get("sales_alerts", True))
        
        self.login_cb = QCheckBox("Notificaciones de inicio de sesión")
        self.login_cb.setChecked(self.manager.config.get("login_alerts", True))
        
        self.system_cb = QCheckBox("Notificaciones del sistema")
        self.system_cb.setChecked(self.manager.config.get("system_alerts", True))
        
        # Posición de notificaciones
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Posición:"))
        self.position_combo = QComboBox()
        self.position_combo.addItems(["Arriba-Derecha", "Abajo-Derecha", "Arriba-Izquierda"])
        current_pos = self.manager.config.get("position", "top-right")
        index = {"top-right": 0, "bottom-right": 1, "top-left": 2}.get(current_pos, 0)
        self.position_combo.setCurrentIndex(index)
        
        position_layout.addWidget(self.position_combo)
        position_layout.addStretch()
        
        # Duración
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duración (segundos):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(3, 30)
        self.duration_spin.setValue(self.manager.notification_duration // 1000)
        duration_layout.addWidget(self.duration_spin)
        duration_layout.addStretch()
        
        # Botón guardar configuración
        save_btn = AnimatedButton("💾 Guardar Configuración")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #10B981;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                padding: 10px 20px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        save_btn.clicked.connect(self.save_config)
        
        # Botón de prueba
        test_btn = AnimatedButton("🧪 Probar Notificación")
        test_btn.setStyleSheet("""
            QPushButton {
                background: #8B5CF6;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                padding: 10px 20px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background: #7C3AED;
            }
        """)
        test_btn.clicked.connect(self.test_notification)
        
        config_layout.addWidget(self.stock_cb)
        config_layout.addWidget(self.sales_cb)
        config_layout.addWidget(self.login_cb)
        config_layout.addWidget(self.system_cb)
        config_layout.addLayout(position_layout)
        config_layout.addLayout(duration_layout)
        config_layout.addWidget(save_btn)
        config_layout.addWidget(test_btn)
        config_layout.addStretch()
        
        layout.addWidget(config_group)
        layout.addStretch()
        
        return widget

    def load_notifications(self):
        """Carga las notificaciones en la lista"""
        self.notif_list.clear()
        
        for notif in self.manager.notification_history:
            item = QListWidgetItem()
            widget = self.create_notification_item(notif)
            item.setSizeHint(widget.sizeHint())
            self.notif_list.addItem(item)
            self.notif_list.setItemWidget(item, widget)

    def create_notification_item(self, notif):
        """Crea un widget de item de notificación"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Icono
        icon_label = QLabel(notif.get("icon", "🔔"))
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        
        # Contenido
                # Contenido
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        title_label = QLabel(notif.get("title", ""))
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: #1E293B;")
        
        message_label = QLabel(notif.get("message", ""))
        message_label.setFont(QFont("Segoe UI", 10))
        message_label.setStyleSheet("color: #64748B;")
        message_label.setWordWrap(True)
        message_label.setMaximumHeight(40)
        
        time_label = QLabel(notif.get("timestamp").strftime("%d/%m/%Y %H:%M"))
        time_label.setFont(QFont("Segoe UI", 9))
        time_label.setStyleSheet("color: #94A3B8;")
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(message_label)
        content_layout.addWidget(time_label)
        
        # Indicador de no leído
        if not notif.get('read', False):
            unread_indicator = QLabel("●")
            unread_indicator.setFont(QFont("Segoe UI", 12))
            unread_indicator.setStyleSheet("color: #3B82F6;")
            unread_indicator.setAlignment(Qt.AlignCenter)
            unread_indicator.setFixedSize(20, 20)
        else:
            unread_indicator = QWidget()
            unread_indicator.setFixedSize(20, 20)
        
        # Color del borde según tipo
        color_map = {
            "info": "#3B82F6",
            "success": "#10B981", 
            "warning": "#F59E0B",
            "error": "#EF4444"
        }
        border_color = color_map.get(notif.get("type", "info"), "#3B82F6")
        
        widget.setStyleSheet(f"""
            QWidget {{
                background: {'#F0F9FF' if not notif.get('read', False) else 'white'};
                border-left: 4px solid {border_color};
                border-radius: 4px;
            }}
            QWidget:hover {{
                background: {'#E0F2FE' if not notif.get('read', False) else '#F8FAFC'};
            }}
        """)
        
        layout.addWidget(icon_label)
        layout.addLayout(content_layout, 1)
        layout.addWidget(unread_indicator)
        
        return widget

    def on_notification_click(self, item):
        """Maneja el click en una notificación"""
        row = self.notif_list.row(item)
        if 0 <= row < len(self.manager.notification_history):
            notif = self.manager.notification_history[row]
            self.manager.handle_notification_click(notif)
            # Actualizar la visualización
            self.load_notifications()
            self.update_unread_count()

    def mark_all_read(self):
        """Marca todas las notificaciones como leídas"""
        self.manager.mark_all_as_read()
        self.load_notifications()
        self.update_unread_count()
        
        # Mostrar confirmación
        QMessageBox.information(self, "Notificaciones Leídas", 
                              "Todas las notificaciones han sido marcadas como leídas.")

    def clear_history(self):
        """Limpia el historial de notificaciones"""
        reply = QMessageBox.question(
            self, 
            "Confirmar Limpieza",
            "¿Está seguro de que desea eliminar todo el historial de notificaciones?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.manager.notification_history.clear()
            self.load_notifications()
            self.update_unread_count()
            
            QMessageBox.information(self, "Historial Limpiado", 
                                  "El historial de notificaciones ha sido limpiado correctamente.")

    def save_config(self):
        """Guarda la configuración"""
        self.manager.config.update({
            "stock_alerts": self.stock_cb.isChecked(),
            "sales_alerts": self.sales_cb.isChecked(),
            "login_alerts": self.login_cb.isChecked(),
            "system_alerts": self.system_cb.isChecked(),
            "position": ["top-right", "bottom-right", "top-left"][self.position_combo.currentIndex()],
        })
        
        # Actualizar duración
        self.manager.notification_duration = self.duration_spin.value() * 1000
        
        # Guardar en archivo
        self.manager.save_config()
        
        # Mostrar confirmación
        QMessageBox.information(self, "Configuración Guardada", 
                              "La configuración de notificaciones ha sido guardada correctamente.")

    def test_notification(self):
        """Muestra una notificación de prueba"""
        self.manager.show_notification(
            "🧪 Notificación de Prueba",
            "Esta es una notificación de prueba del sistema.\n"
            "Puede hacer clic en ella para interactuar.",
            type_="info",
            duration=5000,
            action_callback=lambda: QMessageBox.information(self, "Prueba", "¡Notificación clickeada!"),
            icon="🎯"
        )

    def update_unread_count(self):
        """Actualiza el contador de no leídas"""
        unread_count = self.manager.get_unread_count()
        self.unread_badge.setText(f"{unread_count} no leídas")
        self.unread_badge.setVisible(unread_count > 0)

    def showEvent(self, event):
        """Se ejecuta cuando se muestra el diálogo"""
        super().showEvent(event)
        self.update_unread_count()
        # Marcar como leídas al abrir el centro
        self.manager.mark_all_as_read()
        self.load_notifications()

# ---------------- Funciones de utilidad ----------------

def create_notification_icon(type_):
    """Crea un icono para el tipo de notificación"""
    icons = {
        "info": "🔔",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌"
    }
    return icons.get(type_, "🔔")

def get_notification_color(type_):
    """Retorna el color para el tipo de notificación"""
    colors = {
        "info": "#3B82F6",
        "success": "#10B981",
        "warning": "#F59E0B", 
        "error": "#EF4444"
    }
    return colors.get(type_, "#3B82F6")

# ---------------- Clase de notificación persistente ----------------

class PersistentNotification(QFrame):
    """Notificación persistente para la barra de estado"""
    
    def __init__(self, message, type_="info", parent=None):
        super().__init__(parent)
        self.setup_ui(message, type_)
        
    def setup_ui(self, message, type_):
        """Configura la interfaz de la notificación persistente"""
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QFrame {{
                background: {get_notification_color(type_)};
                border-radius: 6px;
                border: 1px solid rgba(255,255,255,0.1);
                margin: 2px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        
        # Icono
        icon_label = QLabel(create_notification_icon(type_))
        icon_label.setStyleSheet("color: white; font-size: 14px;")
        
        # Mensaje
        message_label = QLabel(message)
        message_label.setStyleSheet("color: white; font-size: 11px; font-weight: 500;")
        
        # Botón cerrar
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
        """)
        close_btn.clicked.connect(self.deleteLater)
        close_btn.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        layout.addWidget(close_btn)
        
        # Auto-ocultar después de 10 segundos
        QTimer.singleShot(10000, self.deleteLater)

# ---------------- Sistema de notificaciones en barra de estado ----------------

class StatusBarNotificationSystem:
    """Sistema de notificaciones para la barra de estado"""
    
    def __init__(self, status_bar):
        self.status_bar = status_bar
        self.notification_area = QWidget()
        self.notification_layout = QHBoxLayout(self.notification_area)
        self.notification_layout.setContentsMargins(0, 0, 0, 0)
        self.notification_layout.setSpacing(4)
        
        # Añadir a la barra de estado
        self.status_bar.addPermanentWidget(self.notification_area)

    def show_notification(self, message, type_="info"):
        """Muestra una notificación en la barra de estado"""
        notification = PersistentNotification(message, type_)
        self.notification_layout.addWidget(notification)
        
        # Limitar a 3 notificaciones simultáneas
        while self.notification_layout.count() > 3:
            old_notif = self.notification_layout.itemAt(0).widget()
            if old_notif:
                old_notif.deleteLater()

    def clear_all(self):
        """Limpia todas las notificaciones"""
        while self.notification_layout.count() > 0:
            item = self.notification_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

# ---------------- Decoradores para notificaciones automáticas ----------------

def notify_on_success(message):
    """Decorador para notificar éxito automáticamente"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                # Buscar el notification_manager en los args o self
                manager = None
                for arg in args:
                    if hasattr(arg, 'notification_manager'):
                        manager = arg.notification_manager
                        break
                    if isinstance(arg, NotificationManager):
                        manager = arg
                        break
                
                if manager and hasattr(manager, 'show_notification'):
                    manager.show_notification(
                        "✅ Operación Exitosa",
                        message,
                        type_="success",
                        duration=4000
                    )
                return result
            except Exception as e:
                # También notificar errores
                for arg in args:
                    if hasattr(arg, 'notification_manager'):
                        manager = arg.notification_manager
                        if manager and hasattr(manager, 'show_notification'):
                            manager.show_notification(
                                "❌ Error en Operación",
                                f"{message}\nError: {str(e)}",
                                type_="error",
                                duration=6000
                            )
                        break
                raise e
        return wrapper
    return decorator

def notify_on_error(error_message):
    """Decorador para notificar errores automáticamente"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Buscar el notification_manager
                manager = None
                for arg in args:
                    if hasattr(arg, 'notification_manager'):
                        manager = arg.notification_manager
                        break
                
                if manager and hasattr(manager, 'show_notification'):
                    manager.show_notification(
                        "❌ Error en Operación",
                        f"{error_message}\nDetalles: {str(e)}",
                        type_="error",
                        duration=6000
                    )
                raise e
        return wrapper
    return decorator

# ---------------- Ejemplos de uso integrado ----------------

class NotificationExamples:
    """Ejemplos de notificaciones para diferentes casos de uso"""
    
    def __init__(self, notification_manager):
        self.manager = notification_manager

    def example_backup_completed(self, filename):
        """Ejemplo: Notificación de backup completado"""
        self.manager.show_notification(
            "💾 Backup Completado",
            f"El respaldo se guardó como:\n{filename}",
            type_="success",
            icon="🛡️"
        )

    def example_export_completed(self, format_type, record_count):
        """Ejemplo: Notificación de exportación completada"""
        self.manager.show_notification(
            "📤 Exportación Exitosa",
            f"Se exportaron {record_count} registros\nFormato: {format_type}",
            type_="success",
            icon="✅"
        )

    def example_import_completed(self, record_count, errors=0):
        """Ejemplo: Notificación de importación completada"""
        if errors == 0:
            self.manager.show_notification(
                "📥 Importación Exitosa",
                f"Se importaron {record_count} registros\nSin errores",
                type_="success",
                icon="✅"
            )
        else:
            self.manager.show_notification(
                "⚠️ Importación con Errores",
                f"Se importaron {record_count} registros\n{errors} errores encontrados",
                type_="warning",
                icon="⚠️"
            )

    def example_system_maintenance(self, message, duration_minutes):
        """Ejemplo: Notificación de mantenimiento del sistema"""
        self.manager.show_notification(
            "🔧 Mantenimiento del Sistema",
            f"{message}\nDuración estimada: {duration_minutes} minutos",
            type_="info",
            duration=8000,
            icon="⚙️"
        )

# ---------------- Fin del archivo ----------------

if __name__ == "__main__":
    # Código de prueba
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Crear ventana de prueba
    window = QWidget()
    window.setWindowTitle("Prueba de Notificaciones")
    window.resize(400, 300)
    
    layout = QVBoxLayout(window)
    
    # Botones de prueba
    test_btn = QPushButton("Probar Notificación de Éxito")
    test_btn.clicked.connect(lambda: 
        NotificationManager(window, None).show_notification(
            "✅ Prueba Exitosa",
            "Esta es una notificación de prueba exitosa",
            type_="success"
        )
    )
    
    error_btn = QPushButton("Probar Notificación de Error")
    error_btn.clicked.connect(lambda:
        NotificationManager(window, None).show_notification(
            "❌ Error de Prueba", 
            "Esta es una notificación de error de prueba",
            type_="error"
        )
    )
    
    layout.addWidget(test_btn)
    layout.addWidget(error_btn)
    layout.addStretch()
    
    window.show()
    
    sys.exit(app.exec())
        
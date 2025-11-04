# main.py  — Estilo Windows 11 Profesional
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QDialog, QLineEdit,
    QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Property
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter

from database import DBManager
from file_manager import FileManager
from frames.notificaciones import NotificationManager

# Intento seguro de importar frames (si faltan, usamos placeholder)
def safe_import_frame(module_path: str, class_name: str):
    try:
        mod = __import__(module_path, fromlist=[class_name])
        return getattr(mod, class_name)
    except Exception as e:
        print(f"[WARN] No se pudo importar {module_path}.{class_name}: {e}")
        return None

DashboardFrameCls = safe_import_frame("frames.dashboard", "DashboardFrame")
ProductFrameCls = safe_import_frame("frames.product", "ProductFrame")
SupplierFrameCls = safe_import_frame("frames.suppliers", "SupplierFrame")
ConfigFrameCls = safe_import_frame("frames.config", "ConfigFrame")
SalesFrameCls = safe_import_frame("frames.sales", "SalesFrame")
ClientsFrameCls = safe_import_frame("frames.clients", "ClientsFrame")


class AnimatedButton(QPushButton):
    """Botón con animaciones suaves al estilo Windows 11"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._animation_progress = 0
        self.setCursor(Qt.PointingHandCursor)
        
        self.animation = QPropertyAnimation(self, b"animation_progress")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
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


class ModernLoginDialog(QDialog):
    """Modal de login con diseño Windows 11 moderno"""
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Iniciar Sesión - Sistema ERP")
        self.setModal(True)
        self.setFixedSize(420, 320)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Widget principal con sombra
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # Header con logo
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Bienvenido")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1E293B; margin-bottom: 4px;")
        
        subtitle = QLabel("Sistema ERP Empresarial")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #64748B;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.username = QLineEdit()
        self.username.setText("admin")
        self.username.setPlaceholderText("Ingrese su usuario")
        self.username.setMinimumHeight(38)
        self.username.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1E293B;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
                background: #F8FAFF;
            }
        """)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setText("1234")
        self.password.setPlaceholderText("Ingrese su contraseña")
        self.password.setMinimumHeight(38)
        self.password.setStyleSheet(self.username.styleSheet())
        
        form_layout.addRow("Usuario:", self.username)
        form_layout.addRow("Contraseña:", self.password)
        layout.addLayout(form_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        btn_cancel = AnimatedButton("Cancelar")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.setStyleSheet("""
            AnimatedButton {
                background: transparent;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                color: #64748B;
                font-weight: 600;
                font-size: 14px;
            }
            AnimatedButton:hover {
                background: #F1F5F9;
                border-color: #CBD5E1;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_login = AnimatedButton("Acceder al Sistema")
        btn_login.setMinimumHeight(38)
        btn_login.setStyleSheet("""
            AnimatedButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563EB, stop:1 #3B82F6);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                font-size: 14px;
            }
            AnimatedButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1D4ED8, stop:1 #2563EB);
            }
        """)
        btn_login.clicked.connect(self.attempt_login)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_login)
        layout.addLayout(btn_layout)
        
        # Layout principal del dialog
        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.setContentsMargins(20, 20, 20, 20)
        main_dialog_layout.addWidget(main_widget)
        
        # Enter key shortcut
        self.username.returnPressed.connect(self.attempt_login)
        self.password.returnPressed.connect(self.attempt_login)

    def attempt_login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()
        
        if not user or not pwd:
            QMessageBox.warning(self, "Campos requeridos", "Por favor complete todos los campos.")
            return
            
        try:
            row = self.db.fetch(
                "SELECT id, nombre, rol FROM Usuarios WHERE usuario = ? AND contrasena = ?",
                (user, pwd)
            )
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", 
                               f"Error al conectar con la base de datos:\n{str(e)}")
            return

        if row:
            self.accepted_user = row[0]
            self.accept()
        else:
            QMessageBox.warning(self, "Acceso denegado", 
                              "Usuario o contraseña incorrectos.\n\nIntente con:\nUsuario: admin\nContraseña: 1234")


class PlaceholderFrame(QWidget):
    def __init__(self, name="Módulo", message="Módulo no convertido a PySide6 aún"):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icono placeholder
        icon_label = QLabel("📊")
        icon_label.setFont(QFont("Segoe UI", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        title = QLabel(f"<h2 style='color: #1E293B; margin: 20px 0;'>{name}</h2>")
        title.setAlignment(Qt.AlignCenter)
        
        desc = QLabel(f"<p style='color: #64748B; font-size: 14px; max-width: 400px; text-align: center;'>{message}</p>")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()


class ModernSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setStyleSheet("""
            ModernSidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F8FAFC, stop:1 #FFFFFF);
                border-right: 1px solid #E2E8F0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(8)
        
        # Branding
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(4)
        
        brand_title = QLabel("Sistema ERP")
        brand_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        brand_title.setStyleSheet("color: #1E293B;")
        
        brand_subtitle = QLabel("Empresa XYZ")
        brand_subtitle.setFont(QFont("Segoe UI", 10))
        brand_subtitle.setStyleSheet("color: #64748B;")
        
        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_subtitle)
        layout.addLayout(brand_layout)
        layout.addSpacing(20)
        
        # Navigation menu
        self.btns = {}
        menu_items = [
            ("🏠", "Dashboard", "Dashboard"),
            ("💰", "Ventas (POS)", "Ventas (POS)"),
            ("👥", "Clientes", "Clientes"),
            ("📦", "Productos", "Productos"),
            ("🏢", "Proveedores", "Proveedores"),
            ("⚙️", "Configuración", "Configuración"),
            ("🔔", "Notificaciones", "Notificaciones")
        ]
        
        for icon, text, name in menu_items:
            btn = AnimatedButton(f"   {icon}  {text}")
            btn.setCheckable(True)
            btn.setMinimumHeight(42)
            btn.setStyleSheet("""
                AnimatedButton {
                    background: transparent;
                    border: none;
                    text-align: left;
                    padding: 10px 16px;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                    color: #475569;
                    border-radius: 8px;
                    margin: 2px 0;
                }
                AnimatedButton:hover {
                    background: #F1F5F9;
                    color: #1E293B;
                }
                AnimatedButton:checked {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3B82F6, stop:1 #60A5FA);
                    color: white;
                    font-weight: 600;
                }
            """)
            btn.clicked.connect(lambda checked, n=name: parent.show_frame(n))
            layout.addWidget(btn)
            self.btns[name] = btn
        
        layout.addStretch()
        
        # User info section
        user_section = QFrame()
        user_section.setStyleSheet("""
            QFrame {
                background: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #E2E8F0;
                padding: 12px;
            }
        """)
        
        user_layout = QVBoxLayout(user_section)
        
        self.lbl_user = QLabel("No autenticado")
        self.lbl_user.setStyleSheet("color: #475569; font-size: 13px; font-weight: 500;")
        
        self.lbl_role = QLabel("Inicia sesión para continuar")
        self.lbl_role.setStyleSheet("color: #94A3B8; font-size: 11px;")
        
        logout_btn = AnimatedButton("🚪  Cerrar sesión")
        logout_btn.setMinimumHeight(36)
        logout_btn.setStyleSheet("""
            AnimatedButton {
                background: transparent;
                border: 1px solid #FECACA;
                border-radius: 6px;
                color: #DC2626;
                font-size: 12px;
                font-weight: 500;
            }
            AnimatedButton:hover {
                background: #FEF2F2;
            }
        """)
        logout_btn.clicked.connect(parent.logout)
        
        user_layout.addWidget(self.lbl_user)
        user_layout.addWidget(self.lbl_role)
        user_layout.addSpacing(8)
        user_layout.addWidget(logout_btn)
        
        layout.addWidget(user_section)


class ERPMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema ERP Empresarial - Windows 11 Style")
        self.resize(1600, 1000)
        self.setMinimumSize(1200, 800)

        # DB y filemanager
        self.db = DBManager()
        self.file_manager = FileManager(self.db)

        # Notification manager (PySide6)
        self.notification_manager = NotificationManager(self, self.db)
        try:
            self.notification_manager.stock_check_timer.start()
        except Exception:
            pass

        # datos de usuario
        self.current_user = None

        # Estructura main con estilo moderno
        central_widget = QWidget()
        central_widget.setStyleSheet("background: #F8FAFC;")
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar moderno
        self.sidebar = ModernSidebar(self)
        main_layout.addWidget(self.sidebar)

        # Área principal con header y contenido
        main_area = QWidget()
        main_area.setStyleSheet("background: #F8FAFC;")
        main_area_layout = QVBoxLayout(main_area)
        main_area_layout.setContentsMargins(0, 0, 0, 0)
        main_area_layout.setSpacing(0)

        # Header moderno
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        self.header_title = QLabel("Dashboard")
        self.header_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.header_title.setStyleSheet("color: #1E293B;")
        
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        
        # Botones de control de ventana (minimizar, maximizar, cerrar)
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        
        btn_minimize = AnimatedButton("−")
        btn_minimize.setFixedSize(28, 28)
        btn_minimize.setStyleSheet("""
            AnimatedButton {
                background: transparent;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                color: #64748B;
                font-weight: bold;
            }
            AnimatedButton:hover {
                background: #F1F5F9;
            }
        """)
        btn_minimize.clicked.connect(self.showMinimized)
        
        btn_maximize = AnimatedButton("□")
        btn_maximize.setFixedSize(28, 28)
        btn_maximize.setStyleSheet(btn_minimize.styleSheet())
        btn_maximize.clicked.connect(self.toggle_maximize)
        
        btn_close = AnimatedButton("×")
        btn_close.setFixedSize(28, 28)
        btn_close.setStyleSheet("""
            AnimatedButton {
                background: transparent;
                border: 1px solid #FECACA;
                border-radius: 6px;
                color: #DC2626;
                font-weight: bold;
            }
            AnimatedButton:hover {
                background: #FEF2F2;
            }
        """)
        btn_close.clicked.connect(self.close)
        
        control_layout.addWidget(btn_minimize)
        control_layout.addWidget(btn_maximize)
        control_layout.addWidget(btn_close)
        
        header_layout.addLayout(control_layout)
        main_area_layout.addWidget(header)

        # Área de contenido
        content_frame = QFrame()
        content_frame.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background: transparent;
                border-radius: 12px;
            }
        """)
        content_layout.addWidget(self.stack)

        main_area_layout.addWidget(content_frame)
        main_layout.addWidget(main_area, 1)

        # Registrar frames
        self.frames = {}
        self.frame_titles = {
            "Dashboard": "Panel Principal",
            "Ventas (POS)": "Sistema de Ventas POS",
            "Clientes": "Gestión de Clientes",
            "Productos": "Inventario de Productos",
            "Proveedores": "Gestión de Proveedores",
            "Configuración": "Configuración del Sistema",
            "Notificaciones": "Centro de Notificaciones"
        }

        # Dashboard
        if DashboardFrameCls:
            try:
                dashboard = DashboardFrameCls(self)
            except TypeError:
                try:
                    dashboard = DashboardFrameCls(self, self)
                except Exception as e:
                    print("[WARN] Error instanciando Dashboard:", e)
                    dashboard = PlaceholderFrame("Dashboard", "Error cargando el panel principal")
            except Exception as e:
                print("[WARN] Error instanciando Dashboard:", e)
                dashboard = PlaceholderFrame("Dashboard", "Error cargando el panel principal")
        else:
            dashboard = PlaceholderFrame("Dashboard", "Módulo Dashboard en desarrollo")

        self.add_frame("Dashboard", dashboard)

        # Otros frames
        def reg(name, cls):
            if cls:
                try:
                    w = cls(self)
                except TypeError:
                    try:
                        w = cls(self, self)
                    except Exception as ex:
                        print(f"[WARN] Error creando {name}: {ex}")
                        w = PlaceholderFrame(name, f"Error inicializando {name}")
                except Exception as ex:
                    print(f"[WARN] Error creando {name}: {ex}")
                    w = PlaceholderFrame(name, f"Error inicializando {name}")
            else:
                w = PlaceholderFrame(name, f"Módulo {name} en desarrollo")
            self.add_frame(name, w)

        reg("Productos", ProductFrameCls)
        reg("Proveedores", SupplierFrameCls)
        reg("Configuración", ConfigFrameCls)
        reg("Clientes", ClientsFrameCls)
        reg("Ventas (POS)", SalesFrameCls)

        # Notificaciones
        notif_widget = QWidget()
        notif_layout = QVBoxLayout(notif_widget)
        notif_layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("🔔")
        icon.setFont(QFont("Segoe UI", 48))
        icon.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Centro de Notificaciones")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1E293B; margin: 20px 0;")
        title.setAlignment(Qt.AlignCenter)
        
        btn_open = AnimatedButton("Abrir Centro de Notificaciones")
        btn_open.setMinimumHeight(44)
        btn_open.setStyleSheet("""
            AnimatedButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, stop:1 #60A5FA);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                font-size: 14px;
                padding: 0 24px;
            }
            AnimatedButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563EB, stop:1 #3B82F6);
            }
        """)
        btn_open.clicked.connect(self.notification_manager.show_notification_center)
        
        notif_layout.addWidget(icon)
        notif_layout.addWidget(title)
        notif_layout.addWidget(btn_open, alignment=Qt.AlignCenter)
        notif_layout.addStretch()
        
        self.add_frame("Notificaciones", notif_widget)

        # Mostrar dashboard por defecto
        self.show_frame("Dashboard", set_checked=False)
        
        # Abrir login después de mostrar la ventana
        QTimer.singleShot(200, self.show_login)

    def add_frame(self, name, widget):
        idx = self.stack.addWidget(widget)
        self.frames[name] = idx

    def show_frame(self, name, set_checked=True):
        if name in self.frames:
            self.stack.setCurrentIndex(self.frames[name])
            self.header_title.setText(self.frame_titles.get(name, name))
            
            if set_checked:
                for btn_name, btn in self.sidebar.btns.items():
                    btn.setChecked(btn_name == name)
        else:
            print("[WARN] Frame no registrado:", name)

    def show_login(self):
        dlg = ModernLoginDialog(self, self.db)
        res = dlg.exec()
        if res == QDialog.Accepted:
            self.current_user = dlg.accepted_user
            try:
                user_name = self.current_user[1]
                user_role = self.current_user[2]
                self.sidebar.lbl_user.setText(user_name)
                self.sidebar.lbl_role.setText(user_role)
            except Exception:
                self.sidebar.lbl_user.setText("Usuario")
                self.sidebar.lbl_role.setText("Rol no definido")
                
            # Notificar login
            try:
                self.notification_manager.notify_login(user_name, user_role)
            except Exception as e:
                print("[WARN] notify_login falló:", e)
                
            self.show_frame("Dashboard")
        else:
            self.show_frame("Dashboard")

    def logout(self):
        reply = QMessageBox.question(self, "Cerrar sesión", 
                                   "¿Estás seguro de que deseas cerrar la sesión?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.current_user = None
            self.sidebar.lbl_user.setText("No autenticado")
            self.sidebar.lbl_role.setText("Inicia sesión para continuar")
            
            try:
                self.notification_manager.show_notification(
                    "Sesión finalizada", 
                    "Has cerrado sesión correctamente.", 
                    type_="info", 
                    duration=2500
                )
            except Exception:
                pass
            
            self.show_frame("Dashboard")

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def closeEvent(self, event):
        try:
            self.db.close()
        except Exception:
            pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Establecer estilo general de la aplicación
    app.setStyle("Fusion")
    
    # Configurar paleta de colores
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 250, 252))
    palette.setColor(QPalette.WindowText, QColor(30, 41, 59))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 250, 252))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(30, 41, 59))
    palette.setColor(QPalette.Text, QColor(30, 41, 59))
    palette.setColor(QPalette.Button, QColor(248, 250, 252))
    palette.setColor(QPalette.ButtonText, QColor(30, 41, 59))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(59, 130, 246))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Establecer fuente global
    app.setFont(QFont("Segoe UI", 10))
    
    w = ERPMainWindow()
    w.show()
    sys.exit(app.exec())
"""
database.py - Gestor de Base de Datos SQLite Mejorado
Maneja todas las operaciones CRUD y estructura de la base de datos completa
"""

import sqlite3
from datetime import datetime
import json


class DBManager:
    """Maneja la conexión a SQLite y operaciones CRUD/Setup."""

    def __init__(self, db_name="erp_profesional.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.insert_initial_data()

    def create_tables(self):
        """Crea todas las tablas necesarias del sistema."""

        # Tabla de Configuración del Sistema
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT,
                descripcion TEXT,
                categoria TEXT,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de Usuarios
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL,
                rol TEXT NOT NULL,
                email TEXT,
                telefono TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_login DATETIME,
                intentos_login INTEGER DEFAULT 0,
                bloqueado INTEGER DEFAULT 0
            )
        """)

        # Tabla de Clientes
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dni TEXT UNIQUE,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                fecha_registro TEXT NOT NULL,
                activo INTEGER DEFAULT 1,
                tipo_cliente TEXT DEFAULT 'Normal',
                limite_credito REAL DEFAULT 0,
                notas TEXT
            )
        """)

        # Tabla de Proveedores (Mejorada)
        self.cursor.execute("""
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

        # Tabla de Categorías de Productos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT,
                activa INTEGER DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de Productos (Mejorada)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                costo REAL,
                stock INTEGER NOT NULL,
                stock_minimo INTEGER DEFAULT 10,
                categoria_id INTEGER,
                proveedor_id INTEGER,
                sku TEXT UNIQUE,
                codigo_barras TEXT,
                unidad_medida TEXT DEFAULT 'Unidad',
                impuesto REAL DEFAULT 0.15,
                activo INTEGER DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES Categorias(id),
                FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id)
            )
        """)

        # Tabla de Descuentos (Mejorada)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Descuentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT,
                porcentaje REAL NOT NULL,
                monto_minimo REAL DEFAULT 0,
                fecha_inicio DATE,
                fecha_fin DATE,
                activo INTEGER DEFAULT 1,
                aplica_categoria TEXT,
                aplica_producto TEXT,
                maximo_usos INTEGER DEFAULT 0,
                usos_actual INTEGER DEFAULT 0
            )
        """)

        # Tabla de Ventas (Mejorada)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Ventas (
                id TEXT PRIMARY KEY,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                subtotal REAL,
                impuesto REAL,
                descuento_total REAL DEFAULT 0,
                monto_pagado REAL,
                vuelto REAL,
                usuario_id INTEGER,
                id_cliente INTEGER,
                tipo_recibo TEXT,
                estado TEXT DEFAULT 'Completada',
                metodo_pago TEXT DEFAULT 'Efectivo',
                notas TEXT,
                FOREIGN KEY (id_cliente) REFERENCES Clientes(id)
            )
        """)

        # Tabla de Detalle de Venta (Mejorada)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS DetalleVenta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id TEXT,
                producto_id INTEGER,
                nombre_producto TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                descuento REAL DEFAULT 0,
                impuesto REAL DEFAULT 0,
                subtotal REAL,
                FOREIGN KEY (venta_id) REFERENCES Ventas(id),
                FOREIGN KEY (producto_id) REFERENCES Productos(id)
            )
        """)

        # Tabla de Inventario (Movimientos de stock)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MovimientosInventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                tipo_movimiento TEXT, -- 'entrada', 'salida', 'ajuste'
                cantidad INTEGER,
                stock_anterior INTEGER,
                stock_nuevo INTEGER,
                motivo TEXT,
                referencia TEXT, -- ID de venta, compra, etc.
                usuario_id INTEGER,
                fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
                notas TEXT,
                FOREIGN KEY (producto_id) REFERENCES Productos(id)
            )
        """)

        # Tabla de Compras/Órdenes de Compra
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor_id INTEGER,
                numero_orden TEXT UNIQUE,
                fecha_orden DATE,
                fecha_esperada DATE,
                estado TEXT DEFAULT 'Pendiente',
                subtotal REAL,
                impuesto REAL,
                total REAL,
                notas TEXT,
                usuario_id INTEGER,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id)
            )
        """)

        # Tabla de Detalle de Compra
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS DetalleCompra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compra_id INTEGER,
                producto_id INTEGER,
                nombre_producto TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                subtotal REAL,
                FOREIGN KEY (compra_id) REFERENCES Compras(id),
                FOREIGN KEY (producto_id) REFERENCES Productos(id)
            )
        """)

        # Tabla de Notificaciones
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Notificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                tipo TEXT DEFAULT 'info', -- 'info', 'success', 'warning', 'error'
                leida INTEGER DEFAULT 0,
                accion_callback TEXT,
                datos_accion TEXT,
                usuario_id INTEGER,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_leida DATETIME
            )
        """)

        # Tabla de Auditoría (Logs del sistema)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                accion TEXT NOT NULL,
                modulo TEXT,
                descripcion TEXT,
                ip_address TEXT,
                user_agent TEXT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla de Backups
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_archivo TEXT NOT NULL,
                ruta TEXT NOT NULL,
                tamano INTEGER,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                usuario_id INTEGER,
                notas TEXT,
                automatico INTEGER DEFAULT 0
            )
        """)

        # Tabla de Configuración de Empresa
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ruc TEXT,
                direccion TEXT,
                telefono TEXT,
                email TEXT,
                website TEXT,
                logo BLOB,
                moneda TEXT DEFAULT 'HNL',
                idioma TEXT DEFAULT 'es',
                zona_horaria TEXT DEFAULT 'America/Tegucigalpa',
                impuesto_por_defecto REAL DEFAULT 0.15
            )
        """)

        # Tabla de Series de Facturación
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SeriesFacturacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serie TEXT UNIQUE NOT NULL,
                descripcion TEXT,
                numero_actual INTEGER DEFAULT 1,
                resolucion TEXT,
                fecha_resolucion DATE,
                numero_desde INTEGER,
                numero_hasta INTEGER,
                activa INTEGER DEFAULT 1
            )
        """)

        self.conn.commit()

    def insert_initial_data(self):
        """Inserta datos iniciales si las tablas están vacías."""

        # Configuración del sistema
        if not self.fetch("SELECT * FROM Configuracion"):
            configuraciones = [
                ('empresa_nombre', 'Mi Empresa ERP', 'Nombre legal de la empresa', 'empresa'),
                ('empresa_ruc', '', 'RUC o NIT de la empresa', 'empresa'),
                ('empresa_direccion', '', 'Dirección fiscal', 'empresa'),
                ('empresa_telefono', '', 'Teléfono de contacto', 'empresa'),
                ('empresa_email', '', 'Email de contacto', 'empresa'),
                ('iva_por_defecto', '0.15', 'IVA por defecto para facturas', 'facturacion'),
                ('moneda', 'HNL', 'Moneda principal del sistema', 'regional'),
                ('idioma', 'es', 'Idioma del sistema', 'regional'),
                ('zona_horaria', 'America/Tegucigalpa', 'Zona horaria', 'regional'),
                ('recibo_template', self.default_receipt_template(), 'Plantilla de recibo HTML', 'sistema'),
                ('notificaciones_stock', '1', 'Alertas de stock bajo', 'notificaciones'),
                ('notificaciones_ventas', '1', 'Notificaciones de ventas', 'notificaciones'),
                ('backup_automatico', '1', 'Backup automático habilitado', 'backup'),
                ('session_timeout', '30', 'Tiempo de espera de sesión en minutos', 'seguridad'),
            ]
            
            for clave, valor, descripcion, categoria in configuraciones:
                self.execute(
                    "INSERT INTO Configuracion (clave, valor, descripcion, categoria) VALUES (?, ?, ?, ?)",
                    (clave, valor, descripcion, categoria)
                )

        # Usuario administrador por defecto
        if not self.fetch("SELECT * FROM Usuarios"):
            self.execute(
                "INSERT INTO Usuarios (nombre, usuario, contrasena, rol, email) VALUES (?, ?, ?, ?, ?)",
                ("Administrador Principal", "admin", "1234", "Administrador", "admin@empresa.com"),
            )

        # Proveedor de ejemplo
        if not self.fetch("SELECT * FROM Proveedores"):
            self.execute(
                """INSERT INTO Proveedores 
                   (nombre, contacto, cargo, telefono, email, categoria, estado, direccion, ruc) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("Distribuidora Central", "Juan Pérez", "Gerente", "555-1234", 
                 "ventas@distribuidora.com", "Tecnología", "Activo", 
                 "Colonia Palmira, Tegucigalpa", "0801-9999-12345"),
            )

        # Categorías de productos
        if not self.fetch("SELECT * FROM Categorias"):
            categorias = [
                ("Tecnología", "Productos tecnológicos y electrónicos"),
                ("Oficina", "Suministros de oficina"),
                ("Hogar", "Artículos para el hogar"),
                ("Electrodomésticos", "Electrodomésticos y línea blanca"),
            ]
            
            for nombre, descripcion in categorias:
                self.execute(
                    "INSERT INTO Categorias (nombre, descripcion) VALUES (?, ?)",
                    (nombre, descripcion)
                )

        # Descuentos predefinidos
        if not self.fetch("SELECT * FROM Descuentos"):
            descuentos = [
                ("Docena 10%", "Docena", 0.10, 0, None, None, 1),
                ("Mayorista 15%", "Mayorista", 0.15, 1000, None, None, 1),
                ("Cliente Frecuente 5%", "Fidelidad", 0.05, 0, None, None, 1),
            ]
            
            for nombre, tipo, porcentaje, monto_minimo, fecha_inicio, fecha_fin, activo in descuentos:
                self.execute(
                    "INSERT INTO Descuentos (nombre, tipo, porcentaje, monto_minimo, fecha_inicio, fecha_fin, activo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (nombre, tipo, porcentaje, monto_minimo, fecha_inicio, fecha_fin, activo)
                )

        # Productos de ejemplo
        if not self.fetch("SELECT * FROM Productos"):
            # Obtener IDs de categoría y proveedor
            categoria_tec = self.fetch("SELECT id FROM Categorias WHERE nombre = 'Tecnología'")[0][0]
            proveedor_id = self.fetch("SELECT id FROM Proveedores LIMIT 1")[0][0]
            
            productos_ejemplo = [
                ('Monitor 27" 4K', "Monitor 4K profesional para diseño", 320.00, 200.00, 15, 5, categoria_tec, proveedor_id, "MON-27-4K", "1234567890123"),
                ("Teclado Mecánico RGB", "Switches Blue, retroiluminación RGB", 45.00, 25.00, 105, 10, categoria_tec, proveedor_id, "TEC-MEC-RGB", "1234567890124"),
                ("Mouse Gamer Pro", "RGB, 16000 DPI, 6 botones", 35.00, 18.00, 50, 5, categoria_tec, proveedor_id, "MOU-GAM-PRO", "1234567890125"),
                ("Laptop HP EliteBook", "i5, 8GB RAM, 256GB SSD, 14\"", 650.00, 450.00, 8, 2, categoria_tec, proveedor_id, "LAP-HP-ELITE", "1234567890126"),
                ("Impresora Láser", "Impresora láser blanco y negro", 150.00, 90.00, 12, 3, categoria_tec, proveedor_id, "IMP-LAS-BN", "1234567890127"),
            ]
            
            for nombre, descripcion, precio, costo, stock, stock_minimo, categoria_id, proveedor_id, sku, codigo_barras in productos_ejemplo:
                self.execute(
                    """INSERT INTO Productos 
                       (nombre, descripcion, precio, costo, stock, stock_minimo, categoria_id, proveedor_id, sku, codigo_barras) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (nombre, descripcion, precio, costo, stock, stock_minimo, categoria_id, proveedor_id, sku, codigo_barras)
                )

        # Clientes de ejemplo
        if not self.fetch("SELECT * FROM Clientes"):
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            clientes_ejemplo = [
                (
                    "Juan Carlos", "Pérez González", "0801199901234", "9876-1234",
                    "juan.perez@email.com", "Colonia Palmira, Tegucigalpa", fecha_actual,
                    1, "Premium", 5000.00, "Cliente frecuente, paga puntual"
                ),
                (
                    "María Elena", "Rodríguez López", "0801200005678", "9965-4789",
                    "maria.rodriguez@email.com", "Barrio La Granja, San Pedro Sula", fecha_actual,
                    1, "Normal", 1000.00, "Cliente ocasional"
                ),
                (
                    "José Antonio", "Martínez Castro", "0501199812345", "9754-3261",
                    "jose.martinez@email.com", "Centro, Comayagua", fecha_actual,
                    1, "Gold", 10000.00, "Cliente corporativo"
                ),
                (
                    "Ana Sofía", "García Hernández", "1801199909876", "9843-7521",
                    "ana.garcia@email.com", "Colonia Kennedy, La Ceiba", fecha_actual,
                    1, "Normal", 2000.00, "Preferencia por productos tecnológicos"
                ),
            ]
            
            for datos in clientes_ejemplo:
                self.execute(
                    """INSERT INTO Clientes 
                       (nombre, apellido, dni, telefono, email, direccion, fecha_registro, activo, tipo_cliente, limite_credito, notas) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    datos
                )

        # Información de empresa
        if not self.fetch("SELECT * FROM Empresa"):
            self.execute(
                """INSERT INTO Empresa 
                   (nombre, ruc, direccion, telefono, email, moneda, impuesto_por_defecto) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("Mi Empresa ERP", "0801-9999-12345", "Colonia Palmira, Tegucigalpa", 
                 "2234-5678", "info@miempresa.com", "HNL", 0.15)
            )

        # Series de facturación
        if not self.fetch("SELECT * FROM SeriesFacturacion"):
            self.execute(
                """INSERT INTO SeriesFacturacion 
                   (serie, descripcion, numero_actual, resolucion, fecha_resolucion, numero_desde, numero_hasta) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("A", "Serie principal para facturas", 1, "RES-2024-001", 
                 "2024-01-01", 1, 100000)
            )

        self.conn.commit()

    def default_receipt_template(self):
        """Plantilla HTML por defecto para recibos."""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Recibo {{numero_factura}}</title>
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
            padding: 20px; 
            font-size: 10pt; 
            background: #f8f9fa;
        }
        .recibo { 
            width: 300px; 
            margin: 0 auto; 
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header { 
            text-align: center; 
            border-bottom: 2px solid #3B82F6;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .company-name { 
            font-size: 16pt; 
            font-weight: bold;
            color: #1E293B;
            margin: 0;
        }
        .company-info { 
            font-size: 9pt; 
            color: #64748B;
            margin: 5px 0;
        }
        .sale-info { 
            background: #F8FAFC;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 15px;
        }
        .detail { 
            margin-top: 15px; 
        }
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        .items-table th {
            background: #3B82F6;
            color: white;
            padding: 8px;
            text-align: left;
            font-size: 9pt;
        }
        .items-table td {
            padding: 6px 8px;
            border-bottom: 1px solid #E2E8F0;
            font-size: 9pt;
        }
        .total-section { 
            margin-top: 15px; 
            border-top: 2px solid #3B82F6; 
            padding-top: 10px; 
        }
        .total-row {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        .total { 
            font-weight: bold; 
            font-size: 12pt;
            color: #1E293B;
        }
        .footer { 
            margin-top: 15px; 
            border-top: 1px solid #E2E8F0; 
            padding-top: 10px; 
            text-align: center; 
            font-size: 8pt;
            color: #94A3B8;
        }
        .thank-you {
            color: #3B82F6;
            font-weight: bold;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="recibo">
        <div class="header">
            <h1 class="company-name">{{empresa_nombre}}</h1>
            <p class="company-info">RUC: {{empresa_ruc}}</p>
            <p class="company-info">{{empresa_direccion}}</p>
            <p class="company-info">Tel: {{empresa_telefono}}</p>
        </div>
        
        <div class="sale-info">
            <p><strong>Factura:</strong> {{numero_factura}}</p>
            <p><strong>Fecha:</strong> {{fecha}}</p>
            <p><strong>Cliente:</strong> {{cliente_nombre}}</p>
        </div>
        
        <div class="detail">
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Cant.</th>
                        <th>Precio</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {{items}}
                </tbody>
            </table>
        </div>

        <div class="total-section">
            <div class="total-row">
                <span>Subtotal:</span>
                <span>${{subtotal}}</span>
            </div>
            <div class="total-row">
                <span>IVA (15%):</span>
                <span>${{iva}}</span>
            </div>
            <div class="total-row total">
                <span>TOTAL:</span>
                <span>${{total}}</span>
            </div>
            <div class="total-row">
                <span>Monto Pagado:</span>
                <span>${{monto_pagado}}</span>
            </div>
            <div class="total-row">
                <span>Vuelto:</span>
                <span>${{vuelto}}</span>
            </div>
        </div>

        <div class="footer">
            <p class="thank-you">¡Gracias por su compra!</p>
            <p>Vuelva pronto</p>
            <p>{{fecha_impresion}}</p>
        </div>
    </div>
</body>
</html>"""

    def get_config(self, clave, default=None):
        """Obtiene un valor de configuración."""
        result = self.fetch("SELECT valor FROM Configuracion WHERE clave = ?", (clave,))
        return result[0][0] if result else default

    def set_config(self, clave, valor):
        """Establece o actualiza un valor de configuración."""
        self.execute(
            "INSERT OR REPLACE INTO Configuracion (clave, valor, fecha_actualizacion) VALUES (?, ?, datetime('now'))",
            (clave, valor),
        )

    def fetch(self, query, params=()):
        """Ejecuta una consulta SELECT y retorna los resultados."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error en consulta: {e}")
            return []

    def execute(self, query, params=()):
        """Ejecuta una consulta INSERT/UPDATE/DELETE."""
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error en operación: {e}")
            return None

    def close(self):
        """Cierra la conexión a la base de datos."""
        self.conn.close()

    # Métodos adicionales para funcionalidades específicas

    def get_empresa_info(self):
        """Obtiene la información de la empresa."""
        result = self.fetch("SELECT * FROM Empresa LIMIT 1")
        if result:
            return {
                'nombre': result[0][1],
                'ruc': result[0][2],
                'direccion': result[0][3],
                'telefono': result[0][4],
                'email': result[0][5],
                'moneda': result[0][7],
                'impuesto_por_defecto': result[0][10]
            }
        return None

    def registrar_movimiento_inventario(self, producto_id, tipo, cantidad, motivo, referencia=None, usuario_id=None):
        """Registra un movimiento en el inventario."""
        # Obtener stock actual
        stock_actual = self.fetch("SELECT stock FROM Productos WHERE id = ?", (producto_id,))[0][0]
        
        if tipo == 'entrada':
            nuevo_stock = stock_actual + cantidad
        elif tipo == 'salida':
            nuevo_stock = stock_actual - cantidad
        else:  # ajuste
            nuevo_stock = cantidad
        
        # Actualizar stock del producto
        self.execute("UPDATE Productos SET stock = ? WHERE id = ?", (nuevo_stock, producto_id))
        
        # Registrar movimiento
        self.execute(
            """INSERT INTO MovimientosInventario 
               (producto_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, motivo, referencia, usuario_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (producto_id, tipo, cantidad, stock_actual, nuevo_stock, motivo, referencia, usuario_id)
        )
        
        return nuevo_stock

    def get_productos_bajo_stock(self):
        """Obtiene productos con stock bajo."""
        return self.fetch("""
            SELECT id, nombre, stock, stock_minimo 
            FROM Productos 
            WHERE stock <= stock_minimo AND activo = 1
        """)

    def get_estadisticas_ventas(self, periodo='mes'):
        """Obtiene estadísticas de ventas."""
        if periodo == 'mes':
            query = """
                SELECT strftime('%Y-%m', fecha) as mes, COUNT(*), SUM(total)
                FROM Ventas 
                WHERE fecha >= date('now', '-12 months')
                GROUP BY mes
                ORDER BY mes
            """
        else:  # día
            query = """
                SELECT date(fecha) as dia, COUNT(*), SUM(total)
                FROM Ventas 
                WHERE fecha >= date('now', '-30 days')
                GROUP BY dia
                ORDER BY dia
            """
        
        return self.fetch(query)

    def crear_backup(self, nombre_archivo, ruta, usuario_id=None, automatico=False):
        """Crea un registro de backup en la base de datos."""
        return self.execute(
            """INSERT INTO Backups (nombre_archivo, ruta, usuario_id, automatico, tamano) 
               VALUES (?, ?, ?, ?, ?)""",
            (nombre_archivo, ruta, usuario_id, 1 if automatico else 0, 0)
        )

    def get_notificaciones_pendientes(self, usuario_id=None):
        """Obtiene notificaciones no leídas."""
        if usuario_id:
            return self.fetch(
                "SELECT * FROM Notificaciones WHERE leida = 0 AND (usuario_id IS NULL OR usuario_id = ?) ORDER BY fecha_creacion DESC",
                (usuario_id,)
            )
        else:
            return self.fetch(
                "SELECT * FROM Notificaciones WHERE leida = 0 ORDER BY fecha_creacion DESC"
            )

    def registrar_auditoria(self, usuario_id, accion, modulo, descripcion, ip_address=None, user_agent=None):
        """Registra una acción en la auditoría."""
        return self.execute(
            """INSERT INTO Auditoria (usuario_id, accion, modulo, descripcion, ip_address, user_agent) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (usuario_id, accion, modulo, descripcion, ip_address, user_agent)
        )
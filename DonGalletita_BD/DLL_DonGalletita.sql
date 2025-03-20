DROP DATABASE IF EXISTS don_galletita_bd;
CREATE DATABASE don_galletita_bd;
USE don_galletita_bd;

-- ============================================
-- Tablas
-- ============================================

-- Tabla de usuarios
CREATE TABLE usuarios (
    usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_usuario VARCHAR(255) NOT NULL UNIQUE,
    contrasenia VARCHAR(255) NOT NULL, -- Encriptar en la lógica de la aplicación
    rol ENUM('admin', 'empleado', 'cliente') DEFAULT 'cliente',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    estatus_user INT DEFAULT 1
);

-- Tabla de clientes
CREATE TABLE clientes (
    cliente_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_cliente VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de proveedores
CREATE TABLE proveedores (
    proveedor_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    dia_entrega VARCHAR(20)
);

-- Tabla de insumos
CREATE TABLE insumos (
    insumo_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    tipo_insumo VARCHAR(100) NOT NULL,
    unidad VARCHAR(20),
    cantidad_disponible INT CHECK (cantidad_disponible >= 0),
    precio_unitario DECIMAL(10, 2) NOT NULL,
    fecha_caducidad DATE,
    porcentaje_merma DECIMAL(5, 2) DEFAULT 0.00,
    proveedor_id INT,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(proveedor_id)
);

-- Tabla de productos
CREATE TABLE productos (
    producto_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    cantidad_disponible INT NOT NULL CHECK (cantidad_disponible >= 0),
    precio_venta DECIMAL(10, 2) NOT NULL CHECK (precio_venta >= 0),
    fecha_caducidad DATE
);

-- Tabla de recetas
CREATE TABLE recetas (
    receta_id INT PRIMARY KEY AUTO_INCREMENT,
    producto_id INT,
    insumo_id INT,
    cantidad_necesaria INT NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES productos(producto_id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(insumo_id)
);

-- Tabla de producción
CREATE TABLE produccion (
    produccion_id INT PRIMARY KEY AUTO_INCREMENT,
    producto_id INT,
    fecha_produccion DATETIME DEFAULT CURRENT_TIMESTAMP,
    cantidad_producida INT NOT NULL,
    estatus ENUM('EN_PRODUCCION', 'FINALIZADO') DEFAULT 'EN_PRODUCCION',
    FOREIGN KEY (producto_id) REFERENCES productos(producto_id)
);

-- Tabla de ventas
CREATE TABLE ventas (
    venta_id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT,
    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_venta ENUM('UNI', 'GRM', 'PQT'),
    cantidad INT NOT NULL,
    monto_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);

-- Tabla de pedidos
CREATE TABLE pedidos (
    pedido_id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT,
    fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega DATE NOT NULL,
    estatus_pedido ENUM('PENDIENTE', 'ENTREGADO') DEFAULT 'PENDIENTE',
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);

-- Tabla de detalles de pedidos
CREATE TABLE detalles_pedidos (
    detalle_id INT PRIMARY KEY AUTO_INCREMENT,
    pedido_id INT,
    producto_id INT,
    cantidad INT NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(pedido_id),
    FOREIGN KEY (producto_id) REFERENCES productos(producto_id)
);

-- Tabla de cortes diarios
CREATE TABLE cortes_diarios (
    corte_id INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_ventas DECIMAL(10, 2),
    total_produccion DECIMAL(10, 2),
    total_perdidas_merma DECIMAL(10, 2),
    total_gastos DECIMAL(10, 2),
    total_ganancias DECIMAL(10, 2)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_cliente_id ON pedidos(cliente_id);
CREATE INDEX idx_producto_id ON detalles_pedidos(producto_id);
CREATE INDEX idx_pedido_id ON detalles_pedidos(pedido_id);
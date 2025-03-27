DROP DATABASE IF EXISTS don_galletita_bd;
CREATE DATABASE don_galletita_bd;
USE don_galletita_bd;

-- ============================================
-- Base de datos de Don Galletita 
-- MarsCode
-- Version 1.0 (Pre-correciones maestro BD)
-- ============================================

-- ============================================
-- Tablas
-- ============================================

-- Tabla de usuario
CREATE TABLE usuario (
    usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_usuario VARCHAR(255) NOT NULL UNIQUE,
    contrasenia VARCHAR(255) NOT NULL, -- Encriptar en la lógica de la aplicación
    rol ENUM('proveedor', 'cliente') DEFAULT 'cliente',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    estatus_usuario INT DEFAULT 1
);

-- Tabla de persona 
CREATE TABLE persona (
  persona_id INT PRIMARY KEY AUTO_INCREMENT,
  nombre_persona VARCHAR(255) NOT NULL,
  apellido_paterno_persona VARCHAR(255) NOT NULL,
  apellido_materno_persona VARCHAR(255) NOT NULL,
  telefono VARCHAR(10) NOT NULL,
  direccion VARCHAR(255),
  tipo ENUM('cliente', 'proveedor') NOT NULL,
  fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de compra de insumos
CREATE TABLE compra (
    compra_id INT PRIMARY KEY AUTO_INCREMENT,
    proveedor_id INT NOT NULL,
    fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proveedor_id) REFERENCES persona(persona_id) 
);

-- Tabla de detalle de compra de insumos
CREATE TABLE detalle_compra (
    detalle_compra_id INT PRIMARY KEY AUTO_INCREMENT,
    compra_id INT NOT NULL,
	insumo_id INT NOT NULL, 
    unidad_medida ENUM('kg', 'g', 'l', 'ml', 'pz'),
    cantidad DECIMAL(10, 2) NOT NULL CHECK (cantidad > 0), 
    precio_unitario DECIMAL(10, 2) NOT NULL,
    fecha_caducidad DATE NOT NULL,  
    FOREIGN KEY (compra_id) REFERENCES compra(compra_id),
    FOREIGN KEY (insumo_id) REFERENCES insumo(insumo_id)
);

-- Tabla de inventario de insumos
CREATE TABLE insumo (
    insumo_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_insumo VARCHAR (255) NOT NULL, 
    unidad_medida ENUM('kg', 'g', 'l', 'ml', 'pz'),
    cantidad_disponible DECIMAL(10, 2)
);


-- Tabla de inventario de productos generados (Galletas)
CREATE TABLE producto ( 
    producto_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    unidad_medida ENUM('kg', 'g', 'pz') NOT NULL,
    cantidad_disponible INT NOT NULL CHECK (cantidad_disponible >= 0),
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    peso_unidad DECIMAL(5, 2) NOT NULL,  -- Ej: 10 (gramos por galleta)
    fecha_caducidad DATE
);

-- Tabla de recetas (Es la relacion que existe entre la cantidad de insumos que se requiere por producto)
CREATE TABLE receta (
    receta_id INT PRIMARY KEY AUTO_INCREMENT,
    producto_id INT, 
    insumo_id INT,
    cantidad_necesaria DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES producto(producto_id),
    FOREIGN KEY (insumo_id) REFERENCES insumo(insumo_id)
);

-- Tabla de producción
CREATE TABLE produccion (
    produccion_id INT PRIMARY KEY AUTO_INCREMENT, 
    producto_id INT NOT NULL, 
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_finalizacion DATETIME NULL,
    FOREIGN KEY (producto_id) REFERENCES producto(producto_id)
);

-- Tabla de lote de producción
CREATE TABLE lote_produccion (
    lote_id INT PRIMARY KEY AUTO_INCREMENT,
    produccion_id INT NOT NULL,
    cantidad_galletas INT NOT NULL,
    fecha_caducidad DATE NOT NULL,
    FOREIGN KEY (produccion_id) REFERENCES produccion(produccion_id)
);

-- Tabla de consumo de insumos 
CREATE TABLE consumo_insumos (
    consumo_id INT PRIMARY KEY AUTO_INCREMENT,
    produccion_id INT NOT NULL,
    insumo_id INT NOT NULL,
    cantidad_usada DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (produccion_id) REFERENCES produccion(produccion_id),
    FOREIGN KEY (insumo_id) REFERENCES insumo(insumo_id)
);

-- Tabla de venta
CREATE TABLE venta (
    venta_id INT PRIMARY KEY AUTO_INCREMENT,
	persona_id INT NOT NULL,
	fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
    estatus_venta ENUM('Pagado', 'Pendiente', 'Cancelado') DEFAULT 'Pendiente',
	FOREIGN KEY (persona_id) REFERENCES persona(persona_id)
);

-- Tabla de detalle venta
CREATE TABLE detalle_venta (
	detalle_venta_id INT PRIMARY KEY AUTO_INCREMENT,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad DECIMAL(10,3) NOT NULL CHECK (cantidad > 0),
    unidad_medida ENUM('kg', 'g', 'pz') NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES producto(producto_id),
    FOREIGN KEY (venta_id) REFERENCES venta(venta_id)
 );  
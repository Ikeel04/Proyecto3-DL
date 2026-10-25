CREATE TABLE `categorias` (
  `id_categoria` int NOT NULL AUTO_INCREMENT COMMENT 'id de la categoría',
  `nombre` varchar(60) NOT NULL COMMENT 'nombre de la categoría',
  `descripcion` varchar(200) NOT NULL COMMENT 'descripción',
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='categorías de productos';

CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT COMMENT 'id del cliente',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del cliente',
  `ciudad` varchar(40) NOT NULL COMMENT 'ciudad de residencia',
  `fecha_registro` date NOT NULL COMMENT 'fecha de registro',
  `es_vip` tinyint(1) NOT NULL COMMENT '1 si el cliente es VIP',
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='clientes registrados en la tienda';

CREATE TABLE `detalle_pedido` (
  `id_detalle` int NOT NULL AUTO_INCREMENT COMMENT 'id de la línea',
  `id_pedido` int NOT NULL COMMENT 'id de pedido',
  `id_producto` int NOT NULL COMMENT 'id de producto',
  `cantidad` int NOT NULL COMMENT 'unidades compradas',
  `precio_unitario` decimal(10,2) NOT NULL COMMENT 'precio unitario',
  PRIMARY KEY (`id_detalle`),
  KEY `fk_detalle_pedido_id_pedido` (`id_pedido`),
  KEY `fk_detalle_pedido_id_producto` (`id_producto`),
  CONSTRAINT `fk_detalle_pedido_id_pedido` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `fk_detalle_pedido_id_producto` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=701 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='líneas de cada pedido';

CREATE TABLE `pagos` (
  `id_pago` int NOT NULL AUTO_INCREMENT COMMENT 'id del pago',
  `id_pedido` int NOT NULL COMMENT 'id de pedido',
  `metodo` varchar(20) NOT NULL COMMENT 'método de pago',
  `monto` decimal(10,2) NOT NULL COMMENT 'monto pagado',
  `fecha_pago` date NOT NULL COMMENT 'fecha del pago',
  PRIMARY KEY (`id_pago`),
  KEY `fk_pagos_id_pedido` (`id_pedido`),
  CONSTRAINT `fk_pagos_id_pedido` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`)
) ENGINE=InnoDB AUTO_INCREMENT=261 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='pagos registrados para los pedidos';

CREATE TABLE `pedidos` (
  `id_pedido` int NOT NULL AUTO_INCREMENT COMMENT 'id del pedido',
  `id_cliente` int NOT NULL COMMENT 'id de cliente',
  `fecha_pedido` date NOT NULL COMMENT 'fecha del pedido',
  `estado` varchar(20) NOT NULL COMMENT 'estado del pedido',
  `total` decimal(10,2) NOT NULL COMMENT 'monto total del pedido en quetzales',
  PRIMARY KEY (`id_pedido`),
  KEY `fk_pedidos_id_cliente` (`id_cliente`),
  CONSTRAINT `fk_pedidos_id_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='pedidos hechos por los clientes';

CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT COMMENT 'id del producto',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del producto',
  `id_categoria` int NOT NULL COMMENT 'id de categoría',
  `precio` decimal(10,2) NOT NULL COMMENT 'precio unitario en quetzales',
  `existencias` int NOT NULL COMMENT 'unidades en bodega',
  PRIMARY KEY (`id_producto`),
  KEY `fk_productos_id_categoria` (`id_categoria`),
  CONSTRAINT `fk_productos_id_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='catálogo de productos';
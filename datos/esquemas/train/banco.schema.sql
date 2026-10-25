CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT COMMENT 'id del cliente',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del cliente',
  `fecha_nacimiento` date NOT NULL COMMENT 'fecha de nacimiento',
  `segmento` varchar(20) NOT NULL COMMENT 'segmento comercial',
  `id_sucursal` int NOT NULL COMMENT 'sucursal donde abrió su relación',
  PRIMARY KEY (`id_cliente`),
  KEY `fk_clientes_id_sucursal` (`id_sucursal`),
  CONSTRAINT `fk_clientes_id_sucursal` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursales` (`id_sucursal`)
) ENGINE=InnoDB AUTO_INCREMENT=141 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='clientes del banco';

CREATE TABLE `creditos` (
  `id_credito` int NOT NULL AUTO_INCREMENT COMMENT 'id del crédito',
  `id_cliente` int NOT NULL COMMENT 'id de cliente',
  `monto` decimal(12,2) NOT NULL COMMENT 'monto del crédito',
  `tasa` decimal(5,2) NOT NULL COMMENT 'tasa anual en porcentaje',
  `plazo_meses` int NOT NULL COMMENT 'plazo en meses',
  `estado` varchar(15) NOT NULL COMMENT 'estado del crédito',
  `fecha_desembolso` date NOT NULL COMMENT 'fecha de desembolso',
  PRIMARY KEY (`id_credito`),
  KEY `fk_creditos_id_cliente` (`id_cliente`),
  CONSTRAINT `fk_creditos_id_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='créditos (préstamos bancarios) otorgados';

CREATE TABLE `cuentas` (
  `id_cuenta` int NOT NULL AUTO_INCREMENT COMMENT 'id de la cuenta',
  `id_cliente` int NOT NULL COMMENT 'id de cliente',
  `tipo` varchar(20) NOT NULL COMMENT 'tipo de cuenta',
  `saldo` decimal(12,2) NOT NULL COMMENT 'saldo actual en quetzales',
  `fecha_apertura` date NOT NULL COMMENT 'fecha de apertura',
  PRIMARY KEY (`id_cuenta`),
  KEY `fk_cuentas_id_cliente` (`id_cliente`),
  CONSTRAINT `fk_cuentas_id_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=221 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='cuentas bancarias';

CREATE TABLE `sucursales` (
  `id_sucursal` int NOT NULL AUTO_INCREMENT COMMENT 'id de la sucursal',
  `nombre` varchar(60) NOT NULL COMMENT 'nombre de la sucursal',
  `departamento` varchar(40) NOT NULL COMMENT 'departamento del país',
  PRIMARY KEY (`id_sucursal`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='agencias bancarias';

CREATE TABLE `transacciones` (
  `id_transaccion` int NOT NULL AUTO_INCREMENT COMMENT 'id de la transacción',
  `id_cuenta` int NOT NULL COMMENT 'id de cuenta',
  `tipo` varchar(20) NOT NULL COMMENT 'tipo de transacción',
  `monto` decimal(12,2) NOT NULL COMMENT 'monto en quetzales',
  `fecha` datetime NOT NULL COMMENT 'fecha de la transacción',
  PRIMARY KEY (`id_transaccion`),
  KEY `fk_transacciones_id_cuenta` (`id_cuenta`),
  CONSTRAINT `fk_transacciones_id_cuenta` FOREIGN KEY (`id_cuenta`) REFERENCES `cuentas` (`id_cuenta`)
) ENGINE=InnoDB AUTO_INCREMENT=1101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='movimientos de las cuentas';
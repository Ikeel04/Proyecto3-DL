CREATE TABLE `alm` (
  `alm_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del almacén',
  `nom_alm` varchar(60) NOT NULL COMMENT 'nombre del almacén',
  `cap_m3` int NOT NULL COMMENT 'capacidad en m3',
  PRIMARY KEY (`alm_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='almacenes / bodegas';

CREATE TABLE `emp_alm` (
  `emp_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del empleado',
  `nom_emp` varchar(80) NOT NULL COMMENT 'nombre del empleado',
  `alm_id` int NOT NULL COMMENT 'id de almacén',
  `sal_mens` decimal(10,2) NOT NULL COMMENT 'salario mensual',
  `f_ingreso` date NOT NULL COMMENT 'fecha de ingreso',
  PRIMARY KEY (`emp_id`),
  KEY `fk_emp_alm_alm_id` (`alm_id`),
  CONSTRAINT `fk_emp_alm_alm_id` FOREIGN KEY (`alm_id`) REFERENCES `alm` (`alm_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='empleados de bodega';

CREATE TABLE `mov_inv` (
  `mov_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del movimiento',
  `prod_id` int NOT NULL COMMENT 'id de producto',
  `alm_id` int NOT NULL COMMENT 'id de almacén',
  `tipo_mov` char(1) NOT NULL COMMENT 'E = entrada, S = salida',
  `cant` int NOT NULL COMMENT 'cantidad de unidades',
  `fec_mov` date NOT NULL COMMENT 'fecha del movimiento',
  PRIMARY KEY (`mov_id`),
  KEY `fk_mov_inv_prod_id` (`prod_id`),
  KEY `fk_mov_inv_alm_id` (`alm_id`),
  CONSTRAINT `fk_mov_inv_alm_id` FOREIGN KEY (`alm_id`) REFERENCES `alm` (`alm_id`),
  CONSTRAINT `fk_mov_inv_prod_id` FOREIGN KEY (`prod_id`) REFERENCES `prod` (`prod_id`)
) ENGINE=InnoDB AUTO_INCREMENT=901 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='movimientos de inventario (entradas y salidas)';

CREATE TABLE `prod` (
  `prod_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del producto',
  `desc_prod` varchar(80) NOT NULL COMMENT 'descripción del producto',
  `prov_id` int NOT NULL COMMENT 'id de proveedor',
  `cat_prod` varchar(20) NOT NULL COMMENT 'categoría del producto',
  `costo_u` decimal(10,2) NOT NULL COMMENT 'costo unitario en quetzales',
  `stk_min` int NOT NULL COMMENT 'stock mínimo permitido',
  PRIMARY KEY (`prod_id`),
  KEY `fk_prod_prov_id` (`prov_id`),
  CONSTRAINT `fk_prod_prov_id` FOREIGN KEY (`prov_id`) REFERENCES `prov` (`prov_id`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='productos de inventario';

CREATE TABLE `prov` (
  `prov_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del proveedor',
  `nom_prov` varchar(80) NOT NULL COMMENT 'nombre del proveedor',
  `pais` varchar(30) NOT NULL COMMENT 'país del proveedor',
  PRIMARY KEY (`prov_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='proveedores';
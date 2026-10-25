CREATE TABLE `customers` (
  `cust_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del cliente',
  `cust_name` varchar(80) NOT NULL COMMENT 'nombre del cliente',
  `city` varchar(40) NOT NULL COMMENT 'ciudad',
  `cust_type` varchar(15) NOT NULL COMMENT 'tipo de cliente',
  PRIMARY KEY (`cust_id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='clientes que reciben envíos';

CREATE TABLE `drivers` (
  `driver_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del piloto',
  `driver_name` varchar(80) NOT NULL COMMENT 'nombre del piloto',
  `license_type` char(1) NOT NULL COMMENT 'tipo de licencia',
  `hired_on` date NOT NULL COMMENT 'fecha de contratación',
  `wh_id` int NOT NULL COMMENT 'centro asignado',
  PRIMARY KEY (`driver_id`),
  KEY `fk_drivers_wh_id` (`wh_id`),
  CONSTRAINT `fk_drivers_wh_id` FOREIGN KEY (`wh_id`) REFERENCES `warehouses` (`wh_id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='pilotos repartidores';

CREATE TABLE `shipments` (
  `ship_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del envío',
  `cust_id` int NOT NULL COMMENT 'id de cliente',
  `driver_id` int NOT NULL COMMENT 'id de piloto',
  `vehicle_id` int NOT NULL COMMENT 'id de vehículo',
  `ship_date` date NOT NULL COMMENT 'fecha de envío',
  `weight_kg` decimal(8,2) NOT NULL COMMENT 'peso en kg',
  `cost` decimal(10,2) NOT NULL COMMENT 'costo del envío en quetzales',
  `status` varchar(12) NOT NULL COMMENT 'delivered = entregado, in_transit = en tránsito, returned = devuelto',
  PRIMARY KEY (`ship_id`),
  KEY `fk_shipments_cust_id` (`cust_id`),
  KEY `fk_shipments_driver_id` (`driver_id`),
  KEY `fk_shipments_vehicle_id` (`vehicle_id`),
  CONSTRAINT `fk_shipments_cust_id` FOREIGN KEY (`cust_id`) REFERENCES `customers` (`cust_id`),
  CONSTRAINT `fk_shipments_driver_id` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`driver_id`),
  CONSTRAINT `fk_shipments_vehicle_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`)
) ENGINE=InnoDB AUTO_INCREMENT=901 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='envíos realizados';

CREATE TABLE `vehicles` (
  `vehicle_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del vehículo',
  `plate` varchar(10) NOT NULL COMMENT 'placa',
  `vtype` varchar(15) NOT NULL COMMENT 'tipo de vehículo',
  `capacity_kg` int NOT NULL COMMENT 'capacidad de carga en kg',
  PRIMARY KEY (`vehicle_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='vehículos de la flota';

CREATE TABLE `warehouses` (
  `wh_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del centro',
  `wh_name` varchar(60) NOT NULL COMMENT 'nombre del centro de distribución',
  `region` varchar(20) NOT NULL COMMENT 'región',
  PRIMARY KEY (`wh_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='centros de distribución';
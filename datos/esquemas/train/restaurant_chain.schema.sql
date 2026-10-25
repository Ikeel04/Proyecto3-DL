CREATE TABLE `branches` (
  `branch_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la sucursal',
  `branch_name` varchar(60) NOT NULL COMMENT 'nombre de la sucursal',
  `city` varchar(40) NOT NULL COMMENT 'ciudad',
  `opened_on` date NOT NULL COMMENT 'fecha de apertura',
  PRIMARY KEY (`branch_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='sucursales del restaurante';

CREATE TABLE `dishes` (
  `dish_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del platillo',
  `dish_name` varchar(80) NOT NULL COMMENT 'nombre del platillo',
  `category` varchar(20) NOT NULL COMMENT 'categoría del menú',
  `price` decimal(8,2) NOT NULL COMMENT 'precio en quetzales',
  `is_vegan` tinyint(1) NOT NULL COMMENT '1 si es vegano',
  PRIMARY KEY (`dish_id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='platillos del menú';

CREATE TABLE `order_items` (
  `item_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del ítem',
  `order_id` int NOT NULL COMMENT 'id de orden',
  `dish_id` int NOT NULL COMMENT 'id de platillo',
  `qty` int NOT NULL COMMENT 'cantidad pedida',
  PRIMARY KEY (`item_id`),
  KEY `fk_order_items_order_id` (`order_id`),
  KEY `fk_order_items_dish_id` (`dish_id`),
  CONSTRAINT `fk_order_items_dish_id` FOREIGN KEY (`dish_id`) REFERENCES `dishes` (`dish_id`),
  CONSTRAINT `fk_order_items_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='platillos incluidos en cada orden';

CREATE TABLE `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la orden',
  `waiter_id` int NOT NULL COMMENT 'id de mesero',
  `order_time` datetime NOT NULL COMMENT 'fecha y hora',
  `tip` decimal(8,2) NOT NULL COMMENT 'propina en quetzales',
  `payment_type` varchar(15) NOT NULL COMMENT 'card = tarjeta, cash = efectivo',
  PRIMARY KEY (`order_id`),
  KEY `fk_orders_waiter_id` (`waiter_id`),
  CONSTRAINT `fk_orders_waiter_id` FOREIGN KEY (`waiter_id`) REFERENCES `waiters` (`waiter_id`)
) ENGINE=InnoDB AUTO_INCREMENT=401 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='órdenes (cuentas) atendidas';

CREATE TABLE `waiters` (
  `waiter_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del mesero',
  `waiter_name` varchar(80) NOT NULL COMMENT 'nombre del mesero',
  `branch_id` int NOT NULL COMMENT 'id de sucursal',
  `shift` varchar(10) NOT NULL COMMENT 'turno de trabajo',
  PRIMARY KEY (`waiter_id`),
  KEY `fk_waiters_branch_id` (`branch_id`),
  CONSTRAINT `fk_waiters_branch_id` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='meseros';
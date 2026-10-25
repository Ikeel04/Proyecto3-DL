CREATE TABLE `bkg` (
  `bkg_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la reservación',
  `gst_id` int NOT NULL COMMENT 'id de huésped',
  `rm_id` int NOT NULL COMMENT 'id de habitación',
  `chk_in` date NOT NULL COMMENT 'fecha de check-in',
  `nights` int NOT NULL COMMENT 'número de noches',
  `amt` decimal(10,2) NOT NULL COMMENT 'monto total cobrado',
  `sts` varchar(12) NOT NULL COMMENT 'completed = completada, cancelled = cancelada, no-show = no se presentó',
  PRIMARY KEY (`bkg_id`),
  KEY `fk_bkg_gst_id` (`gst_id`),
  KEY `fk_bkg_rm_id` (`rm_id`),
  CONSTRAINT `fk_bkg_gst_id` FOREIGN KEY (`gst_id`) REFERENCES `gst` (`gst_id`),
  CONSTRAINT `fk_bkg_rm_id` FOREIGN KEY (`rm_id`) REFERENCES `rm` (`rm_id`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='reservaciones';

CREATE TABLE `gst` (
  `gst_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del huésped',
  `gst_nm` varchar(80) NOT NULL COMMENT 'nombre del huésped',
  `ctry` varchar(40) NOT NULL COMMENT 'país de origen',
  `email` varchar(80) NOT NULL COMMENT 'correo electrónico',
  PRIMARY KEY (`gst_id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='huéspedes';

CREATE TABLE `htl` (
  `htl_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del hotel',
  `htl_nm` varchar(60) NOT NULL COMMENT 'nombre del hotel',
  `city` varchar(40) NOT NULL COMMENT 'ciudad',
  `stars` int NOT NULL COMMENT 'categoría en estrellas',
  PRIMARY KEY (`htl_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='hoteles de la cadena';

CREATE TABLE `rm` (
  `rm_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la habitación',
  `htl_id` int NOT NULL COMMENT 'id de hotel',
  `rm_no` varchar(10) NOT NULL COMMENT 'número de habitación',
  `rm_type` varchar(15) NOT NULL COMMENT 'tipo de habitación',
  `rate` decimal(8,2) NOT NULL COMMENT 'tarifa por noche en quetzales',
  PRIMARY KEY (`rm_id`),
  KEY `fk_rm_htl_id` (`htl_id`),
  CONSTRAINT `fk_rm_htl_id` FOREIGN KEY (`htl_id`) REFERENCES `htl` (`htl_id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='habitaciones';

CREATE TABLE `svc_chg` (
  `chg_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del cargo',
  `bkg_id` int NOT NULL COMMENT 'id de reservación',
  `svc` varchar(20) NOT NULL COMMENT 'servicio consumido',
  `chg_amt` decimal(8,2) NOT NULL COMMENT 'monto del cargo',
  PRIMARY KEY (`chg_id`),
  KEY `fk_svc_chg_bkg_id` (`bkg_id`),
  CONSTRAINT `fk_svc_chg_bkg_id` FOREIGN KEY (`bkg_id`) REFERENCES `bkg` (`bkg_id`)
) ENGINE=InnoDB AUTO_INCREMENT=501 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='cargos por servicios adicionales';
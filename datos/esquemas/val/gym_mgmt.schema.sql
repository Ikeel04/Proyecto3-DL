CREATE TABLE `att` (
  `att_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la asistencia',
  `cls_id` int NOT NULL COMMENT 'id de clase',
  `mbr_id` int NOT NULL COMMENT 'id de miembro',
  `rtg` int DEFAULT NULL COMMENT 'calificación de 1 a 5 que dio el miembro, NULL si no calificó',
  PRIMARY KEY (`att_id`),
  KEY `fk_att_cls_id` (`cls_id`),
  KEY `fk_att_mbr_id` (`mbr_id`),
  CONSTRAINT `fk_att_cls_id` FOREIGN KEY (`cls_id`) REFERENCES `cls` (`cls_id`),
  CONSTRAINT `fk_att_mbr_id` FOREIGN KEY (`mbr_id`) REFERENCES `mbr` (`mbr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=901 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='asistencia de miembros a clases';

CREATE TABLE `cls` (
  `cls_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la clase',
  `trnr_id` int NOT NULL COMMENT 'id de entrenador',
  `cls_dt` datetime NOT NULL COMMENT 'fecha y hora de la clase',
  `cap` int NOT NULL COMMENT 'cupo máximo',
  PRIMARY KEY (`cls_id`),
  KEY `fk_cls_trnr_id` (`trnr_id`),
  CONSTRAINT `fk_cls_trnr_id` FOREIGN KEY (`trnr_id`) REFERENCES `trnr` (`trnr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=141 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='clases grupales programadas';

CREATE TABLE `loc` (
  `loc_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la sede',
  `loc_nm` varchar(60) NOT NULL COMMENT 'nombre de la sede',
  `opn_dt` date NOT NULL COMMENT 'fecha de apertura',
  PRIMARY KEY (`loc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='sedes del gimnasio';

CREATE TABLE `mbr` (
  `mbr_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del miembro',
  `mbr_nm` varchar(80) NOT NULL COMMENT 'nombre del miembro',
  `plan_id` int NOT NULL COMMENT 'id de plan',
  `loc_id` int NOT NULL COMMENT 'sede principal',
  `jn_dt` date NOT NULL COMMENT 'fecha de inscripción',
  `gndr` char(1) NOT NULL COMMENT 'F o M',
  PRIMARY KEY (`mbr_id`),
  KEY `fk_mbr_plan_id` (`plan_id`),
  KEY `fk_mbr_loc_id` (`loc_id`),
  CONSTRAINT `fk_mbr_loc_id` FOREIGN KEY (`loc_id`) REFERENCES `loc` (`loc_id`),
  CONSTRAINT `fk_mbr_plan_id` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`plan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='miembros (clientes) del gimnasio';

CREATE TABLE `pay` (
  `pay_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del pago',
  `mbr_id` int NOT NULL COMMENT 'id de miembro',
  `pay_dt` date NOT NULL COMMENT 'fecha de pago',
  `amt` decimal(8,2) NOT NULL COMMENT 'monto pagado',
  `mthd` varchar(10) NOT NULL COMMENT 'card = tarjeta, cash = efectivo, transfer = transferencia',
  PRIMARY KEY (`pay_id`),
  KEY `fk_pay_mbr_id` (`mbr_id`),
  CONSTRAINT `fk_pay_mbr_id` FOREIGN KEY (`mbr_id`) REFERENCES `mbr` (`mbr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=701 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='pagos de membresía';

CREATE TABLE `plan` (
  `plan_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del plan',
  `plan_nm` varchar(30) NOT NULL COMMENT 'nombre del plan',
  `mo_fee` decimal(8,2) NOT NULL COMMENT 'cuota mensual en quetzales',
  PRIMARY KEY (`plan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='planes de membresía';

CREATE TABLE `trnr` (
  `trnr_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del entrenador',
  `trnr_nm` varchar(80) NOT NULL COMMENT 'nombre del entrenador',
  `loc_id` int NOT NULL COMMENT 'id de sede',
  `spec` varchar(20) NOT NULL COMMENT 'especialidad',
  PRIMARY KEY (`trnr_id`),
  KEY `fk_trnr_loc_id` (`loc_id`),
  CONSTRAINT `fk_trnr_loc_id` FOREIGN KEY (`loc_id`) REFERENCES `loc` (`loc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='entrenadores';
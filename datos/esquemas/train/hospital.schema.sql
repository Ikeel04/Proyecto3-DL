CREATE TABLE `citas` (
  `id_cita` int NOT NULL AUTO_INCREMENT COMMENT 'id de la cita',
  `id_paciente` int NOT NULL COMMENT 'id de paciente',
  `id_medico` int NOT NULL COMMENT 'id de médico',
  `fecha_hora` datetime NOT NULL COMMENT 'fecha de la cita',
  `estado` varchar(15) NOT NULL COMMENT 'estado de la cita',
  `costo` decimal(8,2) NOT NULL COMMENT 'costo cobrado',
  PRIMARY KEY (`id_cita`),
  KEY `fk_citas_id_paciente` (`id_paciente`),
  KEY `fk_citas_id_medico` (`id_medico`),
  CONSTRAINT `fk_citas_id_medico` FOREIGN KEY (`id_medico`) REFERENCES `medicos` (`id_medico`),
  CONSTRAINT `fk_citas_id_paciente` FOREIGN KEY (`id_paciente`) REFERENCES `pacientes` (`id_paciente`)
) ENGINE=InnoDB AUTO_INCREMENT=801 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='citas médicas';

CREATE TABLE `especialidades` (
  `id_especialidad` int NOT NULL AUTO_INCREMENT COMMENT 'id de la especialidad',
  `nombre` varchar(60) NOT NULL COMMENT 'nombre de la especialidad',
  PRIMARY KEY (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='especialidades médicas';

CREATE TABLE `medicos` (
  `id_medico` int NOT NULL AUTO_INCREMENT COMMENT 'id del médico',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del médico',
  `id_especialidad` int NOT NULL COMMENT 'id de especialidad',
  `colegiado` int NOT NULL COMMENT 'número de colegiado',
  `tarifa_consulta` decimal(8,2) NOT NULL COMMENT 'tarifa por consulta en quetzales',
  PRIMARY KEY (`id_medico`),
  KEY `fk_medicos_id_especialidad` (`id_especialidad`),
  CONSTRAINT `fk_medicos_id_especialidad` FOREIGN KEY (`id_especialidad`) REFERENCES `especialidades` (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='médicos';

CREATE TABLE `pacientes` (
  `id_paciente` int NOT NULL AUTO_INCREMENT COMMENT 'id del paciente',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del paciente',
  `sexo` char(1) NOT NULL COMMENT 'F o M',
  `fecha_nacimiento` date NOT NULL COMMENT 'fecha de nacimiento',
  `seguro` varchar(20) DEFAULT NULL COMMENT 'tipo de seguro, NULL si no se registró',
  PRIMARY KEY (`id_paciente`)
) ENGINE=InnoDB AUTO_INCREMENT=221 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='pacientes';

CREATE TABLE `recetas` (
  `id_receta` int NOT NULL AUTO_INCREMENT COMMENT 'id de la receta',
  `id_cita` int NOT NULL COMMENT 'id de cita',
  `medicamento` varchar(60) NOT NULL COMMENT 'medicamento',
  `dosis_mg` int NOT NULL COMMENT 'dosis en mg',
  `dias` int NOT NULL COMMENT 'días de tratamiento',
  PRIMARY KEY (`id_receta`),
  KEY `fk_recetas_id_cita` (`id_cita`),
  CONSTRAINT `fk_recetas_id_cita` FOREIGN KEY (`id_cita`) REFERENCES `citas` (`id_cita`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='medicamentos recetados en cada cita';
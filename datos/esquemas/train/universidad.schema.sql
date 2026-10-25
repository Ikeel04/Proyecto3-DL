CREATE TABLE `carreras` (
  `id_carrera` int NOT NULL AUTO_INCREMENT COMMENT 'id de la carrera',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre de la carrera',
  `id_facultad` int NOT NULL COMMENT 'id de facultad',
  `duracion_anios` int NOT NULL COMMENT 'duración en años',
  PRIMARY KEY (`id_carrera`),
  KEY `fk_carreras_id_facultad` (`id_facultad`),
  CONSTRAINT `fk_carreras_id_facultad` FOREIGN KEY (`id_facultad`) REFERENCES `facultades` (`id_facultad`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='carreras que ofrece cada facultad';

CREATE TABLE `cursos` (
  `id_curso` int NOT NULL AUTO_INCREMENT COMMENT 'id del curso',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del curso',
  `creditos` int NOT NULL COMMENT 'créditos',
  `id_profesor` int NOT NULL COMMENT 'id de profesor',
  PRIMARY KEY (`id_curso`),
  KEY `fk_cursos_id_profesor` (`id_profesor`),
  CONSTRAINT `fk_cursos_id_profesor` FOREIGN KEY (`id_profesor`) REFERENCES `profesores` (`id_profesor`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='cursos impartidos';

CREATE TABLE `estudiantes` (
  `carne` int NOT NULL AUTO_INCREMENT COMMENT 'número de carné',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del estudiante',
  `id_carrera` int NOT NULL COMMENT 'id de carrera',
  `anio_ingreso` int NOT NULL COMMENT 'año de ingreso',
  `promedio` decimal(5,2) NOT NULL COMMENT 'promedio acumulado sobre 100',
  `becado` tinyint(1) NOT NULL COMMENT '1 si tiene beca',
  PRIMARY KEY (`carne`),
  KEY `fk_estudiantes_id_carrera` (`id_carrera`),
  CONSTRAINT `fk_estudiantes_id_carrera` FOREIGN KEY (`id_carrera`) REFERENCES `carreras` (`id_carrera`)
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='estudiantes inscritos';

CREATE TABLE `facultades` (
  `id_facultad` int NOT NULL AUTO_INCREMENT COMMENT 'id de la facultad',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre de la facultad',
  `edificio` varchar(10) NOT NULL COMMENT 'edificio',
  PRIMARY KEY (`id_facultad`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='facultades de la universidad';

CREATE TABLE `inscripciones` (
  `id_inscripcion` int NOT NULL AUTO_INCREMENT COMMENT 'id de la inscripción',
  `carne` int NOT NULL COMMENT 'id de estudiante',
  `id_curso` int NOT NULL COMMENT 'id de curso',
  `semestre` varchar(10) NOT NULL COMMENT 'semestre',
  `nota` decimal(5,2) DEFAULT NULL COMMENT 'nota final, NULL si no ha terminado',
  PRIMARY KEY (`id_inscripcion`),
  KEY `fk_inscripciones_carne` (`carne`),
  KEY `fk_inscripciones_id_curso` (`id_curso`),
  CONSTRAINT `fk_inscripciones_carne` FOREIGN KEY (`carne`) REFERENCES `estudiantes` (`carne`),
  CONSTRAINT `fk_inscripciones_id_curso` FOREIGN KEY (`id_curso`) REFERENCES `cursos` (`id_curso`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='asignación de estudiantes a cursos';

CREATE TABLE `profesores` (
  `id_profesor` int NOT NULL AUTO_INCREMENT COMMENT 'id del profesor',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del profesor',
  `id_facultad` int NOT NULL COMMENT 'id de facultad',
  `grado` varchar(20) NOT NULL COMMENT 'grado académico',
  `fecha_contratacion` date NOT NULL COMMENT 'fecha de contratación',
  PRIMARY KEY (`id_profesor`),
  KEY `fk_profesores_id_facultad` (`id_facultad`),
  CONSTRAINT `fk_profesores_id_facultad` FOREIGN KEY (`id_facultad`) REFERENCES `facultades` (`id_facultad`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='catedráticos';
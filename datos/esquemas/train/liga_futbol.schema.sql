CREATE TABLE `equipos` (
  `id_equipo` int NOT NULL AUTO_INCREMENT COMMENT 'id del equipo',
  `nombre` varchar(60) NOT NULL COMMENT 'nombre del equipo',
  `id_estadio` int NOT NULL COMMENT 'estadio local',
  `anio_fundacion` int NOT NULL COMMENT 'año de fundación',
  PRIMARY KEY (`id_equipo`),
  KEY `fk_equipos_id_estadio` (`id_estadio`),
  CONSTRAINT `fk_equipos_id_estadio` FOREIGN KEY (`id_estadio`) REFERENCES `estadios` (`id_estadio`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='equipos de la liga';

CREATE TABLE `estadios` (
  `id_estadio` int NOT NULL AUTO_INCREMENT COMMENT 'id del estadio',
  `nombre` varchar(60) NOT NULL COMMENT 'nombre del estadio',
  `ciudad` varchar(40) NOT NULL COMMENT 'ciudad',
  `capacidad` int NOT NULL COMMENT 'capacidad',
  PRIMARY KEY (`id_estadio`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='estadios';

CREATE TABLE `goles` (
  `id_gol` int NOT NULL AUTO_INCREMENT COMMENT 'id del gol',
  `id_partido` int NOT NULL COMMENT 'id de partido',
  `id_jugador` int NOT NULL COMMENT 'jugador que anotó',
  `minuto` int NOT NULL COMMENT 'minuto',
  `tipo` varchar(15) NOT NULL COMMENT 'tipo de gol',
  PRIMARY KEY (`id_gol`),
  KEY `fk_goles_id_partido` (`id_partido`),
  KEY `fk_goles_id_jugador` (`id_jugador`),
  CONSTRAINT `fk_goles_id_jugador` FOREIGN KEY (`id_jugador`) REFERENCES `jugadores` (`id_jugador`),
  CONSTRAINT `fk_goles_id_partido` FOREIGN KEY (`id_partido`) REFERENCES `partidos` (`id_partido`)
) ENGINE=InnoDB AUTO_INCREMENT=381 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='goles anotados';

CREATE TABLE `jugadores` (
  `id_jugador` int NOT NULL AUTO_INCREMENT COMMENT 'id del jugador',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del jugador',
  `id_equipo` int NOT NULL COMMENT 'id de equipo',
  `posicion` varchar(20) NOT NULL COMMENT 'posición',
  `fecha_nacimiento` date NOT NULL COMMENT 'fecha de nacimiento',
  `salario` decimal(10,2) NOT NULL COMMENT 'salario mensual en quetzales',
  PRIMARY KEY (`id_jugador`),
  KEY `fk_jugadores_id_equipo` (`id_equipo`),
  CONSTRAINT `fk_jugadores_id_equipo` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id_equipo`)
) ENGINE=InnoDB AUTO_INCREMENT=181 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='jugadores';

CREATE TABLE `partidos` (
  `id_partido` int NOT NULL AUTO_INCREMENT COMMENT 'id del partido',
  `id_local` int NOT NULL COMMENT 'equipo local',
  `id_visitante` int NOT NULL COMMENT 'equipo visitante',
  `fecha` date NOT NULL COMMENT 'fecha del partido',
  `goles_local` int NOT NULL COMMENT 'goles del local',
  `goles_visitante` int NOT NULL COMMENT 'goles del visitante',
  `asistencia` int NOT NULL COMMENT 'espectadores',
  PRIMARY KEY (`id_partido`),
  KEY `fk_partidos_id_local` (`id_local`),
  KEY `fk_partidos_id_visitante` (`id_visitante`),
  CONSTRAINT `fk_partidos_id_local` FOREIGN KEY (`id_local`) REFERENCES `equipos` (`id_equipo`),
  CONSTRAINT `fk_partidos_id_visitante` FOREIGN KEY (`id_visitante`) REFERENCES `equipos` (`id_equipo`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='partidos jugados';
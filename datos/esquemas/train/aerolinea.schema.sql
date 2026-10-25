CREATE TABLE `aeropuertos` (
  `codigo_iata` char(3) NOT NULL COMMENT 'código IATA',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del aeropuerto',
  `pais` varchar(40) NOT NULL COMMENT 'país',
  PRIMARY KEY (`codigo_iata`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='aeropuertos';

CREATE TABLE `aviones` (
  `id_avion` int NOT NULL AUTO_INCREMENT COMMENT 'id del avión',
  `matricula` varchar(10) NOT NULL COMMENT 'matrícula',
  `modelo` varchar(30) NOT NULL COMMENT 'modelo',
  `capacidad` int NOT NULL COMMENT 'número de asientos',
  PRIMARY KEY (`id_avion`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='flota de aviones';

CREATE TABLE `pasajeros` (
  `id_pasajero` int NOT NULL AUTO_INCREMENT COMMENT 'id del pasajero',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del pasajero',
  `nacionalidad` varchar(40) NOT NULL COMMENT 'nacionalidad',
  `millas` int NOT NULL COMMENT 'millas acumuladas',
  PRIMARY KEY (`id_pasajero`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='pasajeros';

CREATE TABLE `reservas` (
  `id_reserva` int NOT NULL AUTO_INCREMENT COMMENT 'id de la reserva',
  `id_vuelo` int NOT NULL COMMENT 'id de vuelo',
  `id_pasajero` int NOT NULL COMMENT 'id de pasajero',
  `clase` varchar(15) NOT NULL COMMENT 'clase',
  `precio` decimal(10,2) NOT NULL COMMENT 'precio en quetzales',
  `fecha_reserva` date NOT NULL COMMENT 'fecha de la reserva',
  PRIMARY KEY (`id_reserva`),
  KEY `fk_reservas_id_vuelo` (`id_vuelo`),
  KEY `fk_reservas_id_pasajero` (`id_pasajero`),
  CONSTRAINT `fk_reservas_id_pasajero` FOREIGN KEY (`id_pasajero`) REFERENCES `pasajeros` (`id_pasajero`),
  CONSTRAINT `fk_reservas_id_vuelo` FOREIGN KEY (`id_vuelo`) REFERENCES `vuelos` (`id_vuelo`)
) ENGINE=InnoDB AUTO_INCREMENT=701 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='reservas de pasajeros en vuelos';

CREATE TABLE `vuelos` (
  `id_vuelo` int NOT NULL AUTO_INCREMENT COMMENT 'id del vuelo',
  `origen` char(3) NOT NULL COMMENT 'código IATA de origen',
  `destino` char(3) NOT NULL COMMENT 'código IATA de destino',
  `id_avion` int NOT NULL COMMENT 'id de avión',
  `fecha_salida` datetime NOT NULL COMMENT 'fecha de salida',
  `duracion_min` int NOT NULL COMMENT 'duración en minutos',
  `estado` varchar(15) NOT NULL COMMENT 'estado del vuelo',
  PRIMARY KEY (`id_vuelo`),
  KEY `fk_vuelos_origen` (`origen`),
  KEY `fk_vuelos_destino` (`destino`),
  KEY `fk_vuelos_id_avion` (`id_avion`),
  CONSTRAINT `fk_vuelos_destino` FOREIGN KEY (`destino`) REFERENCES `aeropuertos` (`codigo_iata`),
  CONSTRAINT `fk_vuelos_id_avion` FOREIGN KEY (`id_avion`) REFERENCES `aviones` (`id_avion`),
  CONSTRAINT `fk_vuelos_origen` FOREIGN KEY (`origen`) REFERENCES `aeropuertos` (`codigo_iata`)
) ENGINE=InnoDB AUTO_INCREMENT=251 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='vuelos programados';
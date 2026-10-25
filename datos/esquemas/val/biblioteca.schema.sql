CREATE TABLE `autores` (
  `id_autor` int NOT NULL AUTO_INCREMENT COMMENT 'id del autor',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del autor',
  `nacionalidad` varchar(40) NOT NULL COMMENT 'nacionalidad',
  PRIMARY KEY (`id_autor`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='autores de los libros';

CREATE TABLE `editoriales` (
  `id_editorial` int NOT NULL AUTO_INCREMENT COMMENT 'id de la editorial',
  `nombre` varchar(60) NOT NULL COMMENT 'nombre de la editorial',
  `pais` varchar(40) NOT NULL COMMENT 'país',
  PRIMARY KEY (`id_editorial`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='editoriales';

CREATE TABLE `ejemplares` (
  `id_ejemplar` int NOT NULL AUTO_INCREMENT COMMENT 'id del ejemplar',
  `id_libro` int NOT NULL COMMENT 'id de libro',
  `estado` varchar(15) NOT NULL COMMENT 'estado físico',
  `fecha_adquisicion` date NOT NULL COMMENT 'fecha de adquisición',
  PRIMARY KEY (`id_ejemplar`),
  KEY `fk_ejemplares_id_libro` (`id_libro`),
  CONSTRAINT `fk_ejemplares_id_libro` FOREIGN KEY (`id_libro`) REFERENCES `libros` (`id_libro`)
) ENGINE=InnoDB AUTO_INCREMENT=221 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='copias físicas de cada libro';

CREATE TABLE `libros` (
  `id_libro` int NOT NULL AUTO_INCREMENT COMMENT 'id del libro',
  `titulo` varchar(120) NOT NULL COMMENT 'título',
  `id_autor` int NOT NULL COMMENT 'id de autor',
  `id_editorial` int NOT NULL COMMENT 'id de editorial',
  `anio_publicacion` int NOT NULL COMMENT 'año de publicación',
  `genero` varchar(20) NOT NULL COMMENT 'género',
  `paginas` int NOT NULL COMMENT 'número de páginas',
  PRIMARY KEY (`id_libro`),
  KEY `fk_libros_id_autor` (`id_autor`),
  KEY `fk_libros_id_editorial` (`id_editorial`),
  CONSTRAINT `fk_libros_id_autor` FOREIGN KEY (`id_autor`) REFERENCES `autores` (`id_autor`),
  CONSTRAINT `fk_libros_id_editorial` FOREIGN KEY (`id_editorial`) REFERENCES `editoriales` (`id_editorial`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='títulos del catálogo';

CREATE TABLE `prestamos` (
  `id_prestamo` int NOT NULL AUTO_INCREMENT COMMENT 'id del préstamo',
  `id_ejemplar` int NOT NULL COMMENT 'id de ejemplar',
  `id_socio` int NOT NULL COMMENT 'id de socio',
  `fecha_prestamo` date NOT NULL COMMENT 'fecha del préstamo',
  `fecha_devolucion` date DEFAULT NULL COMMENT 'NULL si no se ha devuelto',
  `multa` decimal(8,2) NOT NULL COMMENT 'multa cobrada en quetzales',
  PRIMARY KEY (`id_prestamo`),
  KEY `fk_prestamos_id_ejemplar` (`id_ejemplar`),
  KEY `fk_prestamos_id_socio` (`id_socio`),
  CONSTRAINT `fk_prestamos_id_ejemplar` FOREIGN KEY (`id_ejemplar`) REFERENCES `ejemplares` (`id_ejemplar`),
  CONSTRAINT `fk_prestamos_id_socio` FOREIGN KEY (`id_socio`) REFERENCES `socios` (`id_socio`)
) ENGINE=InnoDB AUTO_INCREMENT=651 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='préstamos de ejemplares a socios';

CREATE TABLE `socios` (
  `id_socio` int NOT NULL AUTO_INCREMENT COMMENT 'id del socio',
  `nombre` varchar(80) NOT NULL COMMENT 'nombre del socio',
  `tipo` varchar(15) NOT NULL COMMENT 'tipo de socio',
  `fecha_alta` date NOT NULL COMMENT 'fecha de alta',
  PRIMARY KEY (`id_socio`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='socios de la biblioteca';
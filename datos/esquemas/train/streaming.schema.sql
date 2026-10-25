CREATE TABLE `genres` (
  `genre_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del género',
  `genre_name` varchar(40) NOT NULL COMMENT 'nombre del género',
  PRIMARY KEY (`genre_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='géneros';

CREATE TABLE `ratings` (
  `rating_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la calificación',
  `user_id` int NOT NULL COMMENT 'id de usuario',
  `title_id` int NOT NULL COMMENT 'id de título',
  `stars` int NOT NULL COMMENT 'calificación de 1 a 5',
  `rated_on` date NOT NULL COMMENT 'fecha de calificación',
  PRIMARY KEY (`rating_id`),
  KEY `fk_ratings_user_id` (`user_id`),
  KEY `fk_ratings_title_id` (`title_id`),
  CONSTRAINT `fk_ratings_title_id` FOREIGN KEY (`title_id`) REFERENCES `titles` (`title_id`),
  CONSTRAINT `fk_ratings_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=501 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='calificaciones de usuarios';

CREATE TABLE `titles` (
  `title_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del título',
  `title` varchar(100) NOT NULL COMMENT 'nombre de la película o serie',
  `genre_id` int NOT NULL COMMENT 'id de género',
  `kind` varchar(10) NOT NULL COMMENT 'movie = película, series = serie',
  `release_year` int NOT NULL COMMENT 'año de estreno',
  `duration_min` int NOT NULL COMMENT 'duración en minutos',
  PRIMARY KEY (`title_id`),
  KEY `fk_titles_genre_id` (`genre_id`),
  CONSTRAINT `fk_titles_genre_id` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`genre_id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='películas y series del catálogo';

CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del usuario',
  `username` varchar(60) NOT NULL COMMENT 'nombre del usuario',
  `country` varchar(40) NOT NULL COMMENT 'país',
  `signup_date` date NOT NULL COMMENT 'fecha de registro',
  `plan` varchar(15) NOT NULL COMMENT 'plan de suscripción',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='usuarios de la plataforma';

CREATE TABLE `views` (
  `view_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la reproducción',
  `user_id` int NOT NULL COMMENT 'id de usuario',
  `title_id` int NOT NULL COMMENT 'id de título',
  `watched_at` datetime NOT NULL COMMENT 'fecha y hora',
  `minutes` int NOT NULL COMMENT 'minutos vistos',
  PRIMARY KEY (`view_id`),
  KEY `fk_views_user_id` (`user_id`),
  KEY `fk_views_title_id` (`title_id`),
  CONSTRAINT `fk_views_title_id` FOREIGN KEY (`title_id`) REFERENCES `titles` (`title_id`),
  CONSTRAINT `fk_views_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='reproducciones de títulos';
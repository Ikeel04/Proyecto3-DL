CREATE TABLE `assignments` (
  `assign_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la asignación',
  `emp_id` int NOT NULL COMMENT 'id de empleado',
  `project_id` int NOT NULL COMMENT 'id de proyecto',
  `hours` int NOT NULL COMMENT 'horas dedicadas',
  `role` varchar(20) NOT NULL COMMENT 'rol en el proyecto',
  PRIMARY KEY (`assign_id`),
  KEY `fk_assignments_emp_id` (`emp_id`),
  KEY `fk_assignments_project_id` (`project_id`),
  CONSTRAINT `fk_assignments_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`),
  CONSTRAINT `fk_assignments_project_id` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=261 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='asignación de empleados a proyectos';

CREATE TABLE `departments` (
  `dept_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del departamento',
  `dept_name` varchar(60) NOT NULL COMMENT 'nombre del departamento',
  `location` varchar(40) NOT NULL COMMENT 'ciudad de la sede',
  PRIMARY KEY (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='departamentos de la empresa';

CREATE TABLE `employees` (
  `emp_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del empleado',
  `full_name` varchar(80) NOT NULL COMMENT 'nombre completo',
  `dept_id` int NOT NULL COMMENT 'id de departamento',
  `hire_date` date NOT NULL COMMENT 'fecha de contratación',
  `salary` decimal(10,2) NOT NULL COMMENT 'salario mensual en quetzales',
  `job_level` varchar(20) NOT NULL COMMENT 'nivel del puesto',
  `manager_id` int DEFAULT NULL COMMENT 'emp_id del jefe directo, NULL si no tiene',
  PRIMARY KEY (`emp_id`),
  KEY `fk_employees_dept_id` (`dept_id`),
  CONSTRAINT `fk_employees_dept_id` FOREIGN KEY (`dept_id`) REFERENCES `departments` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='empleados';

CREATE TABLE `leave_requests` (
  `leave_id` int NOT NULL AUTO_INCREMENT COMMENT 'id de la solicitud',
  `emp_id` int NOT NULL COMMENT 'id de empleado',
  `leave_type` varchar(20) NOT NULL COMMENT 'tipo de permiso',
  `days` int NOT NULL COMMENT 'días solicitados',
  `request_date` date NOT NULL COMMENT 'fecha de solicitud',
  PRIMARY KEY (`leave_id`),
  KEY `fk_leave_requests_emp_id` (`emp_id`),
  CONSTRAINT `fk_leave_requests_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `employees` (`emp_id`)
) ENGINE=InnoDB AUTO_INCREMENT=181 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='solicitudes de vacaciones o permisos';

CREATE TABLE `projects` (
  `project_id` int NOT NULL AUTO_INCREMENT COMMENT 'id del proyecto',
  `project_name` varchar(80) NOT NULL COMMENT 'nombre del proyecto',
  `dept_id` int NOT NULL COMMENT 'id de departamento responsable',
  `budget` decimal(12,2) NOT NULL COMMENT 'presupuesto en quetzales',
  `start_date` date NOT NULL COMMENT 'fecha de inicio',
  PRIMARY KEY (`project_id`),
  KEY `fk_projects_dept_id` (`dept_id`),
  CONSTRAINT `fk_projects_dept_id` FOREIGN KEY (`dept_id`) REFERENCES `departments` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='proyectos internos';
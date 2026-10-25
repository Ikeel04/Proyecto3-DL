"""
Especificación de los esquemas propios del proyecto.

Cada esquema es un dict con tablas; cada columna es una tupla:
    (nombre, tipo_sql, generador, rol, etiqueta, comentario)

- generador: cómo se llenan los datos (ver construir_esquemas.py)
- rol: pk, fk, name, cat, num, date, bool, other  -> lo usan las plantillas de preguntas
- etiqueta: cómo se nombra la columna en español dentro de las preguntas (con artículo)
- comentario: lo que va en COMMENT de MySQL (None = usar la etiqueta sin artículo)

Los 12 esquemas de TRAIN y los 2 de VAL no comparten dominio ni nombres de tabla.
Algunos esquemas usan nombres en inglés o abreviados a propósito, porque la
evaluación oculta puede traer cualquiera de esos estilos.
"""

NOMBRES = ["Ana", "Luis", "María", "José", "Carlos", "Lucía", "Pedro", "Sofía", "Jorge", "Valeria",
           "Diego", "Camila", "Andrés", "Daniela", "Fernando", "Gabriela", "Ricardo", "Paola", "Mario",
           "Andrea", "Javier", "Isabel", "Pablo", "Mónica", "Héctor", "Karla", "Raúl", "Elena", "Óscar",
           "Natalia", "Sergio", "Rosa", "Hugo", "Lorena", "Iván", "Beatriz", "Rodrigo", "Silvia"]
APELLIDOS = ["López", "García", "Pérez", "Morales", "Hernández", "Castillo", "Ramírez", "Méndez",
             "Juárez", "Cruz", "Gómez", "Díaz", "Reyes", "Orellana", "Barrios", "Estrada", "Monzón",
             "Ordóñez", "Aguilar", "Sandoval", "Cabrera", "Recinos", "Pineda", "Velásquez", "Ruiz"]
CIUDADES = ["Guatemala", "Mixco", "Quetzaltenango", "Antigua Guatemala", "Escuintla", "Cobán",
            "Huehuetenango", "Chimaltenango", "Zacapa", "Puerto Barrios", "Retalhuleu", "Flores"]

D = "date:2023-01-01:2025-12-31"
DT = "datetime:2023-01-01:2025-12-31"

TRAIN = []
VAL = []

# ---------------------------------------------------------------- 1 tienda_online (es)
TRAIN.append({"db": "tienda_online", "tablas": [
    {"name": "categorias", "comment": "categorías de productos", "n": 8,
     "sing": "la categoría", "plur": "las categorías", "cols": [
        ("id_categoria", "INT", "pk", "pk", "el id de la categoría", None),
        ("nombre", "VARCHAR(60)", "lista:Electrónica|Hogar|Deportes|Juguetes|Libros|Ropa|Belleza|Mascotas", "name", "el nombre de la categoría", None),
        ("descripcion", "VARCHAR(200)", "text:Productos de la línea", "other", "la descripción", None)]},
    {"name": "clientes", "comment": "clientes registrados en la tienda", "n": 80,
     "sing": "el cliente", "plur": "los clientes", "cols": [
        ("id_cliente", "INT", "pk", "pk", "el id del cliente", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del cliente", None),
        ("ciudad", "VARCHAR(40)", "cat:" + "|".join(CIUDADES[:8]), "cat", "la ciudad", "ciudad de residencia"),
        ("fecha_registro", "DATE", D, "date", "la fecha de registro", None),
        ("es_vip", "TINYINT(1)", "bool", "bool", "si es VIP", "1 si el cliente es VIP")]},
    {"name": "productos", "comment": "catálogo de productos", "n": 60,
     "sing": "el producto", "plur": "los productos", "cols": [
        ("id_producto", "INT", "pk", "pk", "el id del producto", None),
        ("nombre", "VARCHAR(80)", "combo:Audífonos|Lámpara|Balón|Muñeca|Novela|Camisa|Crema|Collar|Teclado|Silla|Raqueta|Rompecabezas;Pro|Clásico|Deluxe|Mini|Plus|Eco|Max", "name", "el nombre del producto", None),
        ("id_categoria", "INT", "fk:categorias", "fk", "la categoría", None),
        ("precio", "DECIMAL(10,2)", "dec:15:2500", "num", "el precio", "precio unitario en quetzales"),
        ("existencias", "INT", "int:0:300", "num", "las existencias", "unidades en bodega")]},
    {"name": "pedidos", "comment": "pedidos hechos por los clientes", "n": 300,
     "sing": "el pedido", "plur": "los pedidos", "cols": [
        ("id_pedido", "INT", "pk", "pk", "el id del pedido", None),
        ("id_cliente", "INT", "fk:clientes", "fk", "el cliente", None),
        ("fecha_pedido", "DATE", D, "date", "la fecha del pedido", None),
        ("estado", "VARCHAR(20)", "cat:entregado|enviado|pendiente|cancelado", "cat", "el estado", "estado del pedido"),
        ("total", "DECIMAL(10,2)", "dec:50:6000", "num", "el total", "monto total del pedido en quetzales")]},
    {"name": "detalle_pedido", "comment": "líneas de cada pedido", "n": 700,
     "sing": "la línea de pedido", "plur": "las líneas de pedido", "cols": [
        ("id_detalle", "INT", "pk", "pk", "el id de la línea", None),
        ("id_pedido", "INT", "fk:pedidos", "fk", "el pedido", None),
        ("id_producto", "INT", "fk:productos", "fk", "el producto", None),
        ("cantidad", "INT", "int:1:8", "num", "la cantidad", "unidades compradas"),
        ("precio_unitario", "DECIMAL(10,2)", "dec:15:2500", "num", "el precio unitario", None)]},
    {"name": "pagos", "comment": "pagos registrados para los pedidos", "n": 260,
     "sing": "el pago", "plur": "los pagos", "cols": [
        ("id_pago", "INT", "pk", "pk", "el id del pago", None),
        ("id_pedido", "INT", "fk:pedidos", "fk", "el pedido", None),
        ("metodo", "VARCHAR(20)", "cat:tarjeta|efectivo|transferencia", "cat", "el método de pago", None),
        ("monto", "DECIMAL(10,2)", "dec:50:6000", "num", "el monto pagado", None),
        ("fecha_pago", "DATE", D, "date", "la fecha del pago", None)]},
]})

# ---------------------------------------------------------------- 2 universidad (es)
TRAIN.append({"db": "universidad", "tablas": [
    {"name": "facultades", "comment": "facultades de la universidad", "n": 5,
     "sing": "la facultad", "plur": "las facultades", "cols": [
        ("id_facultad", "INT", "pk", "pk", "el id de la facultad", None),
        ("nombre", "VARCHAR(80)", "lista:Ingeniería|Ciencias Sociales|Educación|Ciencias y Humanidades|Administración", "name", "el nombre de la facultad", None),
        ("edificio", "VARCHAR(10)", "lista:A|B|C|D|E", "cat", "el edificio", None)]},
    {"name": "carreras", "comment": "carreras que ofrece cada facultad", "n": 14,
     "sing": "la carrera", "plur": "las carreras", "cols": [
        ("id_carrera", "INT", "pk", "pk", "el id de la carrera", None),
        ("nombre", "VARCHAR(80)", "lista:Computación|Mecatrónica|Civil|Industrial|Psicología|Antropología|Pedagogía|Profesorado de Matemática|Biología|Química|Letras|Administración de Empresas|Mercadeo|Finanzas", "name", "el nombre de la carrera", None),
        ("id_facultad", "INT", "fk:facultades", "fk", "la facultad", None),
        ("duracion_anios", "INT", "int:4:6", "num", "la duración en años", None)]},
    {"name": "estudiantes", "comment": "estudiantes inscritos", "n": 150,
     "sing": "el estudiante", "plur": "los estudiantes", "cols": [
        ("carne", "INT", "pk", "pk", "el carné", "número de carné"),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del estudiante", None),
        ("id_carrera", "INT", "fk:carreras", "fk", "la carrera", None),
        ("anio_ingreso", "INT", "int:2019:2025", "other", "el año de ingreso", None),
        ("promedio", "DECIMAL(5,2)", "dec:55:98", "num", "el promedio", "promedio acumulado sobre 100"),
        ("becado", "TINYINT(1)", "bool", "bool", "si está becado", "1 si tiene beca")]},
    {"name": "profesores", "comment": "catedráticos", "n": 30,
     "sing": "el profesor", "plur": "los profesores", "cols": [
        ("id_profesor", "INT", "pk", "pk", "el id del profesor", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del profesor", None),
        ("id_facultad", "INT", "fk:facultades", "fk", "la facultad", None),
        ("grado", "VARCHAR(20)", "cat:Licenciatura|Maestría|Doctorado", "cat", "el grado académico", None),
        ("fecha_contratacion", "DATE", "date:2010-01-01:2024-12-31", "date", "la fecha de contratación", None)]},
    {"name": "cursos", "comment": "cursos impartidos", "n": 40,
     "sing": "el curso", "plur": "los cursos", "cols": [
        ("id_curso", "INT", "pk", "pk", "el id del curso", None),
        ("nombre", "VARCHAR(80)", "combo:Cálculo|Física|Programación|Estadística|Redes|Ética|Contabilidad|Química|Historia|Didáctica;I|II|III|Avanzado", "name", "el nombre del curso", None),
        ("creditos", "INT", "int:2:5", "num", "los créditos", None),
        ("id_profesor", "INT", "fk:profesores", "fk", "el profesor", None)]},
    {"name": "inscripciones", "comment": "asignación de estudiantes a cursos", "n": 600,
     "sing": "la inscripción", "plur": "las inscripciones", "cols": [
        ("id_inscripcion", "INT", "pk", "pk", "el id de la inscripción", None),
        ("carne", "INT", "fk:estudiantes", "fk", "el estudiante", None),
        ("id_curso", "INT", "fk:cursos", "fk", "el curso", None),
        ("semestre", "VARCHAR(10)", "cat:2024-1|2024-2|2025-1|2025-2", "cat", "el semestre", None),
        ("nota", "DECIMAL(5,2)", "?dec:30:100", "num", "la nota final", "nota final, NULL si no ha terminado")]},
]})

# ---------------------------------------------------------------- 3 hr_company (en)
TRAIN.append({"db": "hr_company", "tablas": [
    {"name": "departments", "comment": "departamentos de la empresa", "n": 7,
     "sing": "el departamento", "plur": "los departamentos", "cols": [
        ("dept_id", "INT", "pk", "pk", "el id del departamento", None),
        ("dept_name", "VARCHAR(60)", "lista:Ventas|Finanzas|Tecnología|Recursos Humanos|Operaciones|Legal|Marketing", "name", "el nombre del departamento", "nombre del departamento"),
        ("location", "VARCHAR(40)", "cat:Guatemala|Mixco|Quetzaltenango", "cat", "la sede", "ciudad de la sede")]},
    {"name": "employees", "comment": "empleados", "n": 120,
     "sing": "el empleado", "plur": "los empleados", "cols": [
        ("emp_id", "INT", "pk", "pk", "el id del empleado", None),
        ("full_name", "VARCHAR(80)", "persona", "name", "el nombre del empleado", "nombre completo"),
        ("dept_id", "INT", "fk:departments", "fk", "el departamento", None),
        ("hire_date", "DATE", "date:2015-01-01:2025-06-30", "date", "la fecha de contratación", "fecha de contratación"),
        ("salary", "DECIMAL(10,2)", "dec:4000:30000", "num", "el salario", "salario mensual en quetzales"),
        ("job_level", "VARCHAR(20)", "cat:junior|semi-senior|senior|manager", "cat", "el nivel del puesto", "nivel del puesto"),
        ("manager_id", "INT", "?int:1:15", "other", "el jefe", "emp_id del jefe directo, NULL si no tiene")]},
    {"name": "projects", "comment": "proyectos internos", "n": 25,
     "sing": "el proyecto", "plur": "los proyectos", "cols": [
        ("project_id", "INT", "pk", "pk", "el id del proyecto", None),
        ("project_name", "VARCHAR(80)", "combo:Migración|Portal|Auditoría|Campaña|Automatización|Rediseño;Clientes|Nómina|Inventario|Web|Móvil", "name", "el nombre del proyecto", "nombre del proyecto"),
        ("dept_id", "INT", "fk:departments", "fk", "el departamento responsable", None),
        ("budget", "DECIMAL(12,2)", "dec:20000:900000", "num", "el presupuesto", "presupuesto en quetzales"),
        ("start_date", "DATE", "date:2022-01-01:2025-06-30", "date", "la fecha de inicio", None)]},
    {"name": "assignments", "comment": "asignación de empleados a proyectos", "n": 260,
     "sing": "la asignación", "plur": "las asignaciones", "cols": [
        ("assign_id", "INT", "pk", "pk", "el id de la asignación", None),
        ("emp_id", "INT", "fk:employees", "fk", "el empleado", None),
        ("project_id", "INT", "fk:projects", "fk", "el proyecto", None),
        ("hours", "INT", "int:10:400", "num", "las horas trabajadas", "horas dedicadas"),
        ("role", "VARCHAR(20)", "cat:developer|analyst|tester|lead", "cat", "el rol", "rol en el proyecto")]},
    {"name": "leave_requests", "comment": "solicitudes de vacaciones o permisos", "n": 180,
     "sing": "la solicitud de permiso", "plur": "las solicitudes de permiso", "cols": [
        ("leave_id", "INT", "pk", "pk", "el id de la solicitud", None),
        ("emp_id", "INT", "fk:employees", "fk", "el empleado", None),
        ("leave_type", "VARCHAR(20)", "cat:vacaciones|enfermedad|personal", "cat", "el tipo de permiso", "tipo de permiso"),
        ("days", "INT", "int:1:15", "num", "los días", "días solicitados"),
        ("request_date", "DATE", D, "date", "la fecha de solicitud", None)]},
]})

# ---------------------------------------------------------------- 4 aerolinea (es)
TRAIN.append({"db": "aerolinea", "tablas": [
    {"name": "aeropuertos", "comment": "aeropuertos", "n": 10,
     "sing": "el aeropuerto", "plur": "los aeropuertos", "cols": [
        ("codigo_iata", "CHAR(3)", "lista:GUA|FRS|SAL|MEX|MIA|PTY|SJO|BOG|LAX|MAD", "pk_text", "el código IATA", None),
        ("nombre", "VARCHAR(80)", "lista:La Aurora|Mundo Maya|Monseñor Romero|Benito Juárez|Miami International|Tocumen|Juan Santamaría|El Dorado|Los Angeles International|Barajas", "name", "el nombre del aeropuerto", None),
        ("pais", "VARCHAR(40)", "lista:Guatemala|Guatemala|El Salvador|México|Estados Unidos|Panamá|Costa Rica|Colombia|Estados Unidos|España", "cat", "el país", None)]},
    {"name": "aviones", "comment": "flota de aviones", "n": 15,
     "sing": "el avión", "plur": "los aviones", "cols": [
        ("id_avion", "INT", "pk", "pk", "el id del avión", None),
        ("matricula", "VARCHAR(10)", "text:TG-A", "name", "la matrícula", None),
        ("modelo", "VARCHAR(30)", "cat:A320|A321|B737|E190", "cat", "el modelo", None),
        ("capacidad", "INT", "int:100:220", "num", "la capacidad", "número de asientos")]},
    {"name": "vuelos", "comment": "vuelos programados", "n": 250,
     "sing": "el vuelo", "plur": "los vuelos", "cols": [
        ("id_vuelo", "INT", "pk", "pk", "el id del vuelo", None),
        ("origen", "CHAR(3)", "fk:aeropuertos", "fk", "el aeropuerto de origen", "código IATA de origen"),
        ("destino", "CHAR(3)", "fk:aeropuertos", "fk", "el aeropuerto de destino", "código IATA de destino"),
        ("id_avion", "INT", "fk:aviones", "fk", "el avión", None),
        ("fecha_salida", "DATETIME", DT, "date", "la fecha de salida", None),
        ("duracion_min", "INT", "int:45:720", "num", "la duración en minutos", None),
        ("estado", "VARCHAR(15)", "cat:a tiempo|retrasado|cancelado", "cat", "el estado del vuelo", None)]},
    {"name": "pasajeros", "comment": "pasajeros", "n": 200,
     "sing": "el pasajero", "plur": "los pasajeros", "cols": [
        ("id_pasajero", "INT", "pk", "pk", "el id del pasajero", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del pasajero", None),
        ("nacionalidad", "VARCHAR(40)", "cat:guatemalteca|salvadoreña|mexicana|estadounidense|española", "cat", "la nacionalidad", None),
        ("millas", "INT", "int:0:90000", "num", "las millas acumuladas", None)]},
    {"name": "reservas", "comment": "reservas de pasajeros en vuelos", "n": 700,
     "sing": "la reserva", "plur": "las reservas", "cols": [
        ("id_reserva", "INT", "pk", "pk", "el id de la reserva", None),
        ("id_vuelo", "INT", "fk:vuelos", "fk", "el vuelo", None),
        ("id_pasajero", "INT", "fk:pasajeros", "fk", "el pasajero", None),
        ("clase", "VARCHAR(15)", "cat:económica|ejecutiva|primera", "cat", "la clase", None),
        ("precio", "DECIMAL(10,2)", "dec:400:9000", "num", "el precio del boleto", "precio en quetzales"),
        ("fecha_reserva", "DATE", D, "date", "la fecha de la reserva", None)]},
]})

# ---------------------------------------------------------------- 5 restaurant_chain (en)
TRAIN.append({"db": "restaurant_chain", "tablas": [
    {"name": "branches", "comment": "sucursales del restaurante", "n": 8,
     "sing": "la sucursal", "plur": "las sucursales", "cols": [
        ("branch_id", "INT", "pk", "pk", "el id de la sucursal", None),
        ("branch_name", "VARCHAR(60)", "lista:Zona 10|Zona 1|Cayalá|Miraflores|Antigua|Xela Centro|Escuintla|Peri Roosevelt", "name", "el nombre de la sucursal", "nombre de la sucursal"),
        ("city", "VARCHAR(40)", "lista:Guatemala|Guatemala|Guatemala|Guatemala|Antigua Guatemala|Quetzaltenango|Escuintla|Mixco", "cat", "la ciudad", "ciudad"),
        ("opened_on", "DATE", "date:2012-01-01:2023-12-31", "date", "la fecha de apertura", "fecha de apertura")]},
    {"name": "dishes", "comment": "platillos del menú", "n": 35,
     "sing": "el platillo", "plur": "los platillos", "cols": [
        ("dish_id", "INT", "pk", "pk", "el id del platillo", None),
        ("dish_name", "VARCHAR(80)", "combo:Pepián|Hilachas|Tacos|Hamburguesa|Ensalada|Pasta|Pizza|Churrasco|Sopa|Pollo;de la casa|especial|clásico|picante|vegetariano", "name", "el nombre del platillo", "nombre del platillo"),
        ("category", "VARCHAR(20)", "cat:entrada|plato fuerte|postre|bebida", "cat", "la categoría", "categoría del menú"),
        ("price", "DECIMAL(8,2)", "dec:15:180", "num", "el precio", "precio en quetzales"),
        ("is_vegan", "TINYINT(1)", "bool", "bool", "si es vegano", "1 si es vegano")]},
    {"name": "waiters", "comment": "meseros", "n": 30,
     "sing": "el mesero", "plur": "los meseros", "cols": [
        ("waiter_id", "INT", "pk", "pk", "el id del mesero", None),
        ("waiter_name", "VARCHAR(80)", "persona", "name", "el nombre del mesero", "nombre del mesero"),
        ("branch_id", "INT", "fk:branches", "fk", "la sucursal", None),
        ("shift", "VARCHAR(10)", "cat:mañana|tarde|noche", "cat", "el turno", "turno de trabajo")]},
    {"name": "orders", "comment": "órdenes (cuentas) atendidas", "n": 400,
     "sing": "la orden", "plur": "las órdenes", "cols": [
        ("order_id", "INT", "pk", "pk", "el id de la orden", None),
        ("waiter_id", "INT", "fk:waiters", "fk", "el mesero", None),
        ("order_time", "DATETIME", DT, "date", "la fecha de la orden", "fecha y hora"),
        ("tip", "DECIMAL(8,2)", "dec:0:150", "num", "la propina", "propina en quetzales"),
        ("payment_type", "VARCHAR(15)", "cat:card|cash", "cat", "el tipo de pago", "card = tarjeta, cash = efectivo")]},
    {"name": "order_items", "comment": "platillos incluidos en cada orden", "n": 1000,
     "sing": "el ítem de orden", "plur": "los ítems de orden", "cols": [
        ("item_id", "INT", "pk", "pk", "el id del ítem", None),
        ("order_id", "INT", "fk:orders", "fk", "la orden", None),
        ("dish_id", "INT", "fk:dishes", "fk", "el platillo", None),
        ("qty", "INT", "int:1:5", "num", "la cantidad", "cantidad pedida")]},
]})

# ---------------------------------------------------------------- 6 inv_almacen (abreviado es)
TRAIN.append({"db": "inv_almacen", "tablas": [
    {"name": "prov", "comment": "proveedores", "n": 15,
     "sing": "el proveedor", "plur": "los proveedores", "cols": [
        ("prov_id", "INT", "pk", "pk", "el id del proveedor", None),
        ("nom_prov", "VARCHAR(80)", "combo:Distribuidora|Comercial|Importadora|Grupo|Industrias;del Valle|Maya|Central|Pacífico|Norte|Quetzal", "name", "el nombre del proveedor", "nombre del proveedor"),
        ("pais", "VARCHAR(30)", "cat:Guatemala|México|El Salvador|China", "cat", "el país", "país del proveedor")]},
    {"name": "alm", "comment": "almacenes / bodegas", "n": 6,
     "sing": "el almacén", "plur": "los almacenes", "cols": [
        ("alm_id", "INT", "pk", "pk", "el id del almacén", None),
        ("nom_alm", "VARCHAR(60)", "lista:Bodega Central|Bodega Norte|Bodega Sur|Bodega Occidente|Bodega Oriente|Bodega Puerto", "name", "el nombre del almacén", "nombre del almacén"),
        ("cap_m3", "INT", "int:500:5000", "num", "la capacidad en metros cúbicos", "capacidad en m3")]},
    {"name": "prod", "comment": "productos de inventario", "n": 70,
     "sing": "el producto", "plur": "los productos", "cols": [
        ("prod_id", "INT", "pk", "pk", "el id del producto", None),
        ("desc_prod", "VARCHAR(80)", "combo:Tornillo|Tuerca|Cable|Tubo|Pintura|Cemento|Varilla|Lámina|Foco|Brocha;1/2|3/4|galvanizado|PVC|blanco|20kg|LED|reforzado", "name", "la descripción del producto", "descripción del producto"),
        ("prov_id", "INT", "fk:prov", "fk", "el proveedor", None),
        ("cat_prod", "VARCHAR(20)", "cat:ferretería|construcción|electricidad|pintura", "cat", "la categoría", "categoría del producto"),
        ("costo_u", "DECIMAL(10,2)", "dec:1:450", "num", "el costo unitario", "costo unitario en quetzales"),
        ("stk_min", "INT", "int:5:100", "num", "el stock mínimo", "stock mínimo permitido")]},
    {"name": "mov_inv", "comment": "movimientos de inventario (entradas y salidas)", "n": 900,
     "sing": "el movimiento", "plur": "los movimientos de inventario", "cols": [
        ("mov_id", "INT", "pk", "pk", "el id del movimiento", None),
        ("prod_id", "INT", "fk:prod", "fk", "el producto", None),
        ("alm_id", "INT", "fk:alm", "fk", "el almacén", None),
        ("tipo_mov", "CHAR(1)", "cat:E|S", "cat", "el tipo de movimiento", "E = entrada, S = salida"),
        ("cant", "INT", "int:1:200", "num", "la cantidad", "cantidad de unidades"),
        ("fec_mov", "DATE", D, "date", "la fecha del movimiento", "fecha del movimiento")]},
    {"name": "emp_alm", "comment": "empleados de bodega", "n": 25,
     "sing": "el empleado de bodega", "plur": "los empleados de bodega", "cols": [
        ("emp_id", "INT", "pk", "pk", "el id del empleado", None),
        ("nom_emp", "VARCHAR(80)", "persona", "name", "el nombre del empleado", "nombre del empleado"),
        ("alm_id", "INT", "fk:alm", "fk", "el almacén", None),
        ("sal_mens", "DECIMAL(10,2)", "dec:3500:9000", "num", "el salario mensual", "salario mensual"),
        ("f_ingreso", "DATE", "date:2016-01-01:2025-06-30", "date", "la fecha de ingreso", "fecha de ingreso")]},
]})

# ---------------------------------------------------------------- 7 banco (es)
TRAIN.append({"db": "banco", "tablas": [
    {"name": "sucursales", "comment": "agencias bancarias", "n": 10,
     "sing": "la sucursal", "plur": "las sucursales", "cols": [
        ("id_sucursal", "INT", "pk", "pk", "el id de la sucursal", None),
        ("nombre", "VARCHAR(60)", "combo:Agencia;Centro|Oakland|Miraflores|Majadas|Xela|Antigua|Cobán|Petén|Zacapa|Escuintla", "name", "el nombre de la sucursal", None),
        ("departamento", "VARCHAR(40)", "cat:Guatemala|Quetzaltenango|Sacatepéquez|Alta Verapaz|Petén", "cat", "el departamento", "departamento del país")]},
    {"name": "clientes", "comment": "clientes del banco", "n": 140,
     "sing": "el cliente", "plur": "los clientes", "cols": [
        ("id_cliente", "INT", "pk", "pk", "el id del cliente", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del cliente", None),
        ("fecha_nacimiento", "DATE", "date:1960-01-01:2005-12-31", "date", "la fecha de nacimiento", None),
        ("segmento", "VARCHAR(20)", "cat:personal|pyme|premium", "cat", "el segmento", "segmento comercial"),
        ("id_sucursal", "INT", "fk:sucursales", "fk", "la sucursal", "sucursal donde abrió su relación")]},
    {"name": "cuentas", "comment": "cuentas bancarias", "n": 220,
     "sing": "la cuenta", "plur": "las cuentas", "cols": [
        ("id_cuenta", "INT", "pk", "pk", "el id de la cuenta", None),
        ("id_cliente", "INT", "fk:clientes", "fk", "el cliente", None),
        ("tipo", "VARCHAR(20)", "cat:monetaria|ahorro|plazo fijo", "cat", "el tipo de cuenta", None),
        ("saldo", "DECIMAL(12,2)", "dec:0:250000", "num", "el saldo", "saldo actual en quetzales"),
        ("fecha_apertura", "DATE", "date:2015-01-01:2025-06-30", "date", "la fecha de apertura", None)]},
    {"name": "transacciones", "comment": "movimientos de las cuentas", "n": 1100,
     "sing": "la transacción", "plur": "las transacciones", "cols": [
        ("id_transaccion", "INT", "pk", "pk", "el id de la transacción", None),
        ("id_cuenta", "INT", "fk:cuentas", "fk", "la cuenta", None),
        ("tipo", "VARCHAR(20)", "cat:depósito|retiro|transferencia|pago", "cat", "el tipo de transacción", None),
        ("monto", "DECIMAL(12,2)", "dec:10:40000", "num", "el monto", "monto en quetzales"),
        ("fecha", "DATETIME", DT, "date", "la fecha de la transacción", None)]},
    {"name": "creditos", "comment": "créditos (préstamos bancarios) otorgados", "n": 90,
     "sing": "el crédito", "plur": "los créditos", "cols": [
        ("id_credito", "INT", "pk", "pk", "el id del crédito", None),
        ("id_cliente", "INT", "fk:clientes", "fk", "el cliente", None),
        ("monto", "DECIMAL(12,2)", "dec:5000:800000", "num", "el monto del crédito", None),
        ("tasa", "DECIMAL(5,2)", "dec:6:24", "num", "la tasa de interés", "tasa anual en porcentaje"),
        ("plazo_meses", "INT", "int:12:240", "num", "el plazo en meses", None),
        ("estado", "VARCHAR(15)", "cat:vigente|pagado|en mora", "cat", "el estado del crédito", None),
        ("fecha_desembolso", "DATE", "date:2018-01-01:2025-06-30", "date", "la fecha de desembolso", None)]},
]})

# ---------------------------------------------------------------- 8 streaming (en)
TRAIN.append({"db": "streaming", "tablas": [
    {"name": "genres", "comment": "géneros", "n": 8,
     "sing": "el género", "plur": "los géneros", "cols": [
        ("genre_id", "INT", "pk", "pk", "el id del género", None),
        ("genre_name", "VARCHAR(40)", "lista:Acción|Comedia|Drama|Terror|Documental|Animación|Romance|Ciencia ficción", "name", "el nombre del género", "nombre del género")]},
    {"name": "titles", "comment": "películas y series del catálogo", "n": 90,
     "sing": "el título", "plur": "los títulos", "cols": [
        ("title_id", "INT", "pk", "pk", "el id del título", None),
        ("title", "VARCHAR(100)", "combo:El regreso|La noche|Sombras|Viaje|El último|Ecos|Más allá|La ciudad|Código|Huellas;del volcán|perdida|de cristal|infinito|del lago|eterno|de fuego|sin nombre", "name", "el nombre del título", "nombre de la película o serie"),
        ("genre_id", "INT", "fk:genres", "fk", "el género", None),
        ("kind", "VARCHAR(10)", "cat:movie|series", "cat", "el tipo", "movie = película, series = serie"),
        ("release_year", "INT", "int:1995:2025", "other", "el año de estreno", "año de estreno"),
        ("duration_min", "INT", "int:20:180", "num", "la duración en minutos", "duración en minutos")]},
    {"name": "users", "comment": "usuarios de la plataforma", "n": 160,
     "sing": "el usuario", "plur": "los usuarios", "cols": [
        ("user_id", "INT", "pk", "pk", "el id del usuario", None),
        ("username", "VARCHAR(60)", "persona", "name", "el nombre del usuario", "nombre del usuario"),
        ("country", "VARCHAR(40)", "cat:Guatemala|México|Colombia|Perú|Chile", "cat", "el país", "país"),
        ("signup_date", "DATE", D, "date", "la fecha de registro", "fecha de registro"),
        ("plan", "VARCHAR(15)", "cat:basic|standard|premium", "cat", "el plan", "plan de suscripción")]},
    {"name": "views", "comment": "reproducciones de títulos", "n": 1200,
     "sing": "la reproducción", "plur": "las reproducciones", "cols": [
        ("view_id", "INT", "pk", "pk", "el id de la reproducción", None),
        ("user_id", "INT", "fk:users", "fk", "el usuario", None),
        ("title_id", "INT", "fk:titles", "fk", "el título", None),
        ("watched_at", "DATETIME", DT, "date", "la fecha de reproducción", "fecha y hora"),
        ("minutes", "INT", "int:1:180", "num", "los minutos vistos", "minutos vistos")]},
    {"name": "ratings", "comment": "calificaciones de usuarios", "n": 500,
     "sing": "la calificación", "plur": "las calificaciones", "cols": [
        ("rating_id", "INT", "pk", "pk", "el id de la calificación", None),
        ("user_id", "INT", "fk:users", "fk", "el usuario", None),
        ("title_id", "INT", "fk:titles", "fk", "el título", None),
        ("stars", "INT", "int:1:5", "num", "las estrellas", "calificación de 1 a 5"),
        ("rated_on", "DATE", D, "date", "la fecha de calificación", None)]},
]})

# ---------------------------------------------------------------- 9 liga_futbol (es)
TRAIN.append({"db": "liga_futbol", "tablas": [
    {"name": "estadios", "comment": "estadios", "n": 8,
     "sing": "el estadio", "plur": "los estadios", "cols": [
        ("id_estadio", "INT", "pk", "pk", "el id del estadio", None),
        ("nombre", "VARCHAR(60)", "lista:Doroteo Guamuch|Cementos Progreso|El Trébol|Mario Camposeco|Pensativo|Las Flores|David Cordón|Carlos Salazar", "name", "el nombre del estadio", None),
        ("ciudad", "VARCHAR(40)", "lista:Guatemala|Guatemala|Mixco|Quetzaltenango|Antigua Guatemala|Jalapa|Guastatoya|Mazatenango", "cat", "la ciudad", None),
        ("capacidad", "INT", "int:5000:30000", "num", "la capacidad", None)]},
    {"name": "equipos", "comment": "equipos de la liga", "n": 8,
     "sing": "el equipo", "plur": "los equipos", "cols": [
        ("id_equipo", "INT", "pk", "pk", "el id del equipo", None),
        ("nombre", "VARCHAR(60)", "lista:Rojos FC|Cremas|Albos|Chivos|Panzas|Jaguares|Pecho Amarillo|Venados", "name", "el nombre del equipo", None),
        ("id_estadio", "INT", "fk:estadios", "fk", "el estadio", "estadio local"),
        ("anio_fundacion", "INT", "int:1920:2010", "other", "el año de fundación", None)]},
    {"name": "jugadores", "comment": "jugadores", "n": 180,
     "sing": "el jugador", "plur": "los jugadores", "cols": [
        ("id_jugador", "INT", "pk", "pk", "el id del jugador", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del jugador", None),
        ("id_equipo", "INT", "fk:equipos", "fk", "el equipo", None),
        ("posicion", "VARCHAR(20)", "cat:portero|defensa|mediocampista|delantero", "cat", "la posición", None),
        ("fecha_nacimiento", "DATE", "date:1988-01-01:2006-12-31", "date", "la fecha de nacimiento", None),
        ("salario", "DECIMAL(10,2)", "dec:3000:60000", "num", "el salario", "salario mensual en quetzales")]},
    {"name": "partidos", "comment": "partidos jugados", "n": 160,
     "sing": "el partido", "plur": "los partidos", "cols": [
        ("id_partido", "INT", "pk", "pk", "el id del partido", None),
        ("id_local", "INT", "fk:equipos", "fk", "el equipo local", "equipo local"),
        ("id_visitante", "INT", "fk:equipos", "fk", "el equipo visitante", "equipo visitante"),
        ("fecha", "DATE", D, "date", "la fecha del partido", None),
        ("goles_local", "INT", "int:0:5", "num", "los goles del local", None),
        ("goles_visitante", "INT", "int:0:4", "num", "los goles del visitante", None),
        ("asistencia", "INT", "int:800:28000", "num", "la asistencia", "espectadores")]},
    {"name": "goles", "comment": "goles anotados", "n": 380,
     "sing": "el gol", "plur": "los goles", "cols": [
        ("id_gol", "INT", "pk", "pk", "el id del gol", None),
        ("id_partido", "INT", "fk:partidos", "fk", "el partido", None),
        ("id_jugador", "INT", "fk:jugadores", "fk", "el jugador", "jugador que anotó"),
        ("minuto", "INT", "int:1:95", "num", "el minuto", None),
        ("tipo", "VARCHAR(15)", "cat:jugada|penal|cabeza|tiro libre", "cat", "el tipo de gol", None)]},
]})

# ---------------------------------------------------------------- 10 hotel_mgmt (en abreviado)
TRAIN.append({"db": "hotel_mgmt", "tablas": [
    {"name": "htl", "comment": "hoteles de la cadena", "n": 6,
     "sing": "el hotel", "plur": "los hoteles", "cols": [
        ("htl_id", "INT", "pk", "pk", "el id del hotel", None),
        ("htl_nm", "VARCHAR(60)", "lista:Hotel Lago|Hotel Volcán|Hotel Colonial|Hotel Selva|Hotel Playa|Hotel Ciudad", "name", "el nombre del hotel", "nombre del hotel"),
        ("city", "VARCHAR(40)", "lista:Panajachel|Antigua Guatemala|Antigua Guatemala|Flores|Monterrico|Guatemala", "cat", "la ciudad", "ciudad"),
        ("stars", "INT", "int:3:5", "num", "las estrellas", "categoría en estrellas")]},
    {"name": "rm", "comment": "habitaciones", "n": 80,
     "sing": "la habitación", "plur": "las habitaciones", "cols": [
        ("rm_id", "INT", "pk", "pk", "el id de la habitación", None),
        ("htl_id", "INT", "fk:htl", "fk", "el hotel", None),
        ("rm_no", "VARCHAR(10)", "text:Hab", "name", "el número de habitación", "número de habitación"),
        ("rm_type", "VARCHAR(15)", "cat:sencilla|doble|suite", "cat", "el tipo de habitación", "tipo de habitación"),
        ("rate", "DECIMAL(8,2)", "dec:350:2500", "num", "la tarifa por noche", "tarifa por noche en quetzales")]},
    {"name": "gst", "comment": "huéspedes", "n": 200,
     "sing": "el huésped", "plur": "los huéspedes", "cols": [
        ("gst_id", "INT", "pk", "pk", "el id del huésped", None),
        ("gst_nm", "VARCHAR(80)", "persona", "name", "el nombre del huésped", "nombre del huésped"),
        ("ctry", "VARCHAR(40)", "cat:Guatemala|México|Estados Unidos|Alemania|Francia|Canadá", "cat", "el país de origen", "país de origen"),
        ("email", "VARCHAR(80)", "email", "other", "el correo", "correo electrónico")]},
    {"name": "bkg", "comment": "reservaciones", "n": 600,
     "sing": "la reservación", "plur": "las reservaciones", "cols": [
        ("bkg_id", "INT", "pk", "pk", "el id de la reservación", None),
        ("gst_id", "INT", "fk:gst", "fk", "el huésped", None),
        ("rm_id", "INT", "fk:rm", "fk", "la habitación", None),
        ("chk_in", "DATE", D, "date", "la fecha de entrada", "fecha de check-in"),
        ("nights", "INT", "int:1:10", "num", "las noches", "número de noches"),
        ("amt", "DECIMAL(10,2)", "dec:350:25000", "num", "el monto", "monto total cobrado"),
        ("sts", "VARCHAR(12)", "cat:completed|cancelled|no-show", "cat", "el estado", "completed = completada, cancelled = cancelada, no-show = no se presentó")]},
    {"name": "svc_chg", "comment": "cargos por servicios adicionales", "n": 500,
     "sing": "el cargo por servicio", "plur": "los cargos por servicio", "cols": [
        ("chg_id", "INT", "pk", "pk", "el id del cargo", None),
        ("bkg_id", "INT", "fk:bkg", "fk", "la reservación", None),
        ("svc", "VARCHAR(20)", "cat:spa|restaurante|lavandería|tour|minibar", "cat", "el servicio", "servicio consumido"),
        ("chg_amt", "DECIMAL(8,2)", "dec:20:1500", "num", "el monto del cargo", "monto del cargo")]},
]})

# ---------------------------------------------------------------- 11 hospital (es)
TRAIN.append({"db": "hospital", "tablas": [
    {"name": "especialidades", "comment": "especialidades médicas", "n": 8,
     "sing": "la especialidad", "plur": "las especialidades", "cols": [
        ("id_especialidad", "INT", "pk", "pk", "el id de la especialidad", None),
        ("nombre", "VARCHAR(60)", "lista:Pediatría|Cardiología|Dermatología|Traumatología|Ginecología|Neurología|Medicina interna|Oftalmología", "name", "el nombre de la especialidad", None)]},
    {"name": "medicos", "comment": "médicos", "n": 35,
     "sing": "el médico", "plur": "los médicos", "cols": [
        ("id_medico", "INT", "pk", "pk", "el id del médico", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del médico", None),
        ("id_especialidad", "INT", "fk:especialidades", "fk", "la especialidad", None),
        ("colegiado", "INT", "int:1000:20000", "other", "el número de colegiado", None),
        ("tarifa_consulta", "DECIMAL(8,2)", "dec:150:900", "num", "la tarifa de consulta", "tarifa por consulta en quetzales")]},
    {"name": "pacientes", "comment": "pacientes", "n": 220,
     "sing": "el paciente", "plur": "los pacientes", "cols": [
        ("id_paciente", "INT", "pk", "pk", "el id del paciente", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del paciente", None),
        ("sexo", "CHAR(1)", "cat:F|M", "cat", "el sexo", "F o M"),
        ("fecha_nacimiento", "DATE", "date:1945-01-01:2022-12-31", "date", "la fecha de nacimiento", None),
        ("seguro", "VARCHAR(20)", "?cat:IGSS|privado|ninguno", "cat", "el seguro", "tipo de seguro, NULL si no se registró")]},
    {"name": "citas", "comment": "citas médicas", "n": 800,
     "sing": "la cita", "plur": "las citas", "cols": [
        ("id_cita", "INT", "pk", "pk", "el id de la cita", None),
        ("id_paciente", "INT", "fk:pacientes", "fk", "el paciente", None),
        ("id_medico", "INT", "fk:medicos", "fk", "el médico", None),
        ("fecha_hora", "DATETIME", DT, "date", "la fecha de la cita", None),
        ("estado", "VARCHAR(15)", "cat:atendida|cancelada|programada", "cat", "el estado de la cita", None),
        ("costo", "DECIMAL(8,2)", "dec:150:900", "num", "el costo", "costo cobrado")]},
    {"name": "recetas", "comment": "medicamentos recetados en cada cita", "n": 600,
     "sing": "la receta", "plur": "las recetas", "cols": [
        ("id_receta", "INT", "pk", "pk", "el id de la receta", None),
        ("id_cita", "INT", "fk:citas", "fk", "la cita", None),
        ("medicamento", "VARCHAR(60)", "cat:Paracetamol|Ibuprofeno|Amoxicilina|Loratadina|Omeprazol|Metformina|Losartán", "cat", "el medicamento", None),
        ("dosis_mg", "INT", "int:5:1000", "num", "la dosis en mg", None),
        ("dias", "INT", "int:1:30", "num", "los días de tratamiento", None)]},
]})

# ---------------------------------------------------------------- 12 logistics (en)
TRAIN.append({"db": "logistics", "tablas": [
    {"name": "warehouses", "comment": "centros de distribución", "n": 6,
     "sing": "el centro de distribución", "plur": "los centros de distribución", "cols": [
        ("wh_id", "INT", "pk", "pk", "el id del centro", None),
        ("wh_name", "VARCHAR(60)", "lista:CD Norte|CD Sur|CD Occidente|CD Oriente|CD Central|CD Puerto", "name", "el nombre del centro", "nombre del centro de distribución"),
        ("region", "VARCHAR(20)", "lista:norte|sur|occidente|oriente|central|sur", "cat", "la región", "región")]},
    {"name": "drivers", "comment": "pilotos repartidores", "n": 40,
     "sing": "el piloto", "plur": "los pilotos", "cols": [
        ("driver_id", "INT", "pk", "pk", "el id del piloto", None),
        ("driver_name", "VARCHAR(80)", "persona", "name", "el nombre del piloto", "nombre del piloto"),
        ("license_type", "CHAR(1)", "cat:A|B|C", "cat", "el tipo de licencia", "tipo de licencia"),
        ("hired_on", "DATE", "date:2014-01-01:2025-06-30", "date", "la fecha de contratación", "fecha de contratación"),
        ("wh_id", "INT", "fk:warehouses", "fk", "el centro de distribución", "centro asignado")]},
    {"name": "vehicles", "comment": "vehículos de la flota", "n": 30,
     "sing": "el vehículo", "plur": "los vehículos", "cols": [
        ("vehicle_id", "INT", "pk", "pk", "el id del vehículo", None),
        ("plate", "VARCHAR(10)", "text:C-", "name", "la placa", "placa"),
        ("vtype", "VARCHAR(15)", "cat:moto|panel|camión", "cat", "el tipo de vehículo", "tipo de vehículo"),
        ("capacity_kg", "INT", "int:50:12000", "num", "la capacidad en kg", "capacidad de carga en kg")]},
    {"name": "customers", "comment": "clientes que reciben envíos", "n": 120,
     "sing": "el cliente", "plur": "los clientes", "cols": [
        ("cust_id", "INT", "pk", "pk", "el id del cliente", None),
        ("cust_name", "VARCHAR(80)", "persona", "name", "el nombre del cliente", "nombre del cliente"),
        ("city", "VARCHAR(40)", "cat:" + "|".join(CIUDADES), "cat", "la ciudad", "ciudad"),
        ("cust_type", "VARCHAR(15)", "cat:empresa|persona", "cat", "el tipo de cliente", "tipo de cliente")]},
    {"name": "shipments", "comment": "envíos realizados", "n": 900,
     "sing": "el envío", "plur": "los envíos", "cols": [
        ("ship_id", "INT", "pk", "pk", "el id del envío", None),
        ("cust_id", "INT", "fk:customers", "fk", "el cliente", None),
        ("driver_id", "INT", "fk:drivers", "fk", "el piloto", None),
        ("vehicle_id", "INT", "fk:vehicles", "fk", "el vehículo", None),
        ("ship_date", "DATE", D, "date", "la fecha de envío", "fecha de envío"),
        ("weight_kg", "DECIMAL(8,2)", "dec:0.5:2500", "num", "el peso en kg", "peso en kg"),
        ("cost", "DECIMAL(10,2)", "dec:25:4500", "num", "el costo del envío", "costo del envío en quetzales"),
        ("status", "VARCHAR(12)", "cat:delivered|in_transit|returned", "cat", "el estado del envío", "delivered = entregado, in_transit = en tránsito, returned = devuelto")]},
]})

# =============================================================== VALIDACIÓN (no vistos)
# ---------------------------------------------------------------- V1 biblioteca (es)
VAL.append({"db": "biblioteca", "tablas": [
    {"name": "autores", "comment": "autores de los libros", "n": 25,
     "sing": "el autor", "plur": "los autores", "cols": [
        ("id_autor", "INT", "pk", "pk", "el id del autor", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del autor", None),
        ("nacionalidad", "VARCHAR(40)", "cat:guatemalteca|mexicana|colombiana|argentina|española", "cat", "la nacionalidad", None)]},
    {"name": "editoriales", "comment": "editoriales", "n": 6,
     "sing": "la editorial", "plur": "las editoriales", "cols": [
        ("id_editorial", "INT", "pk", "pk", "el id de la editorial", None),
        ("nombre", "VARCHAR(60)", "lista:Piedra Santa|Alfaguara|Planeta|Anagrama|F&G Editores|Norma", "name", "el nombre de la editorial", None),
        ("pais", "VARCHAR(40)", "lista:Guatemala|España|España|España|Guatemala|Colombia", "cat", "el país", None)]},
    {"name": "libros", "comment": "títulos del catálogo", "n": 90,
     "sing": "el libro", "plur": "los libros", "cols": [
        ("id_libro", "INT", "pk", "pk", "el id del libro", None),
        ("titulo", "VARCHAR(120)", "combo:Crónica|Historia|Memorias|El jardín|Cartas|La casa|Leyendas|Poemas|Cuentos|El silencio;del sur|de la montaña|olvidadas|de agua|del maíz|nocturnas|de papel|del puerto", "name", "el título", None),
        ("id_autor", "INT", "fk:autores", "fk", "el autor", None),
        ("id_editorial", "INT", "fk:editoriales", "fk", "la editorial", None),
        ("anio_publicacion", "INT", "int:1960:2025", "num", "el año de publicación", None),
        ("genero", "VARCHAR(20)", "cat:novela|cuento|poesía|ensayo|infantil", "cat", "el género", None),
        ("paginas", "INT", "int:60:800", "num", "el número de páginas", None)]},
    {"name": "ejemplares", "comment": "copias físicas de cada libro", "n": 220,
     "sing": "el ejemplar", "plur": "los ejemplares", "cols": [
        ("id_ejemplar", "INT", "pk", "pk", "el id del ejemplar", None),
        ("id_libro", "INT", "fk:libros", "fk", "el libro", None),
        ("estado", "VARCHAR(15)", "cat:bueno|regular|dañado", "cat", "el estado físico", None),
        ("fecha_adquisicion", "DATE", "date:2015-01-01:2025-06-30", "date", "la fecha de adquisición", None)]},
    {"name": "socios", "comment": "socios de la biblioteca", "n": 120,
     "sing": "el socio", "plur": "los socios", "cols": [
        ("id_socio", "INT", "pk", "pk", "el id del socio", None),
        ("nombre", "VARCHAR(80)", "persona", "name", "el nombre del socio", None),
        ("tipo", "VARCHAR(15)", "cat:estudiante|docente|externo", "cat", "el tipo de socio", None),
        ("fecha_alta", "DATE", "date:2018-01-01:2025-06-30", "date", "la fecha de alta", None)]},
    {"name": "prestamos", "comment": "préstamos de ejemplares a socios", "n": 650,
     "sing": "el préstamo", "plur": "los préstamos", "cols": [
        ("id_prestamo", "INT", "pk", "pk", "el id del préstamo", None),
        ("id_ejemplar", "INT", "fk:ejemplares", "fk", "el ejemplar", None),
        ("id_socio", "INT", "fk:socios", "fk", "el socio", None),
        ("fecha_prestamo", "DATE", D, "date", "la fecha del préstamo", None),
        ("fecha_devolucion", "DATE", "?date:2023-01-05:2026-01-31", "date", "la fecha de devolución", "NULL si no se ha devuelto"),
        ("multa", "DECIMAL(8,2)", "dec:0:60", "num", "la multa", "multa cobrada en quetzales")]},
]})

# ---------------------------------------------------------------- V2 gym_mgmt (en abreviado)
VAL.append({"db": "gym_mgmt", "tablas": [
    {"name": "loc", "comment": "sedes del gimnasio", "n": 5,
     "sing": "la sede", "plur": "las sedes", "cols": [
        ("loc_id", "INT", "pk", "pk", "el id de la sede", None),
        ("loc_nm", "VARCHAR(60)", "lista:Sede Zona 9|Sede Mixco|Sede Xela|Sede Antigua|Sede Carretera", "name", "el nombre de la sede", "nombre de la sede"),
        ("opn_dt", "DATE", "date:2015-01-01:2023-12-31", "date", "la fecha de apertura", "fecha de apertura")]},
    {"name": "plan", "comment": "planes de membresía", "n": 4,
     "sing": "el plan", "plur": "los planes", "cols": [
        ("plan_id", "INT", "pk", "pk", "el id del plan", None),
        ("plan_nm", "VARCHAR(30)", "lista:Básico|Plus|Premium|Estudiante", "name", "el nombre del plan", "nombre del plan"),
        ("mo_fee", "DECIMAL(8,2)", "lista:199.00|299.00|449.00|159.00", "num", "la cuota mensual", "cuota mensual en quetzales")]},
    {"name": "mbr", "comment": "miembros (clientes) del gimnasio", "n": 160,
     "sing": "el miembro", "plur": "los miembros", "cols": [
        ("mbr_id", "INT", "pk", "pk", "el id del miembro", None),
        ("mbr_nm", "VARCHAR(80)", "persona", "name", "el nombre del miembro", "nombre del miembro"),
        ("plan_id", "INT", "fk:plan", "fk", "el plan", None),
        ("loc_id", "INT", "fk:loc", "fk", "la sede", "sede principal"),
        ("jn_dt", "DATE", "date:2021-01-01:2025-06-30", "date", "la fecha de inscripción", "fecha de inscripción"),
        ("gndr", "CHAR(1)", "cat:F|M", "cat", "el género", "F o M")]},
    {"name": "trnr", "comment": "entrenadores", "n": 18,
     "sing": "el entrenador", "plur": "los entrenadores", "cols": [
        ("trnr_id", "INT", "pk", "pk", "el id del entrenador", None),
        ("trnr_nm", "VARCHAR(80)", "persona", "name", "el nombre del entrenador", "nombre del entrenador"),
        ("loc_id", "INT", "fk:loc", "fk", "la sede", None),
        ("spec", "VARCHAR(20)", "cat:pesas|yoga|spinning|crossfit|natación", "cat", "la especialidad", "especialidad")]},
    {"name": "cls", "comment": "clases grupales programadas", "n": 140,
     "sing": "la clase", "plur": "las clases", "cols": [
        ("cls_id", "INT", "pk", "pk", "el id de la clase", None),
        ("trnr_id", "INT", "fk:trnr", "fk", "el entrenador", None),
        ("cls_dt", "DATETIME", DT, "date", "la fecha de la clase", "fecha y hora de la clase"),
        ("cap", "INT", "int:8:30", "num", "el cupo", "cupo máximo")]},
    {"name": "att", "comment": "asistencia de miembros a clases", "n": 900,
     "sing": "la asistencia", "plur": "las asistencias", "cols": [
        ("att_id", "INT", "pk", "pk", "el id de la asistencia", None),
        ("cls_id", "INT", "fk:cls", "fk", "la clase", None),
        ("mbr_id", "INT", "fk:mbr", "fk", "el miembro", None),
        ("rtg", "INT", "?int:1:5", "num", "la calificación", "calificación de 1 a 5 que dio el miembro, NULL si no calificó")]},
    {"name": "pay", "comment": "pagos de membresía", "n": 700,
     "sing": "el pago", "plur": "los pagos", "cols": [
        ("pay_id", "INT", "pk", "pk", "el id del pago", None),
        ("mbr_id", "INT", "fk:mbr", "fk", "el miembro", None),
        ("pay_dt", "DATE", D, "date", "la fecha de pago", "fecha de pago"),
        ("amt", "DECIMAL(8,2)", "dec:150:460", "num", "el monto", "monto pagado"),
        ("mthd", "VARCHAR(10)", "cat:card|cash|transfer", "cat", "el método de pago", "card = tarjeta, cash = efectivo, transfer = transferencia")]},
]})

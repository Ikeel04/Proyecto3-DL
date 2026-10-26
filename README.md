# Proyecto 3 · Text-to-SQL con LoRA

Deep Learning 2026 · Universidad del Valle de Guatemala
Adrián González (23152) · José Ordóñez

Fine-tuning con LoRA de `Qwen/Qwen2.5-Coder-1.5B-Instruct` para que, dado el esquema de una base
MySQL (tal como sale de `SHOW CREATE TABLE`, con `COMMENT`) y una pregunta en español, genere una
consulta `SELECT` o `WITH ... SELECT` correcta para MySQL 8.4.

## Cómo correrlo

### Uso directo (lo que hace el evaluador)

```python
import solucion                     # carga el modelo de config.json (base + adapter/)
sql = solucion.generar_sql(esquema, pregunta)            # sin ejecutar
sql = solucion.generar_sql(esquema, pregunta, ejecutar)  # con ejecutar (máx. 3 llamadas)
```

Con `"usar_adapter": false` en `config.json` se usa el modelo base con el mismo prompt.

### Reproducir todo en Colab (GPU T4)

`notebooks/00_proyecto_completo.ipynb` que ejecuta el flujo completo en una
sola sesión (datos → entrenamiento A y B → evaluación → entregables), con checkpoints de
commit/push para poder reanudar si la sesión se cae:

1. Haz tu commit+push local; en Colab: pestaña **"GitHub"** → abre `notebooks/00_proyecto_completo.ipynb`.
2. En el panel izquierdo, ícono de llave (**Secretos**): crea `GITHUB_TOKEN` con un token
   fine-grained de GitHub (permiso *Contents: Read and write* sobre el repositorio), activado con
   "acceso para notebook".
3. Llena `REPO`, `GIT_USER` y `GIT_EMAIL` en la primera celda, selecciona **T4 GPU**
   (Entorno de ejecución → Cambiar tipo) y ejecuta las celdas de arriba hacia abajo (~3–4 h).

Para clonar el repo privado desde Colab, guardan un token de GitHub en los *Secrets* de Colab con
el nombre `GITHUB_TOKEN` y cambien la variable `REPO` de la primera celda.

### En local (sin Colab)

```bash
pip install -r requirements.txt
docker run -d --name mysql84 -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -p 3306:3306 mysql:8.4.10
python datos/construir_esquemas.py --crear-lector        # host 127.0.0.1, root sin contraseña
python datos/validar_pares.py
python datos/generar_reparaciones.py
python src/entrenar.py --config A
python src/correr_evaluacion.py --nombre final --adapter adapter/ --beams 4 --verbose
```

## Estructura

| Ruta | Qué hay |
|---|---|
| `solucion.py` | contrato `generar_sql`, prompt, compactación del esquema, filtro de seguridad, ejecutar + reparar |
| `config.json` | modelo base, adapter, semilla |
| `adapter/` | adapter LoRA entregado |
| `datos/esquemas_spec.py` | definición de los 14 esquemas propios (12 train, 2 val) || `datos/construir_esquemas.py` | datos sintéticos, carga en MySQL y `SHOW CREATE TABLE` |
| `datos/generar_pares.py` | plantillas de preguntas en español por nivel (58 patrones) |
| `datos/validar_pares.py` | ejecuta cada par en MySQL; escribe `entrenamiento/train.jsonl` y `descartes/` |
| `datos/generar_reparaciones.py` | ejemplos de corrección con errores reales de MySQL |
| `datos/validacion/validacion_propia.json` | 40 preguntas propias sobre 2 esquemas no vistos |
| `datos/validacion/validacion_propia.json` | 40 preguntas propias sobre 2 esquemas no vistos |
| `datos/validacion/verificar_validacion.py` | corre las 40 referencias en MySQL y reporta si todas pasan |
| `src/entrenar.py` | entrenamiento LoRA (configs A y B) |
| `src/datos_chat.py` | convierte los pares al formato de chat (mismo prompt) |
| `src/evaluador.py` | exactitud por ejecución, `ejecutar()` de solo lectura, categorías de error |
| `src/correr_evaluacion.py` | evalúa una variante y guarda CSV/JSON en `resultados/` |
| `src/prediccion.py` | predicción justificada del EX oculto |
| `src/generar_presentacion.py` | arma `presentacion.pdf` con los resultados |
| `notebooks/` | datos, entrenamiento, evaluación |
| `resultados/` | `validacion_propia.csv`, evaluaciones, curvas de loss, predicción |

## Decisiones principales

**Datos.** 12 esquemas propios de 5–6 tablas (tienda, universidad, aerolínea, banco, hospital,
liga de fútbol, etc.), con nombres en español, en inglés y abreviados (`prov`, `mov_inv`, `htl`,
`bkg`) para parecerse a lo que puede traer la evaluación oculta. Cada columna lleva `COMMENT`.
Las preguntas salen de plantillas por nivel con varias redacciones, y cada una dice qué columnas
devolver. Todo par se ejecuta en MySQL y solo se acepta si corre sin error y devuelve filas.

Resultado: **2,840 pares** (fácil 1,054 · media 927 · difícil 859) + 360 de reparación.
Se descartaron 1,560: 1,522 duplicados entre las dos pasadas del generador, 29 con resultado
vacío y 9 por balance entre patrones (detalle en `datos/descartes/`). En la primera versión del
generador hubo 14 consultas con error de MySQL (columnas con el mismo nombre dentro de un CTE);
se corrigió la plantilla y en la versión final no queda ninguna.

**Validación.** 2 esquemas que no están en entrenamiento: `biblioteca` (español) y `gym_mgmt`
(abreviado en inglés), 40 preguntas: 13 fáciles, 14 medias, 13 difíciles. La partición es por
esquema y se verifica que ninguna tabla de validación comparta nombre con las de entrenamiento.

**Prompt.** System con las reglas + `### Esquema` (compactado) + `### Pregunta` + `### SQL`.
La compactación quita índices, motor, charset, `AUTO_INCREMENT` y `NOT NULL`, y conserva tipos,
`COMMENT`, PK y FK (≈40% menos texto).

**Inferencia.** Beam search de 4 sin muestreo (determinista). Si hay `ejecutar`: se corre el mejor
candidato; si falla, el modelo corrige con el mensaje de error; si corre pero sin filas, se prueba el
siguiente candidato. Nunca más de 3 llamadas y con un presupuesto de 24 s por pregunta. Cualquier
consulta que no empiece con `SELECT`/`WITH` o contenga instrucciones de escritura se descarta.

## Licencias

- Modelo base `Qwen/Qwen2.5-Coder-1.5B-Instruct`: Apache 2.0. El adapter se distribuye bajo la misma licencia.
- Datos: esquemas, datos y preguntas generados por nosotros (sintéticos, sin datos personales reales). No usamos Spider ni BIRD.
- MySQL 8.4.10 (GPLv2) solo se usa como motor; no se redistribuye.
- Librerías: PyTorch (BSD), Transformers, PEFT y Accelerate (Apache 2.0), PyMySQL (MIT), sqlglot (MIT).

## Uso de IA

Usamos Claude (Anthropic) como asistente de programación para escribir la primera versión del
código (generador de esquemas y plantillas, evaluador, script de entrenamiento, notebooks) y para
redactar las plantillas de preguntas. Los pares de entrenamiento cuentan como "generados con un
LLM sobre esquemas propios": las plantillas las propuso el LLM y los valores salen de los datos.
Revisamos y corregimos el código, corrimos todo en Colab, y las decisiones de experimentos,
hipótesis e interpretación de resultados son nuestras. Las preguntas de validación las revisamos
y ajustamos una por una. No se usa ninguna API externa al generar las consultas.

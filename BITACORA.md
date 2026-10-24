# Bitácora

Cada entrada la escribe quien hizo el trabajo, el día que lo hizo. Formato: fecha · autor · qué se hizo · resultado o decisión.

---

### 2026-10-23 · Adrián González
Definimos los 14 esquemas propios: 12 para entrenamiento y 2 para validación (biblioteca y gym_mgmt).
Mezclamos nombres en español, inglés y abreviados porque la evaluación oculta puede traer cualquiera.
Al revisar la partición vimos que `prestamos` existía en banco (train) y en biblioteca (val); se
renombró la de banco a `creditos` para que ninguna tabla de validación aparezca en entrenamiento.

### 2026-10-23 · Adrián González
Generador de pares con 58 patrones (fácil, media, difícil) y validación en MySQL 8.4.
Primera corrida: 14 consultas con error 1060 (dos columnas `nombre` dentro de un CTE). Se corrigió
la plantilla poniendo alias. Versión final: 2,840 pares aceptados, 0 errores de MySQL,
1,560 descartes (casi todos duplicados entre las dos semillas del generador).

### 2026-10-23 · Adrián González
Ejemplos de reparación: 360 consultas rotas a propósito (columna, tabla, GROUP BY, sintaxis) con el
error real de MySQL. Servirán para el paso de corrección cuando el evaluador entregue `ejecutar`.
`solucion.py` listo: prompt, compactación del esquema (~40% menos texto) y filtro de seguridad.

### AAAA-MM-DD · José Ordóñez
Revisión y ajuste de las 40 preguntas de validación propia. Se verificó que las 40 consultas de
referencia corren en MySQL y devuelven filas. _(completar: qué preguntas cambiaste y por qué)_

### AAAA-MM-DD · José Ordóñez
Hipótesis escritas antes de entrenar (`resultados/hipotesis.md`). Entrenamiento de la config A en
Colab T4. _(completar: minutos, parámetros entrenables, train/eval loss final, si la curva se ve estable)_

### AAAA-MM-DD · José Ordóñez
Entrenamiento de la config B. _(completar: comparación con A y si se cumplió la hipótesis)_

### AAAA-MM-DD · José Ordóñez
Baseline sin adapter y evaluación de A y B en la validación propia. _(completar: EX de cada una,
cuál se eligió para `adapter/`)_

### AAAA-MM-DD · Adrián González
Experimento de inferencia: greedy vs beam 4 vs beam 4 + ejecutar/reparar, y esquema crudo vs
compactado. _(completar: EX de cada variante y qué tipo de errores se corrigieron)_

### AAAA-MM-DD · José Ordóñez
Análisis de errores por categoría y predicción del EX oculto. _(completar: categoría más común y
predicción con su rango)_

### AAAA-MM-DD · Adrián González
Verificación final del contrato en Colab: carga < 5 min, < 30 s por pregunta, determinismo, versión
con `usar_adapter: false`. Presentación generada. _(completar con los tiempos medidos)_

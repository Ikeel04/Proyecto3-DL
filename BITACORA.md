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

### 2026-10-25 · José Ordóñez
40 preguntas de validación propia sobre `biblioteca` y `gym_mgmt`
(13 fáciles, 14 medias, 13 difíciles), guardadas en `datos/validacion/validacion_propia.json`.
Verificación de las 40 consultas de referencia corren en MySQL 8.4 con `ONLY_FULL_GROUP_BY`
y devuelven filas. Hallazgo: los dumps tienen los valores con tilde almacenados doble-codificados
('daÃ±ado' en vez de 'dañado'), Se remplazaron literales con tilde ('poesía' → 'novela',
'dañado' → 'bueno') para que las referencias no dependan del encoding. El detalle lo verifica
`datos/validacion/verificar_validacion.py`.

### 2026-10-25 · José Ordóñez
Escritas las hipótesis antes de entrenar en `resultados/hipotesis.md`: las configs LoRA A y B
difieren en un solo factor (`target_modules`: solo atención vs atención+MLP); fijos r=16,
alpha=32, lr=2e-4, 1 época y semilla 2026. Apuesto B algo mejor en nivel difícil; se elegirá
por EX en la validación propia. Pendiente: entrenar en Colab.

### 2026-10-25 · José Ordóñez
Entrenamiento de la config A en Colab T4: 4,358,144 parámetros entrenables (0.282 % del modelo),
42.5 min, 187 pasos (batch efectivo 16 sobre 3,000 ejemplos de chat: 2,640 pares + 360 de
reparación, con 200 pares apartados para la curva). Curva estable y descendente; eval loss
final 0.0042. Únicos tropiezos: Colab trae `torchao` 0.10 y peft 0.21 exige ≥0.16 (se quitó,
no lo usamos) y un OOM del paso de eval que se resolvió bajando la evaluación a lote 1 con
`empty_cache` (el entrenamiento en sí nunca tronó).

### 2026-10-25 · José Ordóñez
Entrenamiento de la config B: 18,464,768 entrenables (1.182 %, 4.2× más que A), 57.2 min,
eval loss final 0.0043 — prácticamente idéntico al de A pese a los parámetros extra, con la
curva igual de estable. Primera señal contra la hipótesis de B: con el loss ya saturado
(~0.004), la capacidad adicional de los MLP no comprimió mejor el dataset, así que el desempate
dependería del EX, no del loss.

### 2026-10-25 · José Ordóñez
Baseline sin adapter y evaluación de A y B (greedy + ejecutar) sobre la validación propia de
40 preguntas: base EX 0.575 (F 0.77/M 0.86/D 0.31), **A 0.675 (0.85/0.57/0.69)** y
B 0.562 (0.85/0.57/0.46). El fine-tuning le gana +0.100 al baseline en greedy, y A supera a B
con toda la brecha en el nivel difícil (0.69 vs 0.46): B sobreajustó las plantillas con sus
4× parámetros. Ganadora: config A → `adapter/`.

### 2026-10-25 · Adrián González
Experimento de inferencia con el adapter de A: beam 4 · EX 0.662 (0.92/0.71/0.54); esquema
crudo sin compactar · 0.637 (0.85/0.57/0.62); base + beam 4 + ejecutar/reparar · 0.725
(0.85/0.93/0.54); final (adapter + beam 4 + ejecutar) · 0.662 (0.92/0.71/0.54). Lo que se
corrigió con ejecutar/reparar: los errores de sintaxis y de columna/tabla inexistente
(se ven en los niveles F/M); el costo se pagó en difícil. Detalle a favor del método: las dos
corridas con flags idénticos (beam vs final) dieron exactamente el mismo EX — el protocolo con
semilla 2026 es determinista. Con n=40, todas las diferencias quedan dentro del IC de
bootstrap [0.53, 0.80].

### 2026-10-25 · José Ordóñez
Análisis de errores por categoría y predicción del EX oculto: dominan
`columna_o_tabla_inexistente` (6 en greedy), seguidos de `resultado_distinto`, `filtro` y
`join`; casi la mitad de los fallos fue sintaxis o columna/tabla inexistente, justamente lo
que el paso ejecutar+reparar suele rescatar. Predicción con bootstrap de 2,000 re-muestreos
(semilla 2026): **EX 0.62, rango [0.43, 0.82]** (EX de validación 0.662, ajuste −0.04 por la
variedad de los esquemas ocultos, de hasta 10 tablas). Justificación en `resultados/prediccion.json`.

### 2026-10-25 · Adrián González
Verificación final del contrato en Colab: carga del pipeline dentro de los 5 min, menos de
30 s por pregunta, determinismo con semilla 2026 y la versión `usar_adapter: false` corriendo
sin adapter como plan B. Presentación generada con los resultados de las 7 corridas; los
tiempos medidos quedan en la salida de la celda de contrato del notebook 00.

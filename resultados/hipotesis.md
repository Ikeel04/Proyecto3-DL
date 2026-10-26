# Hipótesis de las configuraciones LoRA

Escritas antes de entrenar (2026-10-25 · José Ordóñez). Las dos configuraciones difieren en
**un solo factor: el rango LoRA (`r`)**. Todo lo demás es idéntico: módulos objetivo
(`q_proj`, `k_proj`, `v_proj`, `o_proj`), `lr = 2e-4`, 2 épocas, batch efectivo 16
(batch 1 × grad-acumulación 16), `max_len = 1024`, `dropout = 0.05` y la misma semilla (2026).
El dataset es el mismo para ambas: 2,840 pares + 360 de reparación.

| Factor | Config A | Config B |
|---|---|---|
| `r` | 8 | 16 |
| `alpha` | 16 | 16 |

## Config A — r = 8

- **Hipótesis:** 8 es el rango típico en text-to-SQL para un modelo de 1.5B; con este dataset
  (plantillas de un taller, no código libre) la capacidad de 8 debería bastar para aprender el
  formato de chat, la compactación del esquema y los patrones de los tres niveles.
- **Esperado:** más params entrenables en B no garantiza mejor EX; A puede igualar a B
  (diferencia < 0.02) y entrenar ~25–30% más rápido. Ideal para T4: memoria y tiempo holgados.

## Config B — r = 16

- **Hipótesis:** duplicar `r` da más capacidad sobre las mismas matrices, útil para las preguntas
  difíciles (ventanas de funciones, encadenamientos de conjuntos, fechas) que nacen del plan
  de predicción de `solucion.py`.
- **Esperado:** mejor EX en nivel difícil (+0.05 sobre A en el subconjunto difícil, es la apuesta),
  con mayor riesgo de sobre-ajuste con solo 2 épocas y más memoria de entrenamiento que A.

## Cómo se decide

Se evalúan las dos en la validación propia (40 preguntas sobre 2 esquemas no vistos) junto con
el baseline sin adapter. Gana la de EX ponderado más alto; en empate gana A por ser más liviana
(merge `< 1.5 GB` en T4 tras `merge_and_unload`). Toda evidencia (parámetros entrenables,
tiempo, curvas de loss) queda en `resultados/entrenamiento_*.json` y `resultados/loss_*.png`.

---

### Lo que reportará cada corrida (rellenar en `notebooks/02_entrenamiento.ipynb`)

| Config | Parámetros entrenables | % del total | Tiempo de entrenamiento (T4) | Loss train/eval final | ¿Se cumplió la hipótesis? |
|---|---|---|---|---|---|
| A | _(pendiente)_ | | | | |
| B | _(pendiente)_ | | | | |

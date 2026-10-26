# Hipótesis de las configuraciones LoRA

Escritas antes de entrenar (2026-10-25 · José Ordóñez). Las dos configuraciones difieren en
**un solo factor: los `target_modules`**. Fijo en ambas: `r = 16`, `alpha = 32`, `dropout = 0.05`,
`lr = 2e-4` coseno con warmup 3%, **1 época**, batch efectivo 16 (batch 1 × acumulación 16),
`max_len = 2048`, semilla 2026. El dataset es el mismo: 2,840 pares + 360 de reparación
(3,200 ejemplos de chat).

| Factor | Config A | Config B |
|---|---|---|
| `target_modules` | `q_proj, k_proj, v_proj, o_proj` (solo atención) | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` (atención + MLP) |

## Config A — solo atención

- **Hipótesis:** el mayor aporte del fine-tuning en text-to-SQL está en el *formato* y la copia
  de nombres desde el esquema (atender tokens del COMMENT y del CREATE TABLE). Con solo las
  matrices de atención (r=16) debería bastar y capturar casi todo el margen de mejora.
- **Esperado:** ≈4× menos parámetros entrenables que B → entrena más rápido en T4 (estimado
  35–40 min) y menos riesgo de sobreajuste a las plantillas.

## Config B — atención + MLP

- **Hipótesis:** agregar los projectores gate/up/down da capacidad de computo adicional
  (las preguntas difíciles: funciones de ventana, `WITH`, fechas) que con solo atención
  no se alcanza.
- **Esperado:** mejor EX en nivel difícil (+0.05 sobre A en ese subconjunto, es la apuesta),
  a cambio de ~4× parámetros entrenables, más tiempo de entrenamiento y algo más de memoria
  en T4.

## Cómo se decide

Se entrena A y B con el mismo dataset y partición, se evalúa en la validación propia
(40 preguntas sobre 2 esquemas no vistos) junto con el baseline sin adapter. Gana la de
EX ponderado más alto; en empate gana A por ser más liviana. La evidencia (parámetros
entrenables, tiempo, curvas de loss) queda en `resultados/entrenamiento_{A,B}.json` y
`resultados/loss_{A,B}.png`. El adapter ganador se copia a `adapter/`.

---

### Lo que reporta cada corrida (se completa en `notebooks/02_entrenamiento.ipynb`)

| Config | Parámetros entrenables | Tiempo (T4) | Eval loss final | ¿Se cumplió la hipótesis? |
|---|---|---|---|---|
| A | _(pendiente)_ | | | |
| B | _(pendiente)_ | | | |

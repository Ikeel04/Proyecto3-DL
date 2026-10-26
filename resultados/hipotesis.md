# Hipótesis de las configuraciones LoRA

Escritas antes de entrenar (2026-10-25 · José Ordóñez). Las dos configuraciones difieren en
**un solo factor: los `target_modules`**. Fijo en ambas: `r = 16`, `alpha = 32`, `dropout = 0.05`,
`lr = 2e-4` coseno con warmup 3%, **1 época**, batch efectivo 16 (batch 1 × acumulación 16),
`max_len = 2048`, semilla 2026. El dataset es el mismo: 2,840 pares + 360 de reparación
(3,200 construidos; se entrenó con 3,000 — 2,640 pares + 360 de reparación — y 200 pares
quedaron apartados solo para la curva de loss).

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
| A (solo atención) | 4,358,144 (0.282 %) | 42.5 min | 0.0042 | **Sí** — capturó casi todo el margen con 4.2× menos parámetros (ver veredicto) |
| B (atención + MLP) | 18,464,768 (1.182 %) | 57.2 min | 0.0043 | **No** — eval loss igual que A y sobreajustó en difícil (ver veredicto) |

## Veredicto (2026-10-25, con datos)

EX sobre la validación propia (40 preguntas; pesos del docente 1/2/3):

| corrida | EX | F / M / D |
|---|---|---|
| base_greedy (sin adapter) | 0.575 | 0.77 / 0.86 / 0.31 |
| **A_greedy (ganadora)** | **0.675** | 0.85 / 0.57 / 0.69 |
| B_greedy | 0.562 | 0.85 / 0.57 / 0.46 |
| final (A + beam 4 + ejecutar) | 0.662 | 0.92 / 0.71 / 0.54 |
| base_final (base + beam 4 + ejecutar) | 0.725 | 0.85 / 0.93 / 0.54 |

1. **La hipótesis de A se cumplió**: con solo las matrices de atención (4.35 M parámetros,
 42.5 min) capturó la mejora central del fine-tuning — *copia de nombres desde el esquema y
 formato* — mejorando al baseline +0.100 EX en greedy (0.575 → 0.675), sobre todo porque
 rescata el nivel difícil (D 0.31 → 0.69).
2. **La de B se refutó**: la apuesta era +0.05 sobre A en difícil; lo real fue lo contrario
 (D 0.46 vs 0.69 de A, EX global 0.562 vs 0.675). Con el train loss ya saturado (~0.004),
 los 18.5 M parámetros adicionales no comprimieron mejor el dataset: sobreajustaron las
 plantillas y generalizaron peor justo donde B debía ganar.
3. El **eval loss no distinguió** a las configs (0.0042 vs 0.0043): la decisión se tomó por EX,
 tal como dictaba el protocolo. El loss dijo "empate técnico"; la ejecución mostró la
 diferencia real — argumento a favor de evaluar SQL ejecutándolo. Ganadora: `config_A` → `adapter/`.
4. Contra el **pipeline completo** (beam 4 + ejecutar/reparar), el LoRA no superó al base
 (0.662 vs 0.725 base_final): el reparador rescata más las salidas *"casi correctas"* del
 modelo general que las del modelo afinado. Con n=40, la diferencia queda dentro del IC 90 %
 del bootstrap ([0.53, 0.80]) — se reporta como estadísticamente emparejada, y esa incertidumbre
 es la que justifica el rango de `resultados/prediccion.json`.
5. Corridas con flags idénticas (mejor_beam vs final) produjeron EX **idénticos** — el protocolo
 es determinista con semilla 2026.

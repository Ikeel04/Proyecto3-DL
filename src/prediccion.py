"""Predicción justificada del EX en la evaluación oculta.

Lee resultados/validacion_propia.csv (el CSV de la corrida `final`) y produce
resultados/prediccion.json con el formato que consume generar_presentacion.py:
    {ex_val, ic_bajo, ic_alto, prediccion, rango, razones}

La base es un bootstrap del EX ponderado de la validación; sobre él:
 · −0.05 por estilo de pregunta (nuestras salen de plantillas propias, las del docente
   serán más variadas);
 · +0.02 * porcentaje de errores "reparables" (sintaxis o columna inexistentes que el
   paso de ejecutar + reparar suele poder alear);
 · el rango del informe nace del intervalo de confianza, holgado hacia abajo por si
   los esquemas ocultos traen 8–10 tablas.

Uso:
    python src/prediccion.py                # usa resultados/validacion_propia.csv
    python src/prediccion.py --csv resultados/eval_final.csv
"""
import argparse
import csv
import json
import os
import random
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
RES = os.path.join(RAIZ, "resultados")
B, SEMILLA = 2000, 2026


def ex_bootstrap(filas):
    rng = random.Random(SEMILLA)
    vals = []
    for f in filas:
        f["peso"] = int(f["peso"])
        f["acierto"] = int(f["acierto"])
    tp = sum(f["peso"] for f in filas)
    for _ in range(B):
        m = [rng.choice(filas) for _ in filas]
        vals.append(sum(r["peso"] * r["acierto"] for r in m) / tp)
    vals.sort()
    ex = sum(r["peso"] * r["acierto"] for r in filas) / tp
    return ex, vals[int(0.05 * B)], vals[int(0.95 * B)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(RES, "validacion_propia.csv"))
    ap.add_argument("--salida", default=os.path.join(RES, "prediccion.json"))
    a = ap.parse_args()

    with open(a.csv, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        raise SystemExit(f"CSV vacío: {a.csv}")

    ex_val, ic_bajo, ic_alto = ex_bootstrap(filas)
    errores = Counter(r["categoria_error"] or "" for r in filas
                      if int(r["acierto"]) == 0 and r["categoria_error"])
    ex_facil = (sum(int(r["acierto"]) for r in filas if r["nivel"] == "facil")
                / max(sum(1 for r in filas if r["nivel"] == "facil"), 1))
    reparables_pct = ((errores.get("sintaxis", 0) + errores.get("columna_o_tabla_inexistente", 0))
                      / max(sum(errores.values()), 1)) if errores else 0.0

    # ajustes por estilo de la evaluación oculta (justificados en las razones)
    ajuste = round(-0.05 + 0.02 * reparables_pct, 3)
    prediccion = round(max(0.0, ex_val + ajuste), 3)
    rango = [round(max(0.0, min(ic_bajo, ex_val) - 0.10), 2),
             round(min(1.0, max(ic_alto, prediccion) + 0.02), 2)]

    razones = [
        f"EX ponderada en la validación propia (pipeline de entrega): {ex_val:.3f}.",
        f"Fácil acierta {ex_facil:.2f}; los pesos 1/2/3 del docente premian de forma parecida.",
        f"El {reparables_pct:.0%} de los fallos en la validación fue sintaxis o columna/tabla inexistente, que es justo lo que el paso de ejecutar + reparar suele poder corregir.",
        f"Bootstrap de {B} re-muestreos sobre las {len(filas)} preguntas (semilla {SEMILLA}): "
        f"IC 90% = [{ic_bajo:.2f}, {ic_alto:.2f}].",
        "Ajuste final por estilo: −0.05 (preguntas ocultas más variadas y hasta 10 tablas por esquema) "
        f"más +0.02 por la proporción reparable de errores ({reparables_pct:.0%}) en la validación.",
    ]

    out = {
        "ex_val": round(ex_val, 3), "ic_bajo": round(ic_bajo, 2), "ic_alto": round(ic_alto, 2),
        "ajuste": ajuste, "prediccion": prediccion, "rango": rango, "razones": razones,
        "errores_por_categoria": dict(errores),
    }
    with open(a.salida, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"EX validación = {ex_val:.3f} · ajuste {ajuste:+.3f} → predicción {prediccion:.2f} "
          f"(rango {rango[0]}–{rango[1]})")
    print("Escrito:", a.salida)


if __name__ == "__main__":
    main()

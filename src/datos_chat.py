"""Convierte train.jsonl + reparaciones.jsonl al formato de chat para el fine-tuning.

Produce:
    datos/entrenamiento/dataset_chat.jsonl   (prácticamente todo)
    datos/entrenamiento/dataset_eval.jsonl   (200 pares separados solo para la curva de loss)

Cada línea = {"mensajes": [system, user, assistant], "db", "id", "tipo"} de modo que el user
se construye EXACTAMENTE igual que en solucion.py (mismo sistema, misma compactación del
esquema, mismas secciones ### Esquema / ### Pregunta / ### SQL) y los ejemplos de reparación
usan el mismo formato de corrección que la inferencia usa con `ejecutar`.

Uso:
    python src/datos_chat.py
    python src/datos_chat.py --n-eval 200 --semilla 2026
"""
import argparse
import json
import os
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
os.environ.setdefault("T2SQL_SOLO_PROMPT", "1")  # evita cargar el modelo al importar solucion
sys.path.insert(0, RAIZ)  # para importar solucion.py desde src/
import solucion  # noqa: E402  (funciones de prompt; no carga el modelo)

ESQUEMAS = os.path.join(RAIZ, "datos", "esquemas", "train")


def mensajes_de_par(par, tipo="genera"):
    """Mensajes de chat para un par (generación normal o reparación con error)."""
    with open(os.path.join(ESQUEMAS, f"{par['db']}.schema.sql"), encoding="utf-8") as f:
        esquema = f.read()
    if tipo == "reparacion":
        msj = solucion.construir_mensajes(esquema, par["pregunta"],
                                          sql_previa=par["sql_erronea"], error=par["error"])
    else:
        msj = solucion.construir_mensajes(esquema, par["pregunta"])
    msj = list(msj) + [{"role": "assistant", "content": par["sql"]}]
    return msj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-jsonl", default=os.path.join(RAIZ, "datos", "entrenamiento", "train.jsonl"))
    ap.add_argument("--reparaciones-jsonl", default=os.path.join(RAIZ, "datos", "entrenamiento", "reparaciones.jsonl"))
    ap.add_argument("--salida-train", default=os.path.join(RAIZ, "datos", "entrenamiento", "dataset_chat.jsonl"))
    ap.add_argument("--salida-eval", default=os.path.join(RAIZ, "datos", "entrenamiento", "dataset_eval.jsonl"))
    ap.add_argument("--n-eval", type=int, default=200, help="pares separados para la curva de loss")
    ap.add_argument("--semilla", type=int, default=2026)
    a = ap.parse_args()

    pares = [json.loads(l) for l in open(a.train_jsonl, encoding="utf-8")]
    reparaciones = [json.loads(l) for l in open(a.reparaciones_jsonl, encoding="utf-8")]
    rng = random.Random(a.semilla)

    idx = list(range(len(pares)))
    rng.shuffle(idx)
    idx_eval = set(idx[:a.n_eval])

    escritos = {"genera": 0, "reparacion": 0}
    with open(a.salida_train, "w", encoding="utf-8") as ft, open(a.salida_eval, "w", encoding="utf-8") as fe:
        for i, par in enumerate(pares):
            tipo = "genera"
            ejemplo = {"mensajes": mensajes_de_par(par, tipo), "db": par["db"],
                       "id": par["id"], "tipo": tipo}
            (fe if i in idx_eval else ft).write(json.dumps(ejemplo, ensure_ascii=False) + "\n")
            escritos[tipo] += 1
        for par in reparaciones:  # las reparaciones van siempre a train
            tipo = "reparacion"
            ejemplo = {"mensajes": mensajes_de_par(par, tipo), "db": par["db"],
                       "id": par["id"], "tipo": tipo}
            ft.write(json.dumps(ejemplo, ensure_ascii=False) + "\n")
            escritos[tipo] += 1

    print(f"dataset_chat.jsonl : {escritos['genera'] + escritos['reparacion']} ejemplos")
    print(f"  - generación     : {escritos['genera']}")
    print(f"  - reparación     : {escritos['reparacion']}")
    n_eval = sum(1 for _ in open(a.salida_eval, encoding="utf-8"))
    print(f"dataset_eval.jsonl : {n_eval} pares (solo para eval loss)")
    ej = solucion.construir_mensajes("", "")  # sanity: solucion cargó sin modelo
    assert ej[0]["role"] == "system"


if __name__ == "__main__":
    main()

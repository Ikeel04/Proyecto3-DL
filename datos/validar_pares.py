"""
Genera los pares de entrenamiento y deja solo los que se ejecutan sin error en MySQL.

Criterios de descarte (cada descarte queda en datos/descartes/descartes.csv con su motivo):
  - error_mysql      : la consulta falla en MySQL 8.4 (sintaxis, ONLY_FULL_GROUP_BY, etc.)
  - resultado_vacio  : se ejecuta pero no devuelve filas (no sirve para medir por ejecución)
  - duplicado        : misma pregunta o mismo par (esquema, sql) ya incluido
  - resultado_grande : más de 2000 filas (preguntas poco útiles)

Uso:
    python datos/validar_pares.py --socket /tmp/mysql.sock
    python datos/validar_pares.py --host 127.0.0.1 --user root --password ""
"""
import argparse
import csv
import json
import os
import random
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from esquemas_spec import TRAIN  # noqa: E402
from generar_pares import generar_todos  # noqa: E402
from construir_esquemas import conectar  # noqa: E402

SEMILLAS = [2026, 2027]
MAX_POR_ESQUEMA = 270


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    ap.add_argument("--socket", default=None)
    a = ap.parse_args()

    conn = conectar(a.host, a.user, a.password, a.port, unix_socket=a.socket)
    aceptados, descartes = [], []
    for esq in TRAIN:
        candidatos = []
        for s in SEMILLAS:
            candidatos += generar_todos(esq, s)
        vistos_q, vistos_sql = set(), set()
        buenos = []
        with conn.cursor() as cur:
            cur.execute(f"USE `{esq['db']}`")
            cur.execute("SET SESSION max_execution_time = 5000")
            for p in candidatos:
                motivo, detalle = None, ""
                if p["pregunta"] in vistos_q or p["sql"] in vistos_sql:
                    motivo = "duplicado"
                else:
                    try:
                        cur.execute(p["sql"])
                        filas = cur.fetchall()
                        if len(filas) == 0:
                            motivo = "resultado_vacio"
                        elif len(filas) > 2000:
                            motivo = "resultado_grande"
                        else:
                            p["n_filas"] = len(filas)
                    except Exception as e:  # noqa: BLE001
                        motivo, detalle = "error_mysql", str(e)[:200]
                if motivo:
                    descartes.append({**p, "motivo": motivo, "detalle": detalle})
                else:
                    vistos_q.add(p["pregunta"])
                    vistos_sql.add(p["sql"])
                    buenos.append(p)
        # recorte balanceado por patrón para que ningún esquema domine
        rng = random.Random(f"recorte-{esq['db']}")
        rng.shuffle(buenos)
        if len(buenos) > MAX_POR_ESQUEMA:
            por_patron = Counter()
            elegidos, sobrantes = [], []
            for p in buenos:
                (elegidos if por_patron[p["patron"]] < 4 else sobrantes).append(p)
                por_patron[p["patron"]] += 1
            resto = MAX_POR_ESQUEMA - len(elegidos)
            elegidos += sobrantes[:max(resto, 0)]
            for p in sobrantes[max(resto, 0):]:
                descartes.append({**p, "motivo": "recorte_balance", "detalle": "excede el máximo por esquema"})
            buenos = elegidos[:MAX_POR_ESQUEMA]
        aceptados += buenos
        print(f"{esq['db']}: {len(buenos)} aceptados")

    os.makedirs(os.path.join(AQUI, "entrenamiento"), exist_ok=True)
    os.makedirs(os.path.join(AQUI, "descartes"), exist_ok=True)
    with open(os.path.join(AQUI, "entrenamiento", "train.jsonl"), "w", encoding="utf-8") as f:
        for i, p in enumerate(aceptados):
            p["id"] = f"tr{i:05d}"
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with open(os.path.join(AQUI, "descartes", "descartes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["db", "nivel", "patron", "motivo", "detalle", "pregunta", "sql"], extrasaction="ignore")
        w.writeheader()
        w.writerows(descartes)

    resumen = {
        "aceptados": len(aceptados),
        "por_nivel": Counter(p["nivel"] for p in aceptados),
        "por_esquema": Counter(p["db"] for p in aceptados),
        "descartados": len(descartes),
        "descartes_por_motivo": Counter(d["motivo"] for d in descartes),
        "patrones_distintos": len({p["patron"] for p in aceptados}),
    }
    with open(os.path.join(AQUI, "descartes", "resumen_descartes.json"), "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

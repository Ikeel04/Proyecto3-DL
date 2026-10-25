"""
Ejemplos de reparación: (pregunta, consulta incorrecta, error real de MySQL) -> consulta correcta.

Se toman pares ya validados de train.jsonl, se rompen a propósito con errores típicos
de un LLM (columna o tabla con nombre equivocado, GROUP BY olvidado, error de sintaxis)
y se ejecutan en MySQL para guardar el mensaje de error real. Solo se aceptan si la
consulta rota efectivamente falla. Estos ejemplos entrenan el paso de corrección que
usa generar_sql() cuando el evaluador entrega ejecutar().

Uso:
    python datos/generar_reparaciones.py --socket /tmp/mysql.sock
"""
import argparse
import json
import os
import random
import re
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from construir_esquemas import conectar  # noqa: E402
from esquemas_spec import TRAIN  # noqa: E402

N_OBJETIVO = 360


def columnas_y_tablas(db):
    esq = next(e for e in TRAIN if e["db"] == db)
    cols = {c[0] for t in esq["tablas"] for c in t["cols"]}
    tablas = {t["name"] for t in esq["tablas"]}
    return cols, tablas


def romper(sql, db, rng):
    cols, tablas = columnas_y_tablas(db)
    tipo = rng.choice(["columna", "columna", "tabla", "group_by", "sintaxis"])
    if tipo == "columna":
        usadas = [c for c in cols if re.search(rf"\b{c}\b", sql)]
        if not usadas:
            return None
        c = rng.choice(usadas)
        variantes = [c + "s", c.replace("_", ""), c.split("_")[-1] if "_" in c else c + "_id",
                     "nombre" if c != "nombre" else "name", c + "_total"]
        nueva = rng.choice([v for v in variantes if v not in cols] or [c + "_x"])
        return tipo, re.sub(rf"\b{c}\b", nueva, sql, count=1)
    if tipo == "tabla":
        usadas = [t for t in tablas if re.search(rf"\b(FROM|JOIN) {t}\b", sql)]
        if not usadas:
            return None
        t = rng.choice(usadas)
        nueva = t[:-2] if t.endswith("es") and len(t) > 4 else (t[:-1] if t.endswith("s") else t + "s")
        if nueva in tablas:
            nueva = t + "_tbl"
        return tipo, re.sub(rf"\b(FROM|JOIN) {t}\b", rf"\1 {nueva}", sql, count=1)
    if tipo == "group_by":
        if "GROUP BY" not in sql or "WITH" in sql or "OVER" in sql:
            return None
        rota = re.sub(r" GROUP BY .+?(?= HAVING| ORDER BY| LIMIT|$)", "", sql, count=1)
        rota = re.sub(r" HAVING .+?(?= ORDER BY| LIMIT|$)", "", rota, count=1)
        return tipo, rota
    # sintaxis
    opciones = [(" FROM ", " FORM "), (", ", " "), (" AS ", " AS AS "), (" BY ", " "), ("(", "((")]
    a, b = rng.choice([o for o in opciones if o[0] in sql] or [(" FROM ", " FORM ")])
    return tipo, sql.replace(a, b, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    ap.add_argument("--socket", default=None)
    a = ap.parse_args()

    pares = [json.loads(l) for l in open(os.path.join(AQUI, "entrenamiento", "train.jsonl"), encoding="utf-8")]
    rng = random.Random(2026)
    rng.shuffle(pares)
    conn = conectar(a.host, a.user, a.password, a.port, unix_socket=a.socket)
    salida, rechazados = [], Counter()
    with conn.cursor() as cur:
        for p in pares:
            if len(salida) >= N_OBJETIVO:
                break
            r = romper(p["sql"], p["db"], rng)
            if not r or r[1] == p["sql"]:
                rechazados["sin_cambio"] += 1
                continue
            tipo, rota = r
            cur.execute(f"USE `{p['db']}`")
            try:
                cur.execute(rota)
                cur.fetchall()
                rechazados["no_falla"] += 1  # la versión rota corre: no sirve como ejemplo de error
                continue
            except Exception as e:  # noqa: BLE001
                err = str(e)
            salida.append({**p, "id": "rp" + p["id"][2:], "tipo": "reparacion", "error_tipo": tipo,
                           "sql_erronea": rota, "error": err})
    with open(os.path.join(AQUI, "entrenamiento", "reparaciones.jsonl"), "w", encoding="utf-8") as f:
        for s in salida:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print("reparaciones:", len(salida), dict(Counter(s["error_tipo"] for s in salida)), "rechazados:", dict(rechazados))


if __name__ == "__main__":
    main()

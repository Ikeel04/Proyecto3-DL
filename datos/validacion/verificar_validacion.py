"""Verifica las preguntas de validación propia contra MySQL 8.4.

Corre la consulta de referencia de cada pregunta, revisa que ejecute sin
error, que devuelva al menos una fila y que ninguna caché de resultados,
incluso los ceros de COUNT(*), pase inadvertida como vacía.
Si todo sale bien escribe un mensaje de resumen; regresando exit code 1 si algo falla.

Uso:
    python datos/validacion/verificar_validacion.py [--host 127.0.0.1 --port 3306]
                                                    [--user root --password ""]
"""
import argparse
import json
import os
import sys

import pymysql

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--socket", default=None)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    args = ap.parse_args()

    with open(os.path.join(AQUI, "validacion_propia.json"), encoding="utf-8") as f:
        preguntas = json.load(f)

    conn = pymysql.connect(host=args.host, user=args.user, password=args.password,
                           port=args.port,
                           **({"unix_socket": args.socket} if args.socket else {}))
    cur = conn.cursor()

    ok, problemas = 0, []
    for p in preguntas:
        try:
            cur.execute(f"USE {p['db']}")
            cur.execute(p["sql"])
            columnas = [d[0] for d in cur.description] if cur.description else []
            filas = cur.fetchall()
            if not filas:
                problemas.append((p["id"], "resultado vacío"))
                print(f"[X] {p['id']:<8} resultado vacío")
                continue
            if len(filas) == 1 and len(columnas) == 1 and filas[0][0] in (0, None):
                problemas.append((p["id"], "contador en cero"))
                print(f"[X] {p['id']:<8} contador en cero")
                continue
            ok += 1
            print(f"[✓] {p['id']:<8} filas={len(filas)}")
        except Exception as e:  # noqa: BLE001
            problemas.append((p["id"], str(e)))
            print(f"[X] {p['id']:<8} ERROR: {e}")

    niveles = {}
    dbs = {}
    for p in preguntas:
        niveles[p["nivel"]] = niveles.get(p["nivel"], 0) + 1
        dbs[p["db"]] = dbs.get(p["db"], 0) + 1

    print(f"\nAprobadas: {ok}/{len(preguntas)} · niveles: {niveles} · por esquema: {dbs}")
    if problemas:
        print("Fallaron:")
        for pid, motivo in problemas:
            print(f"  - {pid}: {motivo}")
        sys.exit(1)


if __name__ == "__main__":
    main()

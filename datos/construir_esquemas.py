"""
Construye los esquemas propios: genera datos sintéticos (deterministas), escribe un
.sql por base (CREATE + INSERT) y, si hay MySQL disponible, carga las bases y guarda
el texto de SHOW CREATE TABLE, que es justo lo que recibe generar_sql() en la evaluación.

Uso:
    python datos/construir_esquemas.py --host 127.0.0.1 --user root --password ""
"""
import argparse
import datetime as dt
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esquemas_spec import TRAIN, VAL, NOMBRES, APELLIDOS  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
SEMILLA = 2026


# ------------------------------------------------------------------ generación de datos
def _fecha(rng, a, b, con_hora=False):
    a = dt.datetime.fromisoformat(a)
    b = dt.datetime.fromisoformat(b)
    seg = rng.randint(0, int((b - a).total_seconds()))
    d = a + dt.timedelta(seconds=seg)
    if con_hora:
        d = d.replace(minute=(d.minute // 5) * 5, second=0)
        return d.strftime("%Y-%m-%d %H:%M:%S")
    return d.strftime("%Y-%m-%d")


def generar_datos(esquema, semilla=SEMILLA):
    """Devuelve {tabla: [fila(dict), ...]} respetando las FK."""
    rng = random.Random(f"{semilla}-{esquema['db']}")
    datos = {}
    for t in esquema["tablas"]:
        filas = []
        usados = {}
        for i in range(1, t["n"] + 1):
            fila = {}
            for (col, tipo, gen, rol, _lbl, _com) in t["cols"]:
                nulo = gen.startswith("?")
                g = gen[1:] if nulo else gen
                if nulo and rng.random() < 0.15:
                    fila[col] = None
                    continue
                kind, _, arg = g.partition(":")
                if kind == "pk":
                    v = i
                elif kind == "fk":
                    padres = [r for r in datos[arg]]
                    pk_padre = next(c[0] for c in _tabla(esquema, arg)["cols"] if c[3] in ("pk", "pk_text"))
                    # distribución sesgada para que haya grupos de distinto tamaño
                    idx = min(int(rng.paretovariate(1.3)) - 1, len(padres) - 1) if rng.random() < 0.3 else rng.randrange(len(padres))
                    v = padres[idx][pk_padre]
                elif kind == "persona":
                    v = f"{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)}"
                    k = 0
                    while v in usados.setdefault(col, set()) and k < 30:
                        v = f"{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}"
                        k += 1
                elif kind == "combo":
                    a, b = arg.split(";")
                    a, b = a.split("|"), b.split("|")
                    v = f"{rng.choice(a)} {rng.choice(b)}"
                    k = 0
                    while v in usados.setdefault(col, set()) and k < 40:
                        v = f"{rng.choice(a)} {rng.choice(b)}"
                        k += 1
                    if v in usados[col]:
                        v = f"{v} {i}"
                elif kind == "lista":
                    v = arg.split("|")[i - 1]
                elif kind == "cat":
                    opciones = arg.split("|")
                    pesos = [len(opciones) - j + 1 for j in range(len(opciones))]  # no uniformes
                    v = rng.choices(opciones, weights=pesos)[0]
                elif kind == "int":
                    lo, hi = map(int, arg.split(":"))
                    v = rng.randint(lo, hi)
                elif kind == "dec":
                    lo, hi = map(float, arg.split(":"))
                    # sesgo hacia valores bajos, más realista para montos
                    v = round(lo + (hi - lo) * (rng.random() ** 1.6), 2)
                elif kind == "date":
                    a, b = arg.split(":")
                    v = _fecha(rng, a, b)
                elif kind == "datetime":
                    a, b = arg.split(":")
                    v = _fecha(rng, a, b, True)
                elif kind == "bool":
                    v = 1 if rng.random() < 0.3 else 0
                elif kind == "text":
                    v = f"{arg}{i:03d}" if arg.endswith(("-", "A")) or arg in ("Hab",) else f"{arg} {i}"
                elif kind == "email":
                    v = f"usuario{i}@correo.com"
                else:
                    raise ValueError(gen)
                usados.setdefault(col, set()).add(v)
                fila[col] = v
            # coherencia: fechas de devolución posteriores al préstamo, origen != destino
            if "fecha_devolucion" in fila and fila["fecha_devolucion"] is not None:
                f0 = dt.date.fromisoformat(fila["fecha_prestamo"])
                fila["fecha_devolucion"] = (f0 + dt.timedelta(days=rng.randint(1, 40))).isoformat()
            if "origen" in fila and "destino" in fila and fila["origen"] == fila["destino"]:
                otros = [r["codigo_iata"] for r in datos["aeropuertos"] if r["codigo_iata"] != fila["origen"]]
                fila["destino"] = rng.choice(otros)
            if "id_local" in fila and fila["id_local"] == fila["id_visitante"]:
                fila["id_visitante"] = fila["id_local"] % len(datos["equipos"]) + 1
            filas.append(fila)
        datos[t["name"]] = filas
    return datos


def _tabla(esquema, nombre):
    return next(t for t in esquema["tablas"] if t["name"] == nombre)


def pk_de(tabla):
    return next(c[0] for c in tabla["cols"] if c[3] in ("pk", "pk_text"))


# ------------------------------------------------------------------ DDL
def _q(s):
    return "'" + str(s).replace("\\", "\\\\").replace("'", "''") + "'"


def ddl(esquema):
    out = []
    for t in esquema["tablas"]:
        lineas = []
        for (col, tipo, gen, rol, lbl, com) in t["cols"]:
            nulo = gen.startswith("?")
            comentario = com if com else lbl.split(" ", 1)[1]
            if gen.startswith("fk:") and not com:
                comentario = "id de " + lbl.split(" ", 1)[1]
            extra = " AUTO_INCREMENT" if gen == "pk" else ""
            lineas.append(f"  `{col}` {tipo} {'NULL' if nulo else 'NOT NULL'}{extra} COMMENT {_q(comentario)}")
        lineas.append(f"  PRIMARY KEY (`{pk_de(t)}`)")
        for (col, tipo, gen, rol, lbl, com) in t["cols"]:
            if gen.startswith("fk:"):
                padre = _tabla(esquema, gen[3:])
                lineas.append(f"  CONSTRAINT `fk_{t['name']}_{col}` FOREIGN KEY (`{col}`) REFERENCES `{padre['name']}` (`{pk_de(padre)}`)")
        out.append(f"CREATE TABLE `{t['name']}` (\n" + ",\n".join(lineas) +
                   f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT={_q(t['comment'])};")
    return out


def inserts(esquema, datos):
    out = []
    for t in esquema["tablas"]:
        cols = [c[0] for c in t["cols"]]
        filas = datos[t["name"]]
        for k in range(0, len(filas), 200):
            vals = []
            for f in filas[k:k + 200]:
                vals.append("(" + ", ".join("NULL" if f[c] is None else (str(f[c]) if isinstance(f[c], (int, float)) else _q(f[c])) for c in cols) + ")")
            out.append(f"INSERT INTO `{t['name']}` ({', '.join('`'+c+'`' for c in cols)}) VALUES\n" + ",\n".join(vals) + ";")
    return out


def script_sql(esquema, datos):
    db = esquema["db"]
    partes = [f"DROP DATABASE IF EXISTS `{db}`;",
              f"CREATE DATABASE `{db}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;",
              f"USE `{db}`;"]
    partes += ddl(esquema) + inserts(esquema, datos)
    return "\n\n".join(partes) + "\n"


# ------------------------------------------------------------------ MySQL
def conectar(host, user, password, port=3306, database=None, unix_socket=None):
    import pymysql
    kw = dict(host=host, user=user, password=password, port=port, charset="utf8mb4", autocommit=True)
    if unix_socket:
        kw["unix_socket"] = unix_socket
    if database:
        kw["database"] = database
    return pymysql.connect(**kw)


def cargar_sql(conn, texto):
    with conn.cursor() as cur:
        for stmt in texto.split(";\n"):
            if stmt.strip():
                cur.execute(stmt)


def show_create(conn, db):
    with conn.cursor() as cur:
        cur.execute(f"USE `{db}`")
        cur.execute("SHOW TABLES")
        tablas = [r[0] for r in cur.fetchall()]
        textos = []
        for t in tablas:
            cur.execute(f"SHOW CREATE TABLE `{t}`")
            textos.append(cur.fetchone()[1] + ";")
    return "\n\n".join(textos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    ap.add_argument("--socket", default=None)
    ap.add_argument("--sin-mysql", action="store_true", help="solo escribe los .sql")
    ap.add_argument("--crear-lector", action="store_true", help="crea el usuario de solo lectura lector/lector")
    a = ap.parse_args()

    conn = None if a.sin_mysql else conectar(a.host, a.user, a.password, a.port, unix_socket=a.socket)
    resumen = {}
    for split, lista in (("train", TRAIN), ("val", VAL)):
        carpeta = os.path.join(AQUI, "esquemas", split)
        os.makedirs(carpeta, exist_ok=True)
        for esq in lista:
            datos = generar_datos(esq)
            sql = script_sql(esq, datos)
            with open(os.path.join(carpeta, f"{esq['db']}.sql"), "w", encoding="utf-8") as f:
                f.write(sql)
            if conn:
                cargar_sql(conn, sql)
                with open(os.path.join(carpeta, f"{esq['db']}.schema.sql"), "w", encoding="utf-8") as f:
                    f.write(show_create(conn, esq["db"]))
            resumen[esq["db"]] = {"split": split, "tablas": len(esq["tablas"]),
                                  "filas": sum(len(v) for v in datos.values())}
            print(f"[{split}] {esq['db']}: {resumen[esq['db']]['tablas']} tablas, {resumen[esq['db']]['filas']} filas")
    if conn and a.crear_lector:
        with conn.cursor() as cur:
            for host in ("localhost", "%"):
                cur.execute(f"CREATE USER IF NOT EXISTS 'lector'@'{host}' IDENTIFIED BY 'lector'")
                for db in resumen:
                    cur.execute(f"GRANT SELECT ON `{db}`.* TO 'lector'@'{host}'")
        print("usuario de solo lectura: lector / lector")
    with open(os.path.join(AQUI, "esquemas", "resumen.json"), "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

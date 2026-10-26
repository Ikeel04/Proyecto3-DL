"""Evaluador por ejecución para la validación propia (igual criterio que el docente).

- Corre la pregunta con solucion.generar_sql (prompt y experimentos de solucion.py).
- ejecutar() replica el contrato del docente: ejecuta en MySQL (solo lectura), devuelve
  {ok, columnas, filas (máx. 10), error}.
- Acierto = el RESULTADO de la consulta generada coincide con el de la referencia:
  · los números se redondean a 2 decimales;
  · el orden de filas solo cuenta si la pregunta lo pide (`ordenado`);
  · una columna adicional no penaliza (se buscan las columnas de la referencia
    dentro de las generadas en cualquier orden);
  · si la referencia devuelve <= 10 filas se compara el conjunto completo.
- Categorías de error: sintaxis, columna_o_tabla_inexistente, join, agregacion,
  filtro, resultado_distinto.

Salidas (nombres fijos que consume generar_presentacion.py):
    resultados/eval_<nombre>.json  ·  resultados/eval_<nombre>.csv
    y para `--nombre final` además  resultados/validacion_propia.csv
"""
import argparse
import csv
import json
import os
import shutil
import sys
from collections import Counter
from decimal import Decimal

import pymysql

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
RES = os.path.join(RAIZ, "resultados")
PESOS = {"facil": 1, "media": 2, "dificil": 3}
CATEGORIAS = ["sintaxis", "columna_o_tabla_inexistente", "join", "agregacion", "filtro",
              "resultado_distinto"]


# ------------------------------------------------------------ ejecutar como la da el docente
class Ejecutor:
    def __init__(self, db, conn_args):
        self.db = db
        self.args = conn_args
        self.llamadas = 0

    def __call__(self, sql):
        self.llamadas += 1
        try:
            conn = pymysql.connect(**self.args, database=self.db)
            with conn.cursor() as cur:
                cur.execute(sql)
                columnas = [d[0] for d in cur.description] if cur.description else []
                filas = cur.fetchmany(10)
            conn.close()
            return {"ok": True, "columnas": columnas, "filas": filas, "error": ""}
        except Exception as e:  # noqa: BLE001
            try:
                conn.close()
            except Exception:  # noqa: S110
                pass
            return {"ok": False, "columnas": [], "filas": [], "error": str(e)}


# ------------------------------------------------------------ comparación de resultados
def normalizar(valor):
    """Números → float redondeado a 2 decimales. Lo demás → str."""
    if valor is None:
        return None
    if isinstance(valor, bool):
        return int(valor)
    if isinstance(valor, (int, float, Decimal)):
        return round(float(valor), 2)
    s = str(valor)
    try:
        return round(float(Decimal(s)), 2)
    except Exception:  # noqa: BLE001
        return s.strip()


def multiset(filas):
    return Counter(tuple(r) for r in filas)


def conjuntos_iguales(filas_a, columnas_a, filas_b, columnas_b):
    """¿El resultado b es el mismo conjunto que a? b puede tener columnas extra, aunque
    estén en otro orden (se alinea por nombre si los nombres coinciden, o por permutación)."""
    if len(columnas_b) < len(columnas_a):
        return False
    n = len(columnas_a)
    a_norm = [tuple(normalizar(v) for v in f) for f in filas_a]
    b_norm = [[normalizar(v) for v in f] for f in filas_b]
    ms_a = Counter(a_norm)
    if n == len(columnas_b):
        return ms_a == Counter(tuple(f) for f in b_norm)
    import itertools
    # alinear por nombre de columna (caso más común)
    baja_b = [str(c).strip().lower().rsplit(".", 1)[-1] for c in columnas_b]
    baja_a = [str(c).strip().lower().rsplit(".", 1)[-1] for c in columnas_a]
    if set(baja_a) <= set(baja_b):
        idx = []
        for cab in baja_a:
            coinciden = []
            for i, cb in enumerate(baja_b):
                if cb == cab:
                    coinciden.append(i)
            idx.append(coinciden)
        nombres_unicos = all(len(i) == 1 for i in idx) and len(set(i[0] for i in idx)) == n
        if nombres_unicos:
            cols = tuple(i[0] for i in idx)
            if ms_a == Counter(tuple(f[c] for c in cols) for f in b_norm):
                return True
    # resto: probar todas las combinaciones y permutaciones
    for cols in itertools.combinations(range(len(columnas_b)), n):
        for perm in itertools.permutations(range(n)):
            if ms_a == Counter(tuple(f[cols[p]] for p in perm) for f in b_norm):
                return True
    return False


def primero_iguales(filas_a, columnas_a, filas_b, columnas_b):
    """Igualdad ordinal (importa el orden de filas), tolerando columnas extra."""
    if len(columnas_b) < len(columnas_a):
        return False
    n = len(columnas_a)
    a_norm = [tuple(normalizar(v) for v in f) for f in filas_a]
    b_norm = [[normalizar(v) for v in f] for f in filas_b]
    if n == len(columnas_b):
        return tuple(a_norm) == tuple(tuple(f) for f in b_norm)
    import itertools
    for cols in itertools.combinations(range(len(columnas_b)), n):
        for perm in itertools.permutations(range(n)):
            if all(a == tuple(f[cols[p]] for p in perm) for f, a in zip(b_norm, a_norm)):
                return True
    return False


# ------------------------------------------------------------ categorías de error
def categorizar(ref_sql, gen_sql, error, filas_ref, filas_gen, ok):
    if ok:
        return None
    if not gen_sql:
        return "sintaxis"
    if error:
        e = error.lower()
        if "1064" in error or "syntax" in e or "parse" in e:
            return "sintaxis"
        if "1054" in error or "1146" in error or "doesn't exist" in e or "unknown column" in e:
            return "columna_o_tabla_inexistente"
        if "restring" in e and "aggregate" in e:
            return "agregacion"
        if "1241" in error or "1242" in error or "operand" in e:
            return "sintaxis"
        return "sintaxis"
    # corrió sin error pero el resultado difiere
    def tiene(sql, *kws):
        u = sql.upper() if sql else ""
        return any(k in u for k in kws)

    ref_join = tiene(ref_sql, "JOIN") and ref_sql.upper().count("JOIN") >= 1
    gen_join = tiene(gen_sql, "JOIN") and gen_sql.upper().count("JOIN") >= 1
    ref_agg = tiene(ref_sql, "COUNT(", "SUM(", "AVG(", "MIN(", "MAX(", "GROUP BY", "OVER")
    gen_agg = tiene(gen_sql, "COUNT(", "SUM(", "AVG(", "MIN(", "MAX(", "GROUP BY", "OVER")
    if ref_agg and not gen_agg:
        return "agregacion"
    if ref_join and not gen_join:
        return "join"
    reffiltro = tiene(ref_sql, "WHERE", "HAVING")
    genfiltro = tiene(gen_sql, "WHERE", "HAVING")
    if reffiltro != genfiltro:
        return "filtro"
    if ref_agg and gen_agg and tiene(ref_sql, "GROUP BY") != tiene(gen_sql, "GROUP BY"):
        return "agregacion"
    if len(filas_ref) != len(filas_gen):
        return "filtro"
    return "resultado_distinto"


# ------------------------------------------------------------ corrida principal
def evaluar(nombre, mysql, adapter=None, sin_adapter=False, beams=None, ejecutar=True,
            formato="compacto", max_preguntas=None, csv_validacion=False, solucion_mod=None):
    with open(os.path.join(RAIZ, "datos", "validacion", "validacion_propia.json"), encoding="utf-8") as f:
        preguntas = json.load(f)
    if max_preguntas:
        preguntas = preguntas[:max_preguntas]

    # variables clave de solucion.py; el import es perezoso: el modelo se carga
    # en el cargar() correspondiente (así funciona sin adapter/ aún copiado)
    os.environ["T2SQL_SOLO_PROMPT"] = "1"
    os.environ["T2SQL_NUM_BEAMS"] = str(beams or 1)
    os.environ["T2SQL_USAR_EJECUTAR"] = "1" if ejecutar else "0"
    os.environ["T2SQL_FORMATO"] = formato
    if "solucion" in sys.modules:
        sys.modules.pop("solucion", None)
    if "solucion" in sys.modules:
        sys.modules.pop("solucion", None)
    _raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _raiz not in sys.path:
        sys.path.insert(0, _raiz)
    import solucion  # con T2SQL_SOLO_PROMPT=1 no carga el modelo en el import...
    if solucion_mod is not None:  # gancho para pruebas (stub sin modelo)
        solucion = solucion_mod
        globals()["solucion"] = solucion
    elif adapter:
        cfg = solucion.cargar(adapter=adapter)
    elif sin_adapter:
        cfg = solucion.cargar(usar_adapter=False)
    else:
        cfg = solucion.cargar()

    filas_salida = []
    errores_cat = Counter()
    for p in preguntas:
        with open(os.path.join(RAIZ, "datos", "esquemas", "val", f"{p['db']}.schema.sql"), encoding="utf-8") as f:
            esquema = f.read()

        ex = Ejecutor(p["db"], mysql)
        sql_gen = solucion.generar_sql(esquema, p["pregunta"], ex)
        r_gen = ex(sql_gen)
        # correr la referencia (usa el mismo ejecutor de solo lectura)
        e_ref = Ejecutor(p["db"], mysql)
        r_ref = e_ref(p["sql"])

        ok = False
        cat = None
        if r_gen.get("ok") and r_ref.get("ok"):
            filas_gen_n = [[normalizar(v) for v in fila] for fila in r_gen["filas"]]
            filas_ref_n = [[normalizar(v) for v in fila] for fila in r_ref["filas"]]
            # ejecutar entrega máx. 10 filas; el docente también, así que se comparan las primeras 10
            ref10, gen10 = filas_ref_n[:10], filas_gen_n[:10]
            if p["ordenado"]:
                ok = primero_iguales(ref10, r_ref["columnas"], gen10, r_gen["columnas"])
            else:
                ok = conjuntos_iguales(ref10, r_ref["columnas"], gen10, r_gen["columnas"])
            if not ok:
                cat = categorizar(p["sql"], sql_gen, r_gen.get("error", ""), r_ref["filas"],
                                  r_gen["filas"], ok)
        else:
            cat = categorizar(p["sql"], sql_gen, r_gen.get("error", "") or "",
                              r_ref["filas"], r_gen["filas"], False)
        if not ok and cat:
            errores_cat[cat] += 1
        filas_salida.append({
            "id": p["id"], "db": p["db"], "nivel": p["nivel"], "peso": PESOS[p["nivel"]],
            "acierto": int(ok), "categoria_error": cat or "",
            "sql_generada": sql_gen, "sql_referencia": p["sql"],
            "error": r_gen.get("error", ""), "llamadas": ex.llamadas,
        })
        print(f"  [{'✓' if ok else '✗'}] {p['id']:<8} nivel={p['nivel']:<8}"
              f"{' cat=' + (cat or '') if cat else ''}")

    tp = sum(f["peso"] for f in filas_salida)
    EX = sum(f["peso"] * f["acierto"] for f in filas_salida) / tp if tp else 0.0
    por_nivel = {}
    for nivel in PESOS:
        sub = [f for f in filas_salida if f["nivel"] == nivel]
        por_nivel[nivel] = (sum(f["acierto"] for f in sub) / len(sub)) if sub else 0.0

    resultado = {
        "EX_ponderada": round(EX, 4),
        "EX_simple": round(sum(f["acierto"] for f in filas_salida) / len(filas_salida), 4),
        "por_nivel": {k: round(v, 4) for k, v in por_nivel.items()},
        "errores_por_categoria": {c: errores_cat.get(c, 0) for c in CATEGORIAS},
        "config": {
            "nombre": nombre, "adapter": adapter, "sin_adapter": sin_adapter,
            "beams": beams or 1, "ejecutar": ejecutar, "formato": formato,
        },
        "n": len(filas_salida),
        "preguntas": filas_salida,
    }
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, f"eval_{nombre}.json"), "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    campos = list(filas_salida[0].keys())
    with open(os.path.join(RES, f"eval_{nombre}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas_salida)
    if csv_validacion:  # entregable exigido por el PDF
        shutil.copy(os.path.join(RES, f"eval_{nombre}.csv"),
                    os.path.join(RES, "validacion_propia.csv"))

    print(f"\n{nombre}: EX ponderada = {EX:.3f} · niveles "
          f"F {por_nivel['facil']:.2f} / M {por_nivel['media']:.2f} / D {por_nivel['dificil']:.2f} · "
          f"errores: {dict(errores_cat)}")
    return resultado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--adapter", default=None, help="ruta del adapter (p. ej. adapters/config_A)")
    ap.add_argument("--sin-adapter", action="store_true", help="usa el modelo base")
    ap.add_argument("--beams", type=int, default=1)
    ap.add_argument("--sin-ejecutar", action="store_true")
    ap.add_argument("--formato", choices=["compacto", "crudo"], default="compacto")
    ap.add_argument("--max-preguntas", type=int, default=None)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--socket", default=None)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    ap.add_argument("--csv-validacion", action="store_true", default=None,
                    help="copia el CSV final a resultados/validacion_propia.csv (por defecto si --nombre final)")
    a = ap.parse_args()
    mysql = {"host": a.host, "user": a.user, "password": a.password,
             **({"port": a.port} if a.socket else {}), **({"unix_socket": a.socket} if a.socket else {})}
    csv_validacion = a.csv_validacion if a.csv_validacion is not None else a.nombre == "final"
    evaluar(a.nombre, mysql, adapter=a.adapter, sin_adapter=a.sin_adapter,
            beams=a.beams, ejecutar=not a.sin_ejecutar, formato=a.formato,
            max_preguntas=a.max_preguntas, csv_validacion=csv_validacion)


if __name__ == "__main__":
    main()

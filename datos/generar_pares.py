"""
Generador de pares (pregunta en español, SQL MySQL) sobre los esquemas propios.

Las preguntas salen de plantillas parametrizadas (redactadas con ayuda de un LLM y
revisadas por nosotros) que usan los roles de cada columna del spec: nombre,
categoría, medida numérica, fecha, FK. Cada plantilla tiene varias redacciones para
que el modelo no se aprenda una sola forma de preguntar. Toda pregunta dice qué
columnas devolver, igual que en la evaluación oculta.

Niveles (los mismos del enunciado):
  facil   -> una tabla
  media   -> JOIN, GROUP BY, HAVING
  dificil -> subconsultas, WITH, ventanas, fechas
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from construir_esquemas import generar_datos, pk_de  # noqa: E402


# ------------------------------------------------------------------ utilidades de texto
def fix(s):
    for a, b in ((" todos las ", " todas las "), (" de el ", " del "), (" a el ", " al "), ("(de el ", "(del "), (" de El ", " del ")):
        s = s.replace(a, b)
    return s[0].upper() + s[1:]


def bare(lbl):
    return lbl.split(" ", 1)[1] if lbl.split(" ", 1)[0] in ("el", "la", "los", "las") else lbl


def num_bonito(v):
    if v >= 1000:
        return int(round(v, -2))
    if v >= 100:
        return int(round(v, -1))
    if v >= 10:
        return int(round(v))
    return round(v, 1)


def lit(v):
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


class Tabla:
    def __init__(self, spec, filas):
        self.s = spec
        self.name = spec["name"]
        self.sing = spec["sing"]
        self.plur = spec["plur"]
        self.filas = filas
        self.pk = pk_de(spec)
        self.cols = {c[0]: c for c in spec["cols"]}

    def rol(self, *roles):
        return [c[0] for c in self.s["cols"] if c[3] in roles]

    def lbl(self, col):
        return self.cols[col][4]

    @property
    def nombre(self):
        r = self.rol("name")
        return r[0] if r else None

    @property
    def sb(self):  # singular sin artículo
        return bare(self.sing)

    @property
    def pb(self):
        return bare(self.plur)

    def valores(self, col):
        return [f[col] for f in self.filas if f[col] is not None]

    def nullable(self):
        return [c[0] for c in self.s["cols"] if c[2].startswith("?")]


def alias(nombres):
    out, usados = {}, set()
    for n in nombres:
        partes = n.split("_")
        cand = "".join(p[0] for p in partes)
        k = 1
        while cand in usados:
            k += 1
            cand = n[:k] if len(partes) == 1 else "".join(p[:k] for p in partes)
        usados.add(cand)
        out[n] = cand
    return out


class Ctx:
    def __init__(self, esquema, rng):
        self.db = esquema["db"]
        datos = generar_datos(esquema)
        self.T = {t["name"]: Tabla(t, datos[t["name"]]) for t in esquema["tablas"]}
        self.rng = rng
        # relaciones hijo -> padre
        self.fks = []
        for t in self.T.values():
            for c in t.s["cols"]:
                if c[2].startswith("fk:"):
                    self.fks.append((t, c[0], self.T[c[2][3:]]))

    def cat_val(self, t, col):
        return self.rng.choice(sorted(set(t.valores(col)), key=str))

    def umbral(self, t, col, q=None):
        vals = sorted(t.valores(col))
        q = q if q is not None else self.rng.choice([0.5, 0.6, 0.7, 0.8])
        return num_bonito(vals[int(q * (len(vals) - 1))])

    def anio(self, t, col):
        anios = sorted({str(v)[:4] for v in t.valores(col)})
        return int(self.rng.choice(anios))


def pick(rng, *opciones):
    return rng.choice(opciones)


def es_fecha(t, c):
    return t.cols[c][1].startswith(("DATE", "DATETIME"))


# ================================================================== FÁCIL
def facil(ctx):
    r, out = ctx.rng, []
    for t in ctx.T.values():
        nm = t.nombre
        cats = t.rol("cat")
        nums = t.rol("num")
        fechas = [c for c in t.rol("date") if es_fecha(t, c)]
        disp = nm or t.pk

        q = pick(r, f"¿Cuántos registros hay en la tabla de {t.pb}? Devuelve el total.",
                 f"¿Cuál es la cantidad total de {t.pb}? Devuelve un solo número llamado total.",
                 f"Cuenta {t.plur} registrados. Devuelve el total.")
        out.append(("E_count", q, f"SELECT COUNT(*) AS total FROM {t.name}", False))

        for c in cats[:2]:
            v = ctx.cat_val(t, c)
            q = pick(r, f"Lista {t.lbl(disp)} de {t.plur} con {bare(t.lbl(c))} igual a '{v}'.",
                     f"¿Qué {t.pb} tienen {t.lbl(c)} '{v}'? Devuelve {t.lbl(disp)}.",
                     f"Muestra {t.lbl(disp)} de todos {t.plur} cuyo valor de {bare(t.lbl(c))} sea '{v}'.")
            out.append(("E_cat", q, f"SELECT {disp} FROM {t.name} WHERE {c} = {lit(v)}", False))

            q = pick(r, f"¿Cuántos {t.pb} tienen {t.lbl(c)} '{v}'? Devuelve el total.",
                     f"Cuenta {t.plur} con {bare(t.lbl(c))} '{v}'. Devuelve la cantidad.")
            out.append(("E_count_cat", q, f"SELECT COUNT(*) AS total FROM {t.name} WHERE {c} = {lit(v)}", False))

            q = pick(r, f"¿Qué valores distintos de {bare(t.lbl(c))} aparecen en {t.plur}? Devuelve {t.lbl(c)}.",
                     f"Lista sin repetir {t.lbl(c)} de {t.plur}.")
            out.append(("E_distinct", q, f"SELECT DISTINCT {c} FROM {t.name}", False))

            vals = sorted(set(t.valores(c)), key=str)
            if len(vals) >= 3:
                v1, v2 = r.sample(vals, 2)
                q = f"Muestra {t.lbl(disp)} y {t.lbl(c)} de {t.plur} con {bare(t.lbl(c))} '{v1}' o '{v2}'."
                out.append(("E_in", q, f"SELECT {disp}, {c} FROM {t.name} WHERE {c} IN ({lit(v1)}, {lit(v2)})", False))

        for c in nums[:2]:
            if c == disp:
                continue
            x = ctx.umbral(t, c)
            q = pick(r, f"Lista {t.lbl(disp)} y {t.lbl(c)} de {t.plur} con {bare(t.lbl(c))} mayor a {x}.",
                     f"¿Qué {t.pb} tienen {t.lbl(c)} por encima de {x}? Devuelve {t.lbl(disp)} y {t.lbl(c)}.")
            out.append(("E_num_gt", q, f"SELECT {disp}, {c} FROM {t.name} WHERE {c} > {x}", False))

            lo, hi = ctx.umbral(t, c, 0.3), ctx.umbral(t, c, 0.6)
            if lo < hi:
                q = f"Muestra {t.lbl(disp)} de {t.plur} cuyo valor de {bare(t.lbl(c))} esté entre {lo} y {hi} (inclusive)."
                out.append(("E_between", q, f"SELECT {disp} FROM {t.name} WHERE {c} BETWEEN {lo} AND {hi}", False))

            k = r.choice([3, 5, 10])
            q = pick(r, f"¿Cuáles son {t.plur} con los {k} valores más altos de {bare(t.lbl(c))}? Devuelve {t.lbl(disp)} y {t.lbl(c)}, de mayor a menor.",
                     f"Top {k} de {t.plur} por {bare(t.lbl(c))} (de mayor a menor). Devuelve {t.lbl(disp)} y {t.lbl(c)}.")
            out.append(("E_top", q, f"SELECT {disp}, {c} FROM {t.name} ORDER BY {c} DESC LIMIT {k}", True))

            q = f"Muestra {t.lbl(disp)} y {t.lbl(c)} de {t.plur} con los {k} valores más bajos de {bare(t.lbl(c))}, ordenados de menor a mayor."
            out.append(("E_bottom", q, f"SELECT {disp}, {c} FROM {t.name} ORDER BY {c} ASC LIMIT {k}", True))

            fn, palabra, al = r.choice([("AVG", "el promedio", "promedio"), ("MAX", "el valor máximo", "maximo"),
                                        ("MIN", "el valor mínimo", "minimo"), ("SUM", "la suma total", "suma")])
            q = pick(r, f"¿Cuál es {palabra} de {bare(t.lbl(c))} en {t.plur}? Devuelve {palabra}.",
                     f"Calcula {palabra} de {t.lbl(c)} considerando todos {t.plur}.")
            expr = f"ROUND({fn}({c}), 2)" if fn in ("AVG", "SUM") else f"{fn}({c})"
            out.append(("E_agg", q, f"SELECT {expr} AS {al} FROM {t.name}", False))

            if cats:
                cc = cats[0]
                v = ctx.cat_val(t, cc)
                x = ctx.umbral(t, c, 0.5)
                q = f"Lista {t.lbl(disp)} y {t.lbl(c)} de {t.plur} con {bare(t.lbl(cc))} '{v}' y {bare(t.lbl(c))} mayor o igual a {x}."
                out.append(("E_and", q, f"SELECT {disp}, {c} FROM {t.name} WHERE {cc} = {lit(v)} AND {c} >= {x}", False))

        for c in fechas[:1]:
            y = ctx.anio(t, c)
            q = pick(r, f"Lista {t.lbl(t.pk)} y {t.lbl(c)} de {t.plur} del año {y}.",
                     f"¿Qué {t.pb} tienen {t.lbl(c)} en {y}? Devuelve {t.lbl(t.pk)} y {t.lbl(c)}.")
            out.append(("E_year", q, f"SELECT {t.pk}, {c} FROM {t.name} WHERE YEAR({c}) = {y}", False))
            m = r.randint(1, 12)
            q = f"¿Cuántos {t.pb} tienen {t.lbl(c)} en el mes {m} del año {y}? Devuelve el total."
            out.append(("E_month", q, f"SELECT COUNT(*) AS total FROM {t.name} WHERE YEAR({c}) = {y} AND MONTH({c}) = {m}", False))
            q = f"Muestra {t.lbl(t.pk)} y {t.lbl(c)} de {t.plur} con {bare(t.lbl(c))} entre el {y}-01-01 y el {y}-03-31."
            cond = f"{c} BETWEEN '{y}-01-01' AND '{y}-03-31'" if t.cols[c][1] == "DATE" else f"DATE({c}) BETWEEN '{y}-01-01' AND '{y}-03-31'"
            out.append(("E_daterange", q, f"SELECT {t.pk}, {c} FROM {t.name} WHERE {cond}", False))

        if nm:
            letra = r.choice(sorted({str(v)[0] for v in t.valores(nm)}))
            q = pick(r, f"Lista {t.lbl(nm)} de {t.plur} que empiezan con la letra '{letra}'.",
                     f"¿Qué {t.pb} tienen un nombre que comienza con '{letra}'? Devuelve {t.lbl(nm)}.")
            out.append(("E_like", q, f"SELECT {nm} FROM {t.name} WHERE {nm} LIKE '{letra}%'", False))
            q = f"Lista {t.lbl(nm)} de todos {t.plur} en orden alfabético."
            out.append(("E_order", q, f"SELECT {nm} FROM {t.name} ORDER BY {nm} ASC", True))

        for c in t.nullable():
            q = pick(r, f"¿Qué {t.pb} no tienen {t.lbl(c)} registrado (valor nulo)? Devuelve {t.lbl(t.pk)}.",
                     f"Lista {t.lbl(t.pk)} de {t.plur} donde {bare(t.lbl(c))} es NULL.")
            out.append(("E_null", q, f"SELECT {t.pk} FROM {t.name} WHERE {c} IS NULL", False))
            q = f"¿Cuántos {t.pb} sí tienen {t.lbl(c)} registrado? Devuelve el total."
            out.append(("E_notnull", q, f"SELECT COUNT(*) AS total FROM {t.name} WHERE {c} IS NOT NULL", False))

        for c in t.rol("bool"):
            q = f"Lista {t.lbl(disp)} de {t.plur} que cumplen la condición: {t.lbl(c)} (valor 1)."
            out.append(("E_bool", q, f"SELECT {disp} FROM {t.name} WHERE {c} = 1", False))
    return [(p, fix(q), s, "facil", o) for (p, q, s, o) in out]


# ================================================================== MEDIA
def media(ctx):
    r, out = ctx.rng, []
    for t in ctx.T.values():
        for c in t.rol("cat")[:2]:
            q = pick(r, f"¿Cuántos {t.pb} hay por cada {bare(t.lbl(c))}? Devuelve {t.lbl(c)} y la cantidad.",
                     f"Cuenta {t.plur} agrupados por {bare(t.lbl(c))}. Devuelve {t.lbl(c)} y el conteo.")
            out.append(("M_group_count", q, f"SELECT {c}, COUNT(*) AS cantidad FROM {t.name} GROUP BY {c}", False))
            for n in t.rol("num")[:2]:
                fn, palabra, al = r.choice([("AVG", "el promedio", "promedio"), ("SUM", "la suma", "total"), ("MAX", "el máximo", "maximo")])
                q = f"Para cada {bare(t.lbl(c))}, calcula {palabra} de {bare(t.lbl(n))} de {t.plur}. Devuelve {t.lbl(c)} y {palabra}."
                expr = f"ROUND({fn}({n}), 2)" if fn != "MAX" else f"MAX({n})"
                out.append(("M_group_agg", q, f"SELECT {c}, {expr} AS {al} FROM {t.name} GROUP BY {c}", False))
                q = f"Muestra {t.lbl(c)} y la suma de {bare(t.lbl(n))} de {t.plur} por {bare(t.lbl(c))}, ordenado de mayor a menor suma."
                out.append(("M_group_order", q, f"SELECT {c}, ROUND(SUM({n}), 2) AS total FROM {t.name} GROUP BY {c} ORDER BY total DESC", True))
            conteos = {}
            for v in t.valores(c):
                conteos[v] = conteos.get(v, 0) + 1
            if len(conteos) >= 3:
                k = sorted(conteos.values())[len(conteos) // 2]
                q = pick(r, f"¿Qué valores de {bare(t.lbl(c))} tienen al menos {k} {t.pb}? Devuelve {t.lbl(c)} y la cantidad.",
                         f"Lista {t.lbl(c)} con {k} o más {t.pb} registrados, junto con la cantidad.")
                out.append(("M_having", q, f"SELECT {c}, COUNT(*) AS cantidad FROM {t.name} GROUP BY {c} HAVING COUNT(*) >= {k}", False))

    for (h, fk, p) in ctx.fks:
        A = alias([h.name, p.name])
        a, b = A[h.name], A[p.name]
        on = f"JOIN {p.name} {b} ON {a}.{fk} = {b}.{p.pk}"
        pdisp = p.nombre or p.pk
        hdisp = h.nombre or h.pk
        pfk_lbl = h.lbl(fk)  # p.ej. "el cliente"
        hn = h.rol("num")
        hc = h.rol("cat")

        if p.nombre:
            v = r.choice(sorted(set(p.valores(p.nombre)), key=str))
            extra = f", {a}.{hn[0]}" if hn and hn[0] != hdisp else ""
            ext_lbl = f" y {h.lbl(hn[0])}" if extra else ""
            q = pick(r, f"Lista {h.lbl(hdisp)}{ext_lbl} de {h.plur} cuyo {bare(pfk_lbl)} es '{v}'.",
                     f"Muestra {h.lbl(hdisp)}{ext_lbl} de {h.plur} que corresponden a {pfk_lbl} '{v}'.")
            out.append(("M_join_name", q, f"SELECT {a}.{hdisp}{extra} FROM {h.name} {a} {on} WHERE {b}.{p.nombre} = {lit(v)}", False))

        for pc in p.rol("cat")[:1]:
            v = ctx.cat_val(p, pc)
            q = f"Lista {h.lbl(hdisp)} de {h.plur} junto con {p.lbl(pdisp)}, solo para {p.plur} con {bare(p.lbl(pc))} '{v}'."
            pcol = f"{b}.{pdisp} AS {pdisp}_{p.name}" if pdisp == hdisp else f"{b}.{pdisp}"
            out.append(("M_join_filter", q, f"SELECT {a}.{hdisp}, {pcol} FROM {h.name} {a} {on} WHERE {b}.{pc} = {lit(v)}", False))
            for n in hn[:1]:
                q = f"Para cada {bare(p.lbl(pc))} de {p.plur}, calcula la suma de {bare(h.lbl(n))} de {h.plur}. Devuelve {p.lbl(pc)} y la suma."
                out.append(("M_join_group_cat", q, f"SELECT {b}.{pc}, ROUND(SUM({a}.{n}), 2) AS total FROM {h.name} {a} {on} GROUP BY {b}.{pc}", False))

        if p.nombre:
            q = pick(r, f"¿Cuántos {h.pb} tiene cada {p.sb}? Devuelve {p.lbl(p.nombre)} y la cantidad de {h.pb}.",
                     f"Cuenta {h.plur} por {p.sb}. Devuelve {p.lbl(p.nombre)} y el número de {h.pb}.")
            out.append(("M_join_count", q, f"SELECT {b}.{p.nombre}, COUNT(*) AS cantidad FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre}", False))

            q = f"Lista {p.lbl(p.nombre)} de todos {p.plur} y cuántos {h.pb} tiene cada uno, incluyendo los que tienen cero."
            out.append(("M_left_zero", q, f"SELECT {b}.{p.nombre}, COUNT({a}.{h.pk}) AS cantidad FROM {p.name} {b} LEFT JOIN {h.name} {a} ON {a}.{fk} = {b}.{p.pk} GROUP BY {b}.{p.pk}, {b}.{p.nombre}", False))

            cnt = {}
            for f in h.filas:
                cnt[f[fk]] = cnt.get(f[fk], 0) + 1
            if len(cnt) >= 4:
                k = sorted(cnt.values())[int(len(cnt) * 0.6)]
                q = pick(r, f"¿Qué {p.pb} tienen más de {k} {h.pb}? Devuelve {p.lbl(p.nombre)} y la cantidad.",
                         f"Lista {p.plur} con más de {k} {h.pb} registrados. Devuelve {p.lbl(p.nombre)} y el conteo.")
                out.append(("M_join_having_count", q, f"SELECT {b}.{p.nombre}, COUNT(*) AS cantidad FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre} HAVING COUNT(*) > {k}", False))

            for n in hn[:2]:
                fn, palabra, al = r.choice([("SUM", "la suma", "total"), ("AVG", "el promedio", "promedio"), ("MAX", "el máximo", "maximo")])
                expr = f"ROUND({fn}({a}.{n}), 2)" if fn != "MAX" else f"MAX({a}.{n})"
                q = pick(r, f"Para cada {p.sb}, calcula {palabra} de {bare(h.lbl(n))} de sus {h.pb}. Devuelve {p.lbl(p.nombre)} y {palabra}.",
                         f"Muestra {p.lbl(p.nombre)} y {palabra} de {h.lbl(n)} en {h.plur}, agrupado por {p.sb}.")
                out.append(("M_join_agg", q, f"SELECT {b}.{p.nombre}, {expr} AS {al} FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre}", False))

                sums = {}
                for f in h.filas:
                    if f[n] is not None:
                        sums[f[fk]] = sums.get(f[fk], 0) + f[n]
                if len(sums) >= 4:
                    x = num_bonito(sorted(sums.values())[int(len(sums) * 0.6)])
                    q = f"¿Qué {p.pb} acumulan una suma de {bare(h.lbl(n))} mayor a {x} en {h.plur}? Devuelve {p.lbl(p.nombre)} y la suma."
                    out.append(("M_join_having_sum", q, f"SELECT {b}.{p.nombre}, ROUND(SUM({a}.{n}), 2) AS total FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre} HAVING SUM({a}.{n}) > {x}", False))

                k = r.choice([3, 5])
                q = f"¿Cuáles son {p.plur} con las {k} sumas más altas de {bare(h.lbl(n))} en {h.plur}? Devuelve {p.lbl(p.nombre)} y la suma, de mayor a menor."
                out.append(("M_join_top", q, f"SELECT {b}.{p.nombre}, ROUND(SUM({a}.{n}), 2) AS total FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre} ORDER BY total DESC LIMIT {k}", True))

            for c in hc[:1]:
                v = ctx.cat_val(h, c)
                q = f"Para cada {p.sb}, ¿cuántos {h.pb} con {bare(h.lbl(c))} '{v}' tiene? Devuelve {p.lbl(p.nombre)} y la cantidad."
                out.append(("M_join_cat_count", q, f"SELECT {b}.{p.nombre}, COUNT(*) AS cantidad FROM {h.name} {a} {on} WHERE {a}.{c} = {lit(v)} GROUP BY {b}.{p.pk}, {b}.{p.nombre}", False))

            for d in [c for c in h.rol("date") if es_fecha(h, c)][:1]:
                y = ctx.anio(h, d)
                q = f"¿Cuántos {h.pb} del año {y} tiene cada {p.sb}? Devuelve {p.lbl(p.nombre)} y la cantidad."
                out.append(("M_join_year", q, f"SELECT {b}.{p.nombre}, COUNT(*) AS cantidad FROM {h.name} {a} {on} WHERE YEAR({a}.{d}) = {y} GROUP BY {b}.{p.pk}, {b}.{p.nombre}", False))

    # dos saltos: nieto -> hijo -> abuelo
    for (g, fk1, h) in ctx.fks:
        for (h2, fk2, p) in ctx.fks:
            if h2 is not h or not p.nombre or p is g:
                continue
            A = alias([g.name, h.name, p.name])
            a, b, c = A[g.name], A[h.name], A[p.name]
            joins = f"FROM {g.name} {a} JOIN {h.name} {b} ON {a}.{fk1} = {b}.{h.pk} JOIN {p.name} {c} ON {b}.{fk2} = {c}.{p.pk}"
            q = f"¿Cuántos {g.pb} hay por cada {p.sb} (pasando por {h.plur})? Devuelve {p.lbl(p.nombre)} y la cantidad."
            out.append(("M_two_hop", q, f"SELECT {c}.{p.nombre}, COUNT(*) AS cantidad {joins} GROUP BY {c}.{p.pk}, {c}.{p.nombre}", False))
            for n in g.rol("num")[:1]:
                q = f"Calcula la suma de {bare(g.lbl(n))} de {g.plur} para cada {p.sb}. Devuelve {p.lbl(p.nombre)} y la suma."
                out.append(("M_two_hop_sum", q, f"SELECT {c}.{p.nombre}, ROUND(SUM({a}.{n}), 2) AS total {joins} GROUP BY {c}.{p.pk}, {c}.{p.nombre}", False))
            if p.rol("cat"):
                pc = p.rol("cat")[0]
                v = ctx.cat_val(p, pc)
                q = f"Lista {g.lbl(g.pk)} de {g.plur} relacionados con {p.plur} de {bare(p.lbl(pc))} '{v}'."
                out.append(("M_two_hop_filter", q, f"SELECT {a}.{g.pk} {joins} WHERE {c}.{pc} = {lit(v)}", False))
    return [(pp, fix(q), s, "media", o) for (pp, q, s, o) in out]


# ================================================================== DIFÍCIL
def dificil(ctx):
    r, out = ctx.rng, []
    for t in ctx.T.values():
        disp = t.nombre or t.pk
        cats = t.rol("cat")
        for n in t.rol("num")[:2]:
            if n == disp:
                continue
            q = pick(r, f"¿Qué {t.pb} tienen {t.lbl(n)} mayor al promedio de todos {t.plur}? Devuelve {t.lbl(disp)} y {t.lbl(n)}.",
                     f"Lista {t.lbl(disp)} y {t.lbl(n)} de {t.plur} cuyo valor de {bare(t.lbl(n))} supera el promedio general.")
            out.append(("H_above_avg", q, f"SELECT {disp}, {n} FROM {t.name} WHERE {n} > (SELECT AVG({n}) FROM {t.name})", False))

            q = f"Muestra {t.lbl(disp)}, {t.lbl(n)} y su posición en un ranking de mayor a menor {bare(t.lbl(n))} (con empates usando RANK)."
            out.append(("H_rank", q, f"SELECT {disp}, {n}, RANK() OVER (ORDER BY {n} DESC) AS posicion FROM {t.name}", False))

            q = f"¿Cuál es el segundo valor más alto de {bare(t.lbl(n))} en {t.plur}? Devuelve ese valor."
            out.append(("H_second", q, f"SELECT MAX({n}) AS segundo FROM {t.name} WHERE {n} < (SELECT MAX({n}) FROM {t.name})", False))

            for c in cats[:1]:
                q = pick(r, f"Para cada {bare(t.lbl(c))}, ¿qué {t.sb} tiene el valor más alto de {bare(t.lbl(n))}? Devuelve {t.lbl(c)}, {t.lbl(disp)} y {t.lbl(n)}.",
                         f"Encuentra, dentro de cada {bare(t.lbl(c))}, {t.sing} con el valor máximo de {bare(t.lbl(n))}. Devuelve {t.lbl(c)}, {t.lbl(disp)} y {t.lbl(n)}.")
                out.append(("H_top_per_group", q,
                            f"WITH ranking AS (SELECT {c}, {disp}, {n}, RANK() OVER (PARTITION BY {c} ORDER BY {n} DESC) AS rk FROM {t.name}) "
                            f"SELECT {c}, {disp}, {n} FROM ranking WHERE rk = 1", False))

                q = f"Lista {t.lbl(disp)}, {t.lbl(c)} y {t.lbl(n)} de {t.plur} cuyo {bare(t.lbl(n))} es mayor al promedio de su mismo {bare(t.lbl(c))}."
                out.append(("H_corr_avg", q,
                            f"SELECT x.{disp}, x.{c}, x.{n} FROM {t.name} x WHERE x.{n} > (SELECT AVG(y.{n}) FROM {t.name} y WHERE y.{c} = x.{c})", False))
        for c in cats[:1]:
            q = pick(r, f"¿Qué porcentaje de {t.plur} corresponde a cada {bare(t.lbl(c))}? Devuelve {t.lbl(c)} y el porcentaje con 2 decimales.",
                     f"Calcula para cada {bare(t.lbl(c))} el porcentaje que representa sobre el total de {t.pb}. Devuelve {t.lbl(c)} y el porcentaje.")
            out.append(("H_pct", q, f"SELECT {c}, ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM {t.name}), 2) AS porcentaje FROM {t.name} GROUP BY {c}", False))

        for d in [c for c in t.rol("date") if es_fecha(t, c)][:1]:
            y = ctx.anio(t, d)
            q = pick(r, f"¿Cuántos {t.pb} hubo en cada mes del año {y}? Devuelve el mes (formato AAAA-MM) y la cantidad, ordenado por mes.",
                     f"Muestra, mes a mes durante {y}, la cantidad de {t.pb} según {t.lbl(d)}. Devuelve mes (AAAA-MM) y cantidad en orden cronológico.")
            out.append(("H_month_count", q, f"SELECT DATE_FORMAT({d}, '%Y-%m') AS mes, COUNT(*) AS cantidad FROM {t.name} WHERE YEAR({d}) = {y} GROUP BY DATE_FORMAT({d}, '%Y-%m') ORDER BY mes", True))
            q = f"¿Cuántos {t.pb} hay por año según {t.lbl(d)}? Devuelve el año y la cantidad."
            out.append(("H_year_count", q, f"SELECT YEAR({d}) AS anio, COUNT(*) AS cantidad FROM {t.name} GROUP BY YEAR({d})", False))
            ref = f"{y}-06-30"
            k = r.choice([30, 60, 90])
            q = f"¿Cuántos {t.pb} tienen {t.lbl(d)} dentro de los {k} días anteriores al {ref} (incluyendo ese día)? Devuelve el total."
            out.append(("H_datediff", q, f"SELECT COUNT(*) AS total FROM {t.name} WHERE DATEDIFF('{ref}', {d}) BETWEEN 0 AND {k}", False))
            for n in t.rol("num")[:1]:
                q = f"Para {y}, calcula la suma mensual de {bare(t.lbl(n))} de {t.plur} y el acumulado mes a mes. Devuelve mes (AAAA-MM), la suma del mes y el acumulado, en orden cronológico."
                out.append(("H_running", q,
                            f"WITH m AS (SELECT DATE_FORMAT({d}, '%Y-%m') AS mes, SUM({n}) AS total FROM {t.name} WHERE YEAR({d}) = {y} GROUP BY DATE_FORMAT({d}, '%Y-%m')) "
                            f"SELECT mes, ROUND(total, 2) AS total, ROUND(SUM(total) OVER (ORDER BY mes), 2) AS acumulado FROM m ORDER BY mes", True))
                q = f"Muestra para cada mes de {y} la suma de {bare(t.lbl(n))} de {t.plur} y la diferencia contra el mes anterior. Devuelve mes (AAAA-MM), total y diferencia, en orden cronológico."
                out.append(("H_lag", q,
                            f"WITH m AS (SELECT DATE_FORMAT({d}, '%Y-%m') AS mes, SUM({n}) AS total FROM {t.name} WHERE YEAR({d}) = {y} GROUP BY DATE_FORMAT({d}, '%Y-%m')) "
                            f"SELECT mes, ROUND(total, 2) AS total, ROUND(total - LAG(total) OVER (ORDER BY mes), 2) AS diferencia FROM m ORDER BY mes", True))

    for (h, fk, p) in ctx.fks:
        if not p.nombre:
            continue
        A = alias([h.name, p.name])
        a, b = A[h.name], A[p.name]
        on = f"JOIN {p.name} {b} ON {a}.{fk} = {b}.{p.pk}"
        hdisp = h.nombre or h.pk

        if len({f[fk] for f in h.filas}) < len(p.filas):
            q = pick(r, f"¿Qué {p.pb} no tienen ningún registro en {h.plur}? Devuelve {p.lbl(p.nombre)}.",
                     f"Lista {p.lbl(p.nombre)} de {p.plur} que no aparecen en {h.plur}.")
            sql = pick(r, f"SELECT {b}.{p.nombre} FROM {p.name} {b} WHERE NOT EXISTS (SELECT 1 FROM {h.name} {a} WHERE {a}.{fk} = {b}.{p.pk})",
                       f"SELECT {p.nombre} FROM {p.name} WHERE {p.pk} NOT IN (SELECT {fk} FROM {h.name})")
            out.append(("H_not_exists", q, sql, False))

        q = pick(r, f"¿Qué {p.sb} tiene la mayor cantidad de {h.pb}? Si hay empate, devuelve todos. Devuelve {p.lbl(p.nombre)} y la cantidad.",
                 f"Encuentra {p.plur} con el máximo número de {h.pb} (incluye empates). Devuelve {p.lbl(p.nombre)} y la cantidad.")
        out.append(("H_max_count", q,
                    f"WITH conteo AS (SELECT {b}.{p.nombre}, COUNT(*) AS cantidad FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre}) "
                    f"SELECT {p.nombre}, cantidad FROM conteo WHERE cantidad = (SELECT MAX(cantidad) FROM conteo)", False))

        for n in h.rol("num")[:1]:
            q = f"¿Qué {p.pb} tienen una suma de {bare(h.lbl(n))} en {h.plur} mayor al promedio de esas sumas? Devuelve {p.lbl(p.nombre)} y la suma."
            out.append(("H_cte_above", q,
                        f"WITH totales AS (SELECT {b}.{p.pk}, {b}.{p.nombre}, SUM({a}.{n}) AS total FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre}) "
                        f"SELECT {p.nombre}, ROUND(total, 2) AS total FROM totales WHERE total > (SELECT AVG(total) FROM totales)", False))

            q = f"¿Qué {p.pb} tienen un promedio de {bare(h.lbl(n))} en {h.plur} mayor al promedio general de {h.plur}? Devuelve {p.lbl(p.nombre)} y su promedio."
            out.append(("H_having_sub", q,
                        f"SELECT {b}.{p.nombre}, ROUND(AVG({a}.{n}), 2) AS promedio FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre} "
                        f"HAVING AVG({a}.{n}) > (SELECT AVG({n}) FROM {h.name})", False))

            if hdisp != n:
                pn = f"{p.nombre}_{p.name}" if p.nombre in (hdisp, n) else p.nombre
                q = f"Para cada {p.sb}, muestra {h.plur} con los 3 valores más altos de {bare(h.lbl(n))} (con DENSE_RANK). Devuelve {p.lbl(p.nombre)}, {h.lbl(hdisp)} y {h.lbl(n)}."
                out.append(("H_top3_per_parent", q,
                            f"WITH r AS (SELECT {b}.{p.nombre} AS {pn}, {a}.{hdisp}, {a}.{n}, DENSE_RANK() OVER (PARTITION BY {b}.{p.pk} ORDER BY {a}.{n} DESC) AS rk FROM {h.name} {a} {on}) "
                            f"SELECT {pn}, {hdisp}, {n} FROM r WHERE rk <= 3", False))

                q = f"Lista {h.lbl(hdisp)} y {h.lbl(n)} de {h.plur} que tienen el {bare(h.lbl(n))} máximo dentro de su {bare(h.lbl(fk))}."
                out.append(("H_corr_max", q,
                            f"SELECT x.{hdisp}, x.{n} FROM {h.name} x WHERE x.{n} = (SELECT MAX(y.{n}) FROM {h.name} y WHERE y.{fk} = x.{fk})", False))

            q = f"¿Qué porcentaje del total de {bare(h.lbl(n))} de {h.plur} aporta cada {p.sb}? Devuelve {p.lbl(p.nombre)} y el porcentaje."
            out.append(("H_pct_parent", q,
                        f"SELECT {b}.{p.nombre}, ROUND(100 * SUM({a}.{n}) / (SELECT SUM({n}) FROM {h.name}), 2) AS porcentaje FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre}", False))

            for d in [c for c in h.rol("date") if es_fecha(h, c)][:1]:
                anios = sorted({str(v)[:4] for v in h.valores(d)})
                if len(anios) >= 2:
                    y1, y2 = map(int, r.sample(anios, 2))
                    y1, y2 = min(y1, y2), max(y1, y2)
                    q = f"Para cada {p.sb}, compara la suma de {bare(h.lbl(n))} de {h.plur} en {y1} contra {y2}. Devuelve {p.lbl(p.nombre)}, el total de {y1} y el total de {y2}."
                    out.append(("H_year_compare", q,
                                f"SELECT {b}.{p.nombre}, ROUND(SUM(CASE WHEN YEAR({a}.{d}) = {y1} THEN {a}.{n} ELSE 0 END), 2) AS total_{y1}, "
                                f"ROUND(SUM(CASE WHEN YEAR({a}.{d}) = {y2} THEN {a}.{n} ELSE 0 END), 2) AS total_{y2} "
                                f"FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre}", False))

        for d in [c for c in h.rol("date") if es_fecha(h, c)][:1]:
            q = f"Para cada {p.sb}, ¿cuál es la fecha más reciente y la más antigua de {h.lbl(d)}? Devuelve {p.lbl(p.nombre)}, la más antigua y la más reciente."
            out.append(("H_minmax_date", q, f"SELECT {b}.{p.nombre}, MIN({a}.{d}) AS primera, MAX({a}.{d}) AS ultima FROM {h.name} {a} {on} GROUP BY {b}.{p.pk}, {b}.{p.nombre}", False))

        for c in h.rol("cat")[:1]:
            v = ctx.cat_val(h, c)
            q = f"Lista {p.lbl(p.nombre)} de {p.plur} que tienen al menos un registro en {h.plur} con {bare(h.lbl(c))} '{v}' (usa una subconsulta)."
            out.append(("H_in_sub", q, f"SELECT {p.nombre} FROM {p.name} WHERE {p.pk} IN (SELECT {fk} FROM {h.name} WHERE {c} = {lit(v)})", False))
    return [(pp, fix(q), s, "dificil", o) for (pp, q, s, o) in out]


def generar_todos(esquema, semilla=2026):
    rng = random.Random(f"pares-{semilla}-{esquema['db']}")
    ctx = Ctx(esquema, rng)
    pares = []
    for gen in (facil, media, dificil):
        for (patron, q, sql, nivel, ordenado) in gen(ctx):
            pares.append({"db": esquema["db"], "pregunta": q, "sql": sql, "nivel": nivel,
                          "patron": patron, "ordenado": ordenado})
    return pares


if __name__ == "__main__":
    from esquemas_spec import TRAIN
    total = 0
    for e in TRAIN:
        ps = generar_todos(e)
        total += len(ps)
        cuenta = {}
        for p in ps:
            cuenta[p["nivel"]] = cuenta.get(p["nivel"], 0) + 1
        print(e["db"], len(ps), cuenta)
    print("total", total)

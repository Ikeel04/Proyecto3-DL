"""
Genera presentacion.pdf (12 diapositivas) a partir de lo que haya en resultados/.
Si un resultado todavía no existe, la diapositiva lo marca como pendiente.

Uso:
    python src/generar_presentacion.py --autores "Adrián González" "José Ordóñez"
"""
import argparse
import json
import os
import random
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
AZUL, GRIS, ACENTO = "#1f3b57", "#5b6770", "#d9822b"
PESOS = {"facil": 1, "media": 2, "dificil": 3}


def leer(nombre):
    ruta = os.path.join(RES, nombre)
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    return None


def nueva(pdf, titulo):
    fig = plt.figure(figsize=(13.33, 7.5))
    fig.patch.set_facecolor("white")
    fig.text(0.05, 0.92, titulo, fontsize=26, weight="bold", color=AZUL)
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.895, 0.895], color=ACENTO, lw=2))
    return fig


def texto(fig, x, y, lineas, size=15, ancho=70, color="#222"):
    for l in lineas:
        for i, w in enumerate(textwrap.wrap(l, ancho) or [""]):
            fig.text(x + (0.02 if i else 0), y, ("• " if i == 0 and l and not l.startswith(" ") else "  ") + w,
                     fontsize=size, color=color, va="top")
            y -= 0.055 * size / 15
        y -= 0.012
    return y


def cerrar(pdf, fig, n):
    fig.text(0.95, 0.03, str(n), fontsize=11, color=GRIS, ha="right")
    pdf.savefig(fig)
    plt.close(fig)


def ex_bootstrap(csv_path, B=2000, semilla=2026):
    import csv
    with open(csv_path, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    rng = random.Random(semilla)
    vals = []
    for _ in range(B):
        m = [rng.choice(filas) for _ in filas]
        tp = sum(int(r["peso"]) for r in m)
        vals.append(sum(int(r["peso"]) * int(r["acierto"]) for r in m) / tp)
    vals.sort()
    return vals[int(0.05 * B)], vals[int(0.95 * B)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--autores", nargs="+", default=["Integrante 1", "Integrante 2"])
    ap.add_argument("--salida", default=os.path.join(RAIZ, "presentacion.pdf"))
    a = ap.parse_args()

    datos = leer("../datos/descartes/resumen_descartes.json") or {}
    tA, tB = leer("entrenamiento_A.json"), leer("entrenamiento_B.json")
    evals = {n: leer(f"eval_{n}.json") for n in
             ["base_greedy", "A_greedy", "B_greedy", "mejor_beam", "final", "base_final", "mejor_crudo"]}
    pred = leer("prediccion.json")

    def ex(n):
        e = evals.get(n)
        return e["EX_ponderada"] if e else None

    with PdfPages(a.salida) as pdf:
        n = 1
        # 1 portada
        fig = plt.figure(figsize=(13.33, 7.5))
        fig.text(0.07, 0.62, "Text-to-SQL en español", fontsize=40, weight="bold", color=AZUL)
        fig.text(0.07, 0.53, "Fine-tuning de Qwen2.5-Coder-1.5B-Instruct con LoRA para MySQL 8.4", fontsize=20, color=GRIS)
        fig.text(0.07, 0.40, " · ".join(a.autores), fontsize=18)
        fig.text(0.07, 0.34, "Deep Learning 2026 — Universidad del Valle de Guatemala — Proyecto 3", fontsize=14, color=GRIS)
        fig.add_artist(plt.Line2D([0.07, 0.6], [0.5, 0.5], color=ACENTO, lw=3))
        cerrar(pdf, fig, n); n += 1

        # 2 objetivo
        fig = nueva(pdf, "Qué hicimos")
        texto(fig, 0.06, 0.82, [
            "Objetivo: dado el esquema (SHOW CREATE TABLE con COMMENT) y una pregunta en español, generar una sola consulta SELECT/WITH correcta para MySQL 8.4 (ONLY_FULL_GROUP_BY).",
            "Modelo: Qwen/Qwen2.5-Coder-1.5B-Instruct + adapter LoRA propio. Sin APIs externas.",
            "Medida: exactitud por ejecución ponderada (fácil 1, media 2, difícil 3), igual que la evaluación oculta.",
            "Inferencia determinista (beam search sin muestreo, semilla 2026) y filtro que bloquea cualquier consulta que modifique la base.",
            "Opcional en evaluación: ejecutar() para elegir entre candidatos y corregir con el error de MySQL (máx. 3 llamadas).",
        ], ancho=95)
        cerrar(pdf, fig, n); n += 1

        # 3 dataset
        fig = nueva(pdf, "Dataset de entrenamiento")
        if datos:
            texto(fig, 0.06, 0.82, [
                "12 esquemas propios (5–6 tablas c/u) con nombres en español, inglés y abreviados; datos sintéticos deterministas.",
                f"{datos['aceptados']} pares pregunta–SQL aceptados, todos ejecutados sin error en MySQL 8.4.",
                f"Por nivel: fácil {datos['por_nivel'].get('facil', 0)}, media {datos['por_nivel'].get('media', 0)}, difícil {datos['por_nivel'].get('dificil', 0)}; {datos['patrones_distintos']} patrones de consulta.",
                "Más 360 ejemplos de reparación (consulta rota + error real de MySQL → consulta correcta).",
                f"Descartados: {datos['descartados']} (ver tabla). La mayoría son duplicados entre las dos pasadas del generador.",
            ], size=14, ancho=62)
            ax = fig.add_axes([0.62, 0.15, 0.33, 0.6])
            m = datos["descartes_por_motivo"]
            ax.barh(list(m.keys()), list(m.values()), color=ACENTO)
            ax.set_title("Descartes por motivo")
            for i, v in enumerate(m.values()):
                ax.text(v, i, f" {v}", va="center")
        else:
            texto(fig, 0.06, 0.8, ["(pendiente: correr notebooks/01_datos.ipynb)"])
        cerrar(pdf, fig, n); n += 1

        # 4 validación
        fig = nueva(pdf, "Validación propia (partición por esquema)")
        texto(fig, 0.06, 0.82, [
            "2 esquemas que NO aparecen en entrenamiento: biblioteca (6 tablas, nombres en español) y gym_mgmt (7 tablas, nombres abreviados en inglés).",
            "40 preguntas escritas por nosotros: 13 fáciles, 14 medias, 13 difíciles.",
            "Ninguna tabla de validación comparte nombre con tablas de entrenamiento (se verifica en el notebook de datos).",
            "Mismo criterio que el docente: orden solo si se pide, redondeo a 2 decimales, columnas extra no penalizan.",
        ], ancho=95)
        cerrar(pdf, fig, n); n += 1

        # 5 prompt
        fig = nueva(pdf, "Prompt y formato del esquema")
        texto(fig, 0.06, 0.82, [
            "System: rol de experto en MySQL 8.4 + reglas (solo lectura, ONLY_FULL_GROUP_BY, sin explicaciones).",
            "User: ### Esquema (compactado) → ### Pregunta → ### SQL. El mismo prompt con y sin adapter.",
            "Compactación: se quitan índices KEY, ENGINE/CHARSET/AUTO_INCREMENT y NOT NULL; se conservan tipos, COMMENT, PK y FK. Ahorra ~35% de tokens.",
            "Post-proceso: se extrae la primera sentencia SELECT/WITH y se rechaza todo lo que pueda modificar la base.",
        ], ancho=95)
        cerrar(pdf, fig, n); n += 1

        # 6 configuraciones
        fig = nueva(pdf, "Dos configuraciones de LoRA (un solo factor)")
        filas = [["", "Config A", "Config B"],
                 ["target_modules", "q,k,v,o", "q,k,v,o + gate,up,down"],
                 ["rank / alpha", "16 / 32", "16 / 32"]]
        filas.append(["parámetros entrenables", f"{tA['parametros_entrenables']:,}" if tA else "pend.",
                      f"{tB['parametros_entrenables']:,}" if tB else "pend."])
        filas.append(["tiempo (min, T4)", f"{tA['minutos_entrenamiento']}" if tA else "pend.",
                      f"{tB['minutos_entrenamiento']}" if tB else "pend."])
        filas.append(["eval loss final", f"{tA['eval_loss_final']:.3f}" if tA else "pend.",
                      f"{tB['eval_loss_final']:.3f}" if tB else "pend."])
        filas.append(["EX validación (greedy)", f"{ex('A_greedy'):.3f}" if ex('A_greedy') is not None else "pend.",
                      f"{ex('B_greedy'):.3f}" if ex('B_greedy') is not None else "pend."])
        ax = fig.add_axes([0.06, 0.38, 0.88, 0.45])
        ax.axis("off")
        tb = ax.table(cellText=filas, loc="center", cellLoc="center")
        tb.auto_set_font_size(False)
        tb.set_fontsize(14)
        tb.scale(1, 2.1)
        texto(fig, 0.06, 0.3, [
            "Hipótesis (escrita antes de entrenar): agregar el MLP multiplica por ~4 los parámetros entrenables y debería mejorar sobre todo las preguntas difíciles (subconsultas, ventanas), a cambio de más tiempo y más riesgo de sobreajuste a las plantillas.",
            "Fijo en ambas: 1 época (3,200 ejemplos), lr 2e-4 coseno, batch efectivo 16, dropout 0.05, máx. 2048 tokens, semilla 2026.",
        ], size=13, ancho=110)
        cerrar(pdf, fig, n); n += 1

        # 7 curvas
        fig = nueva(pdf, "Curvas de loss")
        for i, c in enumerate("AB"):
            ruta = os.path.join(RES, f"loss_{c}.png")
            ax = fig.add_axes([0.04 + 0.48 * i, 0.08, 0.45, 0.75])
            ax.axis("off")
            if os.path.exists(ruta):
                ax.imshow(mpimg.imread(ruta))
            else:
                ax.text(0.5, 0.5, f"loss_{c}.png pendiente", ha="center")
        cerrar(pdf, fig, n); n += 1

        # 8 resultados
        fig = nueva(pdf, "Resultados en validación propia (EX ponderada)")
        orden = [("base_greedy", "Base\n(sin adapter)"), ("A_greedy", "LoRA A"), ("B_greedy", "LoRA B"),
                 ("base_final", "Base +\nbeam+ejecutar"), ("final", "Entrega\n(adapter+beam+ejecutar)")]
        crudos = [ex(k) for k, _ in orden]
        vals = [v or 0 for v in crudos]
        ax = fig.add_axes([0.08, 0.15, 0.55, 0.65])
        ax.bar([l for _, l in orden], vals, color=[GRIS, AZUL, AZUL, GRIS, ACENTO])
        ax.set_ylim(0, 1)
        ax.axhline(0.7, ls="--", color="red", lw=1)
        ax.text(4.4, 0.71, "0.70", color="red")
        for i, v in enumerate(crudos):
            ax.text(i, (v or 0) + 0.02, f"{v:.2f}" if v is not None else "pend.", ha="center", fontsize=12)
        lineas = []
        for k, l in orden:
            e = evals.get(k)
            if e:
                pn = e["por_nivel"]
                lineas.append(f"{l.replace(chr(10), ' ')}: F {pn.get('facil', 0):.2f} / M {pn.get('media', 0):.2f} / D {pn.get('dificil', 0):.2f}")
        if ex("final") is not None and ex("base_final") is not None:
            lineas.append(f"Mejora del adapter (mismo pipeline): {ex('final') - ex('base_final'):+.3f}")
        texto(fig, 0.66, 0.8, lineas or ["(pendiente: notebooks/03_evaluacion.ipynb)"], size=12, ancho=42)
        cerrar(pdf, fig, n); n += 1

        # 9 experimento de inferencia
        fig = nueva(pdf, "Experimento de inferencia: usar ejecutar()")
        orden = [("mejor_crudo", "esquema crudo\ngreedy"), ("A_greedy" if (ex("A_greedy") or 0) >= (ex("B_greedy") or 0) else "B_greedy", "greedy"),
                 ("mejor_beam", "beam 4"), ("final", "beam 4 +\nejecutar + reparar")]
        crudos = [ex(k) for k, _ in orden]
        ax = fig.add_axes([0.08, 0.15, 0.5, 0.65])
        ax.bar([l for _, l in orden], [v or 0 for v in crudos], color=[GRIS, AZUL, AZUL, ACENTO])
        ax.set_ylim(0, 1)
        for i, v in enumerate(crudos):
            ax.text(i, (v or 0) + 0.02, f"{v:.2f}" if v is not None else "pend.", ha="center", fontsize=12)
        texto(fig, 0.62, 0.8, [
            "Hipótesis: la mayoría de fallos de un modelo pequeño son nombres de columna/tabla inventados o GROUP BY incompletos, que MySQL detecta. Con el error en el prompt el modelo puede corregir.",
            "Estrategia (≤3 llamadas): ejecutar el mejor candidato; si falla, reparar con el error; si corre sin filas, probar el siguiente candidato del beam.",
            "También probamos pasar el esquema crudo vs compactado.",
        ], size=12, ancho=48)
        cerrar(pdf, fig, n); n += 1

        # 10 errores
        fig = nueva(pdf, "Análisis de errores por categoría")
        cats = ["sintaxis", "columna_o_tabla_inexistente", "join", "agregacion", "filtro", "resultado_distinto"]
        ax = fig.add_axes([0.08, 0.2, 0.84, 0.6])
        ancho = 0.38
        for j, (k, l, col) in enumerate([("base_greedy", "base", GRIS), ("final", "entrega", ACENTO)]):
            e = evals.get(k)
            v = [(e or {}).get("errores_por_categoria", {}).get(c, 0) for c in cats]
            ax.bar([i + j * ancho for i in range(len(cats))], v, ancho, label=l, color=col)
        ax.set_xticks([i + ancho / 2 for i in range(len(cats))])
        ax.set_xticklabels([c.replace("_", "\n") for c in cats])
        ax.set_ylabel("preguntas falladas")
        ax.legend()
        cerrar(pdf, fig, n); n += 1

        # 11 predicción
        fig = nueva(pdf, "Predicción de EX en la evaluación oculta")
        if pred:
            texto(fig, 0.06, 0.82, [
                f"EX ponderada en validación propia (pipeline de entrega): {pred['ex_val']:.3f}; intervalo bootstrap 90%: [{pred['ic_bajo']:.2f}, {pred['ic_alto']:.2f}].",
                f"Predicción: EX ≈ {pred['prediccion']:.2f} (rango {pred['rango'][0]:.2f}–{pred['rango'][1]:.2f}).",
                *pred["razones"],
            ], size=14, ancho=95)
        else:
            texto(fig, 0.06, 0.8, ["(pendiente: se calcula al final de notebooks/03_evaluacion.ipynb)"])
        cerrar(pdf, fig, n); n += 1

        # 12 conclusiones
        fig = nueva(pdf, "Conclusiones y siguiente paso")
        texto(fig, 0.06, 0.82, [
            "El mayor aporte viene de que el modelo aprende el formato (solo SQL, MySQL, alias, ONLY_FULL_GROUP_BY) y a leer los COMMENT para mapear nombres abreviados.",
            "Ejecutar y reparar ataca los errores baratos (columnas inexistentes, sintaxis); los errores de lógica (filtro o resultado distinto) siguen siendo el límite.",
            "Riesgo principal: nuestras preguntas salen de plantillas; el estilo libre del docente puede bajar el resultado.",
            "Para el Proyecto Final: conservamos adapter, prompt, dataset y evaluador; siguiente paso es sumar preguntas de Spider/BIRD traducidas y más esquemas con 8–10 tablas.",
        ], ancho=95)
        cerrar(pdf, fig, n)
    print("presentación generada:", a.salida)


if __name__ == "__main__":
    main()

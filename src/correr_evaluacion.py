"""Corre una evaluación de la validación propia con una variante de inferencia.

Las variantes de referencia (nombres que exe generar_presentacion.py):
    base_greedy   modelo base, greedy, sin ejecutar
    A_greedy      adapter A, greedy, sin ejecutar
    B_greedy      adapter B, greedy, sin ejecutar
    mejor_beam    mejor adapter, beam 4, sin ejecutar
    mejor_crudo   mejor adapter, greedy, esquema crudo (sin compactar)
    base_final    modelo base + beam 4 + ejecutar/reparar
    final         adapter ganador + beam 4 + ejecutar/reparar  (→ validacion_propia.csv)

Uso:
    python src/correr_evaluacion.py --nombre A_greedy --adapter adapters/config_A --beams 1
    python src/correr_evaluacion.py --nombre final --adapter adapters/config_A --beams 4 --verbose
"""
import argparse

import os

import evaluador

RAIZ = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--sin-adapter", action="store_true")
    ap.add_argument("--beams", type=int, default=1)
    ap.add_argument("--sin-ejecutar", action="store_true")
    ap.add_argument("--formato", choices=["compacto", "crudo"], default="compacto")
    ap.add_argument("--max-preguntas", type=int, default=None, help="prueba rápida")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--socket", default=None)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    a = ap.parse_args()
    mysql = {"host": a.host, "user": a.user, "password": a.password,
             **({"port": a.port} if a.socket else {}), **({"unix_socket": a.socket} if a.socket else {})}
    evaluador.evaluar(a.nombre, mysql, adapter=a.adapter, sin_adapter=a.sin_adapter,
                      beams=a.beams, ejecutar=not a.sin_ejecutar, formato=a.formato,
                      max_preguntas=a.max_preguntas,
                      csv_validacion=a.nombre == "final")


if __name__ == "__main__":
    main()

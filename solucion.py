"""
Proyecto 3 - Text-to-SQL con LoRA (Deep Learning 2026, UVG)

Contrato:
    generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str

- Carga el modelo indicado en config.json (con o sin adapter LoRA) al importar el módulo.
- El prompt es el mismo con y sin adapter.
- Generación determinista (do_sample=False, beam search sin muestreo, semilla fija).
- Siempre devuelve UNA consulta SELECT o WITH ... SELECT. Si el modelo produce algo
  que modifica la base, se descarta.
- Si el evaluador entrega `ejecutar`, se usa como máximo 3 veces para elegir/corregir
  la consulta (experimento de inferencia del proyecto).
"""
import json
import os
import random
import re
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.environ.get("T2SQL_CONFIG", os.path.join(_DIR, "config.json"))

# ------------------------------------------------------------------ parámetros de inferencia
# (fijos para la entrega; las variables de entorno solo se usan en los experimentos)
NUM_BEAMS = int(os.environ.get("T2SQL_NUM_BEAMS", "4"))
USAR_EJECUTAR = os.environ.get("T2SQL_USAR_EJECUTAR", "1") == "1"
FORMATO_ESQUEMA = os.environ.get("T2SQL_FORMATO", "compacto")  # compacto | crudo
MAX_NUEVOS_TOKENS = 384
MAX_LLAMADAS = 3
PRESUPUESTO_SEG = 24  # dejamos margen sobre los 30 s por pregunta

SISTEMA = (
    "Eres un experto en bases de datos MySQL 8.4. Recibes el esquema de una base de datos "
    "(sentencias CREATE TABLE con comentarios que explican cada tabla y columna) y una pregunta "
    "en español. Responde únicamente con UNA consulta SQL de solo lectura (SELECT o WITH ... SELECT) "
    "válida para MySQL 8.4 con ONLY_FULL_GROUP_BY activado. Usa solo tablas y columnas que existan "
    "en el esquema, devuelve las columnas que pide la pregunta y no escribas explicaciones."
)

_RESERVADAS = {
    "rank", "order", "group", "key", "keys", "range", "row", "rows", "desc", "asc", "index", "table",
    "select", "where", "from", "limit", "match", "condition", "check", "column", "values", "value",
    "interval", "read", "lead", "lag", "window", "over", "partition", "function", "system", "groups",
    "cume_dist", "dense_rank", "percent_rank", "row_number", "ntile", "first_value", "last_value",
    "nth_value", "usage", "option", "to", "by", "in", "is", "on", "or", "and", "not", "all", "as",
    "user", "status", "date", "time", "year", "month", "day", "level", "type", "name", "comment",
}


# ------------------------------------------------------------------ prompt
def compactar_esquema(esquema: str) -> str:
    """Quita del SHOW CREATE TABLE lo que no ayuda a escribir SQL (índices, motor, charset,
    AUTO_INCREMENT, NOT NULL...) y deja columnas, tipos, COMMENT, PK y FK."""
    salida = []
    for linea in esquema.splitlines():
        l = linea.rstrip().rstrip(",")
        s = l.strip()
        if not s:
            salida.append("")
            continue
        su = s.upper()
        if su.startswith(("KEY ", "UNIQUE KEY", "INDEX ", "FULLTEXT", "SPATIAL")):
            continue
        if su.startswith("CONSTRAINT") and "FOREIGN KEY" in su:
            m = re.search(r"FOREIGN KEY \((.+?)\) REFERENCES (`?\w+`?) \((.+?)\)", s, re.I)
            if m:
                salida.append(f"  FOREIGN KEY ({m.group(1)}) REFERENCES {m.group(2)}({m.group(3)})")
            continue
        if s.startswith(")"):
            com = re.search(r"COMMENT='((?:[^']|'')*)'", s)
            salida.append(f") COMMENT='{com.group(1)}';" if com else ");")
            continue
        if su.startswith("CREATE TABLE"):
            salida.append(s)
            continue
        s = re.sub(r"\s+CHARACTER SET \w+", "", s)
        s = re.sub(r"\s+COLLATE \w+", "", s)
        s = re.sub(r"\s+NOT NULL", "", s)
        s = re.sub(r"\s+AUTO_INCREMENT", "", s)
        s = re.sub(r"\s+DEFAULT NULL", "", s)
        s = re.sub(r"\s+NULL(?= COMMENT|$)", "", s)
        salida.append("  " + s)
    texto = "\n".join(salida)

    # quitar backticks salvo en palabras reservadas
    def _bt(m):
        nombre = m.group(1)
        return m.group(0) if nombre.lower() in _RESERVADAS else nombre
    texto = re.sub(r"`(\w+)`", _bt, texto)
    # agregar comas entre definiciones (las quitamos arriba)
    lineas, res = texto.split("\n"), []
    for i, l in enumerate(lineas):
        sig = lineas[i + 1].strip() if i + 1 < len(lineas) else ""
        if l.startswith("  ") and sig and not sig.startswith(")"):
            l = l + ","
        res.append(l)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(res)).strip()


def formatear_esquema(esquema: str, formato: str = None) -> str:
    formato = formato or FORMATO_ESQUEMA
    return esquema.strip() if formato == "crudo" else compactar_esquema(esquema)


def construir_mensajes(esquema: str, pregunta: str, sql_previa: str = None, error: str = None,
                       formato: str = None):
    usuario = f"### Esquema\n{formatear_esquema(esquema, formato)}\n\n### Pregunta\n{pregunta.strip()}"
    if sql_previa is not None:
        usuario += (f"\n\n### Consulta anterior (incorrecta)\n{sql_previa}\n\n### Error de MySQL\n{error}\n\n"
                    "Corrige la consulta.")
    usuario += "\n\n### SQL"
    return [{"role": "system", "content": SISTEMA}, {"role": "user", "content": usuario}]


# ------------------------------------------------------------------ limpieza y seguridad
_PROHIBIDAS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|RENAME|GRANT|REVOKE|LOCK|UNLOCK|"
    r"CALL|HANDLER|LOAD_FILE|OUTFILE|DUMPFILE|SLEEP|BENCHMARK|COMMIT|ROLLBACK|KILL|SHUTDOWN|INTO)\b",
    re.I)


def extraer_sql(texto: str) -> str:
    t = texto.strip()
    bloque = re.search(r"```(?:sql|mysql)?\s*(.*?)```", t, re.S | re.I)
    if bloque:
        t = bloque.group(1)
    elif "```" in t:
        t = t.split("```", 1)[1]
        t = re.sub(r"^(sql|mysql)\s*", "", t, flags=re.I)
    m = re.search(r"\b(WITH|SELECT)\b", t, re.I)
    if not m:
        return ""
    t = t[m.start():]
    t = t.split(";")[0]
    # cortar texto explicativo que a veces aparece después de la consulta
    t = re.split(r"\n\s*\n(?=[A-ZÁÉÍÓÚa-záéíóú]+ )", t)[0]
    return re.sub(r"\s+", " ", t).strip()


def es_segura(sql: str) -> bool:
    if not sql or not re.match(r"^\s*(WITH|SELECT)\b", sql, re.I):
        return False
    sin_cadenas = re.sub(r"'(?:[^'\\]|\\.|'')*'|\"(?:[^\"\\]|\\.)*\"", "''", sql)
    return _PROHIBIDAS.search(sin_cadenas) is None


# ------------------------------------------------------------------ modelo
_MODELO = None
_TOKENIZER = None
_CFG = None


def _fijar_semilla(s):
    random.seed(s)
    torch.manual_seed(s)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(s)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def cargar(config_path: str = None, usar_adapter: bool = None, adapter: str = None):
    """Carga (o recarga) el modelo. Se llama automáticamente al importar."""
    global _MODELO, _TOKENIZER, _CFG
    if _MODELO is not None:  # liberar el modelo anterior al recargar (experimentos)
        import gc
        _MODELO = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    with open(config_path or _CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    if usar_adapter is not None:
        cfg["usar_adapter"] = usar_adapter
    if adapter is not None:
        cfg["adapter"] = adapter
    _fijar_semilla(int(cfg.get("semilla", 2026)))

    cuda = torch.cuda.is_available()
    dtype = torch.float16 if cuda else torch.float32
    tok = AutoTokenizer.from_pretrained(cfg["modelo_base"])
    modelo = AutoModelForCausalLM.from_pretrained(cfg["modelo_base"], dtype=dtype,
                                                  device_map="cuda" if cuda else None)
    if cfg.get("usar_adapter"):
        from peft import PeftModel
        ruta = cfg["adapter"]
        if not os.path.isabs(ruta):
            ruta = os.path.join(_DIR, ruta)
        modelo = PeftModel.from_pretrained(modelo, ruta)
        modelo = modelo.merge_and_unload()
    modelo.eval()
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    _MODELO, _TOKENIZER, _CFG = modelo, tok, cfg
    return cfg


def _plantilla(mensajes):
    kw = {}
    if "qwen3" in _CFG["modelo_base"].lower():
        kw["enable_thinking"] = False
    return _TOKENIZER.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True, **kw)


@torch.inference_mode()
def _generar(mensajes, num_beams=1, num_return=1):
    texto = _plantilla(mensajes)
    ids = _TOKENIZER(texto, return_tensors="pt").to(_MODELO.device)
    _fijar_semilla(int(_CFG.get("semilla", 2026)))
    salida = _MODELO.generate(
        **ids, max_new_tokens=MAX_NUEVOS_TOKENS, do_sample=False, num_beams=num_beams,
        num_return_sequences=num_return, early_stopping=num_beams > 1,
        pad_token_id=_TOKENIZER.pad_token_id, eos_token_id=_TOKENIZER.eos_token_id,
        temperature=None, top_p=None, top_k=None,
    )
    n = ids["input_ids"].shape[1]
    return [_TOKENIZER.decode(s[n:], skip_special_tokens=True) for s in salida]


def _candidatos(esquema, pregunta):
    k = max(1, NUM_BEAMS)
    crudos = _generar(construir_mensajes(esquema, pregunta), num_beams=k, num_return=k)
    vistos, cands = set(), []
    for c in crudos:
        sql = extraer_sql(c)
        if es_segura(sql) and sql not in vistos:
            vistos.add(sql)
            cands.append(sql)
    return cands


def _llamar(ejecutar, sql):
    try:
        r = ejecutar(sql)
        if not isinstance(r, dict):
            return {"ok": False, "error": "respuesta inválida", "filas": []}
        return r
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e), "filas": []}


def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    inicio = time.time()
    cands = _candidatos(esquema, pregunta)
    respaldo = cands[0] if cands else "SELECT 1"
    if ejecutar is None or not USAR_EJECUTAR or not cands:
        return respaldo

    llamadas, vacia_ok = 0, None
    probadas = set()

    def tiempo_ok():
        return time.time() - inicio < PRESUPUESTO_SEG

    actual = cands[0]
    while llamadas < MAX_LLAMADAS and actual:
        probadas.add(actual)
        r = _llamar(ejecutar, actual)
        llamadas += 1
        if r.get("ok"):
            if r.get("filas"):
                return actual
            vacia_ok = vacia_ok or actual  # corre pero sin filas: guardar y probar otra opción
            actual = next((c for c in cands if c not in probadas), None)
            continue
        # falló: primero intentamos reparar con el mensaje de error, luego otro candidato del beam
        siguiente = None
        if tiempo_ok() and llamadas < MAX_LLAMADAS:
            crudo = _generar(construir_mensajes(esquema, pregunta, actual, r.get("error", "")), num_beams=1)[0]
            rep = extraer_sql(crudo)
            if es_segura(rep) and rep not in probadas:
                siguiente = rep
        if siguiente is None:
            siguiente = next((c for c in cands if c not in probadas), None)
        actual = siguiente

    return vacia_ok or respaldo


if os.environ.get("T2SQL_SOLO_PROMPT") != "1":
    cargar()

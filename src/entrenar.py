"""Fine-tuning LoRA de Qwen2.5-Coder-1.5B-Instruct para text-to-SQL.

Configs A y B (difieren en UN solo factor: los target_modules; r, alpha, lr, épocas,
dropout y semilla son idénticos):
    A: atención        q_proj, k_proj, v_proj, o_proj
    B: atención + MLP  q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

Escribe:
    adapters/config_{A,B}/                        adapter entrenado (no se sube a git)
    resultados/entrenamiento_{A,B}.json           métricas + log_history (lo lee la presentación)
    resultados/loss_{A,B}.png                     curvas de loss

Uso:
    python src/entrenar.py --config A
    python src/entrenar.py --config B --epocas 1
"""
import argparse
import json
import os
import random
import time

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

CONFIGS = {
    "A": {"target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"]},
    "B": {"target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                             "gate_proj", "up_proj", "down_proj"]},
}
# idéntico en ambas (el factor único es target_modules)
FIJOS = {"r": 16, "lora_alpha": 32, "lora_dropout": 0.05, "lr": 2e-4, "epocas": 1,
         "batch": 1, "acumulacion_gradiente": 16, "max_len": 2048}


def fijar_semilla(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


def cargar_dataset(ruta, tokenizer, max_len):
    ejemplos = []
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            d = json.loads(linea)
            prompt = tokenizer.apply_chat_template(d["mensajes"][:-1], tokenize=False,
                                                   add_generation_prompt=True)
            respuesta = d["mensajes"][-1]["content"].strip() + "<|im_end|>\n"
            kpids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
            rids = tokenizer(respuesta, add_special_tokens=False)["input_ids"]
            ids = (kpids + rids)[:max_len]
            labels = ([-100] * len(kpids) + rids)[:max_len]
            ejemplos.append({"input_ids": ids, "labels": labels})
    return ejemplos


def collate(lote, pad_id):
    n = max(len(x["input_ids"]) for x in lote)
    batch = {"input_ids": [], "attention_mask": [], "labels": []}
    for x in lote:
        m = len(x["input_ids"])
        batch["input_ids"].append(x["input_ids"] + [pad_id] * (n - m))
        batch["labels"].append(x["labels"] + [-100] * (n - m))
        batch["attention_mask"].append([1] * m + [0] * (n - m))
    return {k: torch.tensor(v) for k, v in batch.items()}


def guardar_curva(log_history, png, titulo):
    tr_s, tr_l, ev_s, ev_l = [], [], [], []
    for h in log_history:
        if "loss" in h:
            tr_s.append(h["step"]); tr_l.append(h["loss"])
        if "eval_loss" in h:
            ev_s.append(h["step"]); ev_l.append(h["eval_loss"])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(tr_s, tr_l, label="train", color="#1f3b57")
    if ev_s:
        ax.plot(ev_s, ev_l, label="eval", color="#d9822b", marker="o")
    ax.set_xlabel("step"); ax.set_ylabel("loss"); ax.set_title(titulo)
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(png, dpi=110)
    plt.close(fig)


def entrenar_config(nombre, args):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model

    fijar_semilla(args.semilla)
    with open(os.path.join(RAIZ, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)

    tok = AutoTokenizer.from_pretrained(cfg["modelo_base"])
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    train = cargar_dataset(os.path.join(RAIZ, "datos", "entrenamiento", "dataset_chat.jsonl"),
                           tok, FIJOS["max_len"])
    evalset = cargar_dataset(os.path.join(RAIZ, "datos", "entrenamiento", "dataset_eval.jsonl"),
                             tok, FIJOS["max_len"])
    loader = DataLoader(train, batch_size=FIJOS["batch"], shuffle=True,
                        collate_fn=lambda b: collate(b, tok.pad_token_id),
                        num_workers=2, drop_last=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    modelo = AutoModelForCausalLM.from_pretrained(cfg["modelo_base"],
                                                  dtype=torch.float16 if device == "cuda" else torch.float32,
                                                  device_map=device)
    modelo.config.use_cache = False
    peft_cfg = LoraConfig(r=FIJOS["r"], lora_alpha=FIJOS["lora_alpha"],
                          lora_dropout=FIJOS["lora_dropout"],
                          bias="none", task_type="CAUSAL_LM",
                          target_modules=CONFIGS[nombre]["target_modules"])
    modelo = get_peft_model(modelo, peft_cfg)
    modelo.enable_input_require_grads()  # necesario con gradient_checkpointing
    modelo.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    modelo.print_trainable_parameters()

    entrenables = [p for _, p in modelo.named_parameters() if p.requires_grad]
    n_train = sum(p.numel() for p in entrenables)
    n_total = sum(p.numel() for _, p in modelo.named_parameters())
    pasos = len(loader) // FIJOS["acumulacion_gradiente"]
    # al estilo del planificador coseno con warmup 3%
    from transformers import get_cosine_schedule_with_warmup
    opt = torch.optim.AdamW(entrenables, lr=FIJOS["lr"], weight_decay=0.0)
    sched = get_cosine_schedule_with_warmup(opt, pasos * 0.03 + 1, pasos)

    print(f"\n=== Config {nombre}: {len(train)} ejemplos, {pasos} pasos de optimización ===\n")
    inicio = time.time()
    log_history, eval_log = [], []
    eval_loss_final = None
    paso = 0
    micro_pad = tok.pad_token_id
    for epoca in range(FIJOS["epocas"]):
        modelo.train()
        opt.zero_grad(set_to_none=True)
        for i, batch in enumerate(loader):
            batch = {k: v.to(device) for k, v in batch.items()}
            out = modelo(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"],
                         labels=batch["labels"])
            (out.loss / FIJOS["acumulacion_gradiente"]).backward()
            if (i + 1) % FIJOS["acumulacion_gradiente"] == 0:
                torch.nn.utils.clip_grad_norm_(entrenables, 1.0)
                opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
                paso += 1
                log_history.append({"step": paso, "loss": out.loss.item()})
                if paso % 10 == 0:
                    print(f"  paso {paso}/{pasos}  loss={out.loss.item():.4f}  lr={sched.get_last_lr()[0]:.2e}")
                if paso % args.cada_eval == 0:
                    eval_loss_final = probar_eval(modelo, evalset, collate, device, micro_pad)
                    eval_log.append({"step": paso, "eval_loss": eval_loss_final})
                    print(f"  [eval] paso {paso}  eval_loss={eval_loss_final:.4f}")
                    modelo.train()
                if args.max_min and (time.time() - inicio) / 60 > args.max_min:
                    print("  (se detiene por presupuesto de tiempo)")
                    break
            if args.max_min and (time.time() - inicio) / 60 > args.max_min:
                break
        if args.max_min and (time.time() - inicio) / 60 > args.max_min:
            break

    minutos = (time.time() - inicio) / 60
    modelo.save_pretrained(args.salida)
    tok.save_pretrained(args.salida)

    resumen = {
        "config": nombre, "target_modules": CONFIGS[nombre]["target_modules"],
        "fijos": FIJOS, "parametros_entrenables": n_train, "parametros_totales": n_total,
        "porcentaje_entrenable": 100 * n_train / n_total,
        "minutos_entrenamiento": round(minutos, 1), "eval_loss_final": eval_log[-1]["eval_loss"],
        "train_loss_final": log_history[-1]["loss"], "log_history": log_history,
        "eval_log": eval_log, "n_ejemplos": len(train), "n_eval": len(evalset),
        "salida": args.salida, "dispositivo": device,
    }
    os.makedirs(os.path.join(RAIZ, "resultados"), exist_ok=True)
    json_path = os.path.join(RAIZ, "resultados", f"entrenamiento_{nombre}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)
    guardar_curva(log_history, eval_log, os.path.join(RAIZ, "resultados", f"loss_{nombre}.png"),
                  f"Config {nombre} · {CONFIGS[nombre]['target_modules']}")
    print(f"\nAdapter guardado en {args.salida} · {minutos:.1f} min · resumen en {json_path}")


@torch.no_grad()
def probar_eval(modelo, evalset, collate, device, pad_id, lote=8):
    modelo.eval()
    total, n_tok = 0.0, 0
    for i in range(0, len(evalset), lote):
        batch = collate(evalset[i: i + lote], pad_id)
        batch = {k: v.to(device) for k, v in batch.items()}
        out = modelo(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"],
                     labels=batch["labels"])
        n_tok += (batch["labels"] != -100).sum().item()
        total += out.loss.item() * (batch["labels"] != -100).sum().item()
    return total / max(n_tok, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=sorted(CONFIGS), required=True)
    ap.add_argument("--salida", default=None, help="carpeta del adapter (adapters/config_<X>)")
    ap.add_argument("--semilla", type=int, default=2026)
    ap.add_argument("--cada-eval", type=int, default=5, help="eval loss cada N pasos de optimización")
    ap.add_argument("--max-min", type=float, default=0, help="presupuesto de tiempo en minutos (0 = sin límite)")
    a = ap.parse_args()
    if not a.salida:
        a.salida = os.path.join(RAIZ, "adapters", f"config_{a.config}")
    entrenar_config(a.config, a)


if __name__ == "__main__":
    main()

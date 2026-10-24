# Contribuciones

| Tarea | Responsable | Evidencia |
|---|---|---|
| **Área: datos** | Adrián González | |
| Definición de los 14 esquemas (12 train, 2 val) | Adrián | `datos/esquemas_spec.py` |
| Generación de datos sintéticos y carga en MySQL | Adrián | `datos/construir_esquemas.py`, `datos/esquemas/` |
| Plantillas de preguntas por nivel | Adrián | `datos/generar_pares.py` |
| Validación en MySQL y reporte de descartes | Adrián | `datos/validar_pares.py`, `datos/descartes/` |
| Ejemplos de reparación | Adrián | `datos/generar_reparaciones.py`, `datos/entrenamiento/reparaciones.jsonl` |
| Notebook de datos y script de MySQL para Colab | Adrián | `notebooks/01_datos.ipynb`, `scripts/instalar_mysql_colab.sh` |
| `solucion.py` (contrato, prompt, ejecutar + reparar) y `config.json` | Adrián | `solucion.py`, `config.json`, `requirements.txt` |
| **Área: entrenamiento** | José Ordóñez | |
| Formato de chat para entrenamiento | José | `src/datos_chat.py` |
| Script LoRA y configuraciones A/B con hipótesis | José | `src/entrenar.py`, `notebooks/02_entrenamiento.ipynb`, `resultados/hipotesis.md` |
| Entrenamiento en Colab T4, curvas de loss | José | `resultados/entrenamiento_*.json`, `resultados/loss_*.png` |
| **Área: validación y errores** | José Ordóñez | |
| Preguntas de validación propia (40) | José | `datos/validacion/validacion_propia.json` |
| Evaluador por ejecución y categorías de error | José | `src/evaluador.py`, `src/correr_evaluacion.py` |
| Baseline, experimento de inferencia y análisis de errores | José | `notebooks/03_evaluacion.ipynb`, `resultados/eval_*.csv` |
| Predicción justificada del EX | José | `src/prediccion.py`, `resultados/prediccion.json` |
| **Compartido** | | |
| Elección del adapter final | Ambos | `adapter/`, celda de selección en `03_evaluacion.ipynb` |
| Presentación | Ambos | `src/generar_presentacion.py`, `presentacion.pdf` |
| README, bitácora | Ambos | `README.md`, `BITACORA.md` |

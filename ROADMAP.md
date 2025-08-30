Aquí dejo **mi roadmap personal** para construir, paso a paso, un sistema de predicción de precios de acciones. Está escrito como plan propio para ejecutarlo en iteraciones cortas y con foco en el aprendizaje y la comparación honesta entre enfoques.

# Objetivo

Desarrollar, evaluar y comparar modelos que pronostiquen el **precio de cierre (o retorno) a 1 día** de acciones (empezando por AAPL), avanzando desde métodos simples hasta enfoques multimodales.

# Métricas y reglas del juego

* **Métricas principales**: MAE, RMSE, MAPE, **Directional Accuracy** (acierta la subida/bajada), **Calibración** (fiabilidad de probabilidades si aplico clasificación), y **retorno/Sharpe** de una estrategia trivial (ir largo si el retorno predicho > 0).
* **Validación**: siempre **TimeSeriesSplit / walk-forward**; cero fuga de datos.
* **Baselines** obligatorias\*\*:

  * "Naive" (mañana = hoy).
  * Media móvil corta.
    Si un modelo no mejora a estos, no avanzo.

---

# ✅ Etapa 0 — Preparación de datos y entorno **[COMPLETADA]**

**Estado**: ✅ **IMPLEMENTADA Y FUNCIONANDO** - Ver `phase0/` para implementación completa

**Qué se implementó**

* ✅ Definir universo inicial (AAPL) y horizonte (diario, últimos 5–10 años).
* ✅ Descargar datos (precio ajustado, volumen). Ajustar por splits/dividendos.
* ✅ Limpiar huecos, alinear calendarios, verificar zona horaria.
* ✅ Crear **retornos** (log/porcentuales) y una **serie objetivo** clara (precio o retorno t+1).
* ✅ Implementar **backtesting walk-forward** reutilizable (función/pipeline).
* ✅ Guardar un cuaderno de **experiment tracking** (resultados, hiperparámetros, métricas).

**Entregables logrados**

* ✅ Dataset limpio con features mínimas (1,258 días de AAPL 2020-2024).
* ✅ Baselines calculadas y registradas (naive: 47.0%, SMA5: 53.6%, SMA20: 49.2%).
* ✅ Sistema de walk-forward con 46 splits temporales.
* ✅ Framework de evaluación completo (MAE, RMSE, MAPE, Directional Accuracy).

**Resultados clave**

* **Mejor baseline**: SMA_5 con 53.6% de precisión direccional
* **Error de referencia**: Naive con 1.97 MAE
* **Validación robusta**: 46 splits sin fuga de datos
* **Framework listo**: Sistema completo para comparar modelos futuros

**Criterio para pasar de etapa**: ✅ **CUMPLIDO** - baselines reproducibles y backtest funcionando.

**Documentación**: Ver `phase0/README.md` y `phase0/RESULTS.md` para análisis completo.

---

# 🔄 Etapa 1 — Modelos estadísticos (ARIMA/SARIMA y Prophet) **[EN DESARROLLO]**

**Estado**: 🚧 **EN PROGRESO** - Desarrollo iniciado

**Qué se está implementando**

* 🔄 EDA de estacionalidad/tendencias; test ADF para estacionariedad.
* 🔄 Probar transformaciones (diferenciación, log-precios vs retornos).
* 🔄 Ajustar **ARIMA/SARIMA** (grid pequeño, criterios AIC/BIC).
* 🔄 Ajustar **Prophet** con componentes de tendencia y estacionalidad semanal/anual.
* 🔄 Backtest walk-forward con ventana rodante; recolectar métricas.

**Entregables esperados**

* Funciones para entrenar y pronosticar con ARIMA/SARIMA y Prophet.
* Tablas/gráficas comparando contra baselines de Etapa 0.
* Mejora sobre SMA_5 (53.6% directional accuracy).

**Criterio para pasar de etapa**: al menos **una mejora clara** sobre la baseline y lecciones sobre estacionalidad/transformaciones.

**Objetivo de mejora**: Directional Accuracy > 60% (vs 53.6% de SMA_5).

---

# Etapa 2 — ML clásico (árboles y boosting)

**Qué haré**

* **Ingeniería de features**:

  * Lags del precio/retorno (p.ej., 1, 3, 5, 10, 20).
  * Ventanas móviles (SMA/EMA, volatilidad rolling, z-scores).
  * Indicadores técnicos: RSI, MACD, Bollinger.
  * Calendario (día de semana, fin/ini de mes, etc.).
* Etiqueta: retorno t+1 (regresión) o **signo del retorno** (clasificación binaria, si pruebo clasificación).
* Modelos: **RandomForest**, **XGBoost** o **LightGBM**.
  Cuidado con: escalado (si procede), **no mezclar train/test** al calcular features rolling.
* Importancia de variables (SHAP/ganancias), selección de features simple.
* Backtest walk-forward consistente con la Etapa 1.

**Entregables**

* Pipeline de features + modelo (sklearn API).
* Informe de métricas vs. Etapa 1 y baselines.
* Lista de features que realmente aportan.

**Criterio para pasar de etapa**: mejora **estable** en directional accuracy y/o error; overfitting controlado; proceso replicable.

---

# Etapa 3 — Deep Learning para series temporales

**Qué haré**

* Replantear el dataset como **secuencias**: ventanas de entrada de 30–120 días → predicción a 1 día (seq-to-one) y, si procede, multi-horizonte (seq-to-seq).
* Modelos:

  * **LSTM/GRU** (baseline DL).
  * **CNN 1D** para capturar patrones locales.
  * Opcional: **Temporal Fusion Transformer (TFT)** o similares para covariables.
* Regularización (dropout, weight decay), early stopping y normalización por ventana.
* Incluir como **covariables** las features útiles de la Etapa 2 (indicadores, calendario).
* Backtest walk-forward con reentrenos periódicos (mismo protocolo que etapas anteriores).

**Entregables**

* Scripts/funciones de data loader (ventanas), modelos LSTM/GRU, entrenamiento y predicción.
* Comparativa clara: DL vs boosting vs estadísticos.

**Criterio para pasar de etapa**: DL iguala o supera a boosting **sin degradar estabilidad**; evidencias de que captura dependencias temporales más largas.

---

# Etapa 4 — Enfoque híbrido / Multimodal

**Qué haré**

* **Fuentes externas**: noticias, sentiment diario, eventos corporativos (earnings), y/o macro (tipos, VIX).
  Normalizar a **frecuencia diaria** y alinear con el cierre.
* Generar **embeddings** de texto y/o un **índice de sentimiento** por día.
* Estrategias de fusión:

  * **Late fusion**: concatenar features tabulares + embeddings/sentiment y entrenar un booster o una red.
  * **Modelos con atención** (p.ej., TFT) que integren covariables estáticas/dinámicas.
* Evaluar el aporte marginal de cada fuente (ablation study).

**Entregables**

* Pipeline de ingestión → agregación diaria → features externas integradas.
* Informe de impacto de datos alternativos y riesgos (lag, calidad, cobertura).

**Criterio de cierre del roadmap**: mejora consistente y explicable frente a Etapa 3; justificación de complejidad vs. beneficio.

---

# Producción, monitoreo y control de riesgo (transversal)

**Qué haré**

* Versionado de datos/modelos, seeds fijas, informes automáticos.
* Monitoreo de **drift** (datos y rendimiento) y reentrenos programados.
* Estrategia de **riesgo**: tamaño de posición, límites de pérdida, costos de transacción en backtests.
* Registro de **incidencias** y checklist de "no leakage".

---

# Checklists rápidos

**Anti-fuga de datos**

* Features rolling calculadas **solo con pasado**.
* Escalado/normalización ajustado en train y aplicado a test.
* Selección de hiperparámetros hecha **dentro** del walk-forward.

**Comparación justa**

* Misma ventana temporal de evaluación para todos los modelos.
* Reportar baselines junto a cada resultado.
* Guardar seeds, versiones de librerías y commit hash.

**Cuándo no complicarme más**

* Si el modelo más complejo **no supera** a uno simple de forma robusta.
* Si la mejora desaparece al incluir costos de transacción.
* Si la estabilidad entre folds es pobre.

---

# Notas de expectativas

* Los mercados son ruidosos; buscar **robustez**, no récords puntuales.
* Lo importante es el **proceso reproducible** y las comparaciones honestas.
* Añadir datos externos ayuda, pero trae sesgos y lags: medir su **valor marginal**.

---

# 🎯 Próximos pasos inmediatos

1. ✅ **Etapa 0 completada** - Sistema de baselines funcionando.
2. 🔄 **Implementar Etapa 1** - ARIMA/SARIMA y Prophet.
3. **Decidir objetivo principal** (regresión de retorno vs clasificación de dirección) antes de Etapa 2.

---

# 📊 Estado del Proyecto

| **Etapa** | **Estado** | **Progreso** | **Fecha** |
|-----------|------------|---------------|-----------|
| **Etapa 0** | ✅ **COMPLETADA** | 100% | 30 Ago 2025 |
| **Etapa 1** | 🚧 **EN DESARROLLO** | 0% | En progreso |
| **Etapa 2** | ⏳ **PENDIENTE** | 0% | - |
| **Etapa 3** | ⏳ **PENDIENTE** | 0% | - |
| **Etapa 4** | ⏳ **PENDIENTE** | 0% | - |

---

# 📁 Estructura del Proyecto

```
Trading/
├── phase0/                    # ✅ COMPLETADA
│   ├── README.md             # Documentación completa
│   ├── RESULTS.md            # Análisis detallado de resultados
│   ├── main.py               # Script principal
│   ├── data_preparation.py   # Pipeline de datos
│   ├── backtesting.py        # Framework de backtesting
│   ├── utils.py              # Utilidades
│   └── results/              # Resultados generados
├── ROADMAP.md                # Este archivo
└── [Fases futuras...]
```

---

Este plan me sirve como guía viva: actualizaré decisiones y resultados en cada etapa antes de subir la siguiente marcha.
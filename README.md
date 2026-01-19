# InsurTech Ecosystem Analyzer - AI-Powered Classification

Sistema de clasificación de empresas InsurTech basado en el framework académico de **Iván Sosa Gómez (2024)** con análisis experto mediante IA.

## 🚀 Quick Start

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar OpenAI API Key

Crea un archivo `.env` en el directorio del proyecto:

```bash
cp .env.example .env
```

Edita `.env` y añade tu API key de OpenAI:

```
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXX
```

### 3. Ejecutar la Aplicación Web

```bash
streamlit run app.py
```

O para el script CLI:

```bash
python classify_insurtech.py
```

## 📊 Modos de Clasificación

### Modo Keywords (Legacy)
- Clasificación rápida basada en palabras clave
- Sin costos de API
- Ideal para datasets grandes cuando el presupuesto es limitado

### Modo AI Expert (Recomendado)
- Análisis profundo usando GPT-4o-mini o GPT-4o
- Implementa completamente el framework Sosa:
  - **7 Arquetipos**: Innovators, Disruptors, Enablers, Connectors, Protectors, Integrators, Transformers
  - **5 Driving Capabilities (DCs)**: DC1-DC5
  - **3 Innovation Waves**: 1.0, 2.0, 3.0
  - Justificaciones académicas detalladas

## 💰 Estimación de Costos (AI Mode)

Con **gpt-4o-mini** (recomendado):
- ~$0.15 USD por cada 100 empresas
- ~$1.50 USD por cada 1000 empresas

Con **gpt-4o** (calidad superior):
- ~$2.50 USD por cada 100 empresas
- ~$25.00 USD por cada 1000 empresas

## 📁 Estructura de Archivos

```
INSURTECH/
├── app.py                    # Streamlit web app
├── classify_insurtech.py     # Script CLI
├── openai_classifier.py      # Módulo de integración OpenAI
├── config.py                 # Configuración y prompts
├── requirements.txt          # Dependencias
├── .env                      # API keys (no incluir en git!)
├── .env.example              # Template para .env
└── .streamlit/
    └── config.toml           # Tema de la app
```

## 🎯 Features

- **Análisis Temporal**: Detección automática de empresas "falsas disruptoras" por antigüedad
- **Multi-columna**: Analiza automáticamente Description + Industries + Industry Groups
- **Exportación**: Descarga resultados en CSV o Excel
- **Visualizaciones**:
  - Distribución de arquetipos
  - Heatmap de Driving Capabilities
  - Timeline de Innovation Waves
  - Scatter plot temporal

## 🔧 Troubleshooting

**Error: "No module named 'openai'"**
```bash
pip install openai python-dotenv tenacity
```

**Error: "API key not configured"**
- Verifica que `.env` existe y contiene `OPENAI_API_KEY=...`
- Reinicia la aplicación después de crear/editar `.env`

**Costos muy altos**
- Usa `gpt-4o-mini` en lugar de `gpt-4o`
- Filtra tu dataset antes de analizar
- Usa Keyword Mode para pre-filtrar y AI Mode solo para casos ambiguos

## 📚 Referencias

Sosa Gómez, I. (2024). *Tesis Doctoral - Framework InsurTech*. Universidad [TBD].

---

**Desarrollado con ❤️ usando Streamlit + OpenAI**

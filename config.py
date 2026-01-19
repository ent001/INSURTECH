"""
Configuration file for InsurTech Analyzer - OPTIMIZED
Contains OpenAI settings and the Sosa & Sosa 2025 framework context
"""

import os
import streamlit as st

# OpenAI API Configuration - Load from environment or Streamlit secrets
def get_api_key():
    """Get API key from environment variable or Streamlit secrets"""
    # Try environment variable first (local development)
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Fall back to Streamlit secrets (Streamlit Cloud deployment)
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            pass
    
    return api_key

OPENAI_API_KEY = get_api_key()
OPENAI_MODEL = "gpt-4o-mini"  # Most cost-efficient model
TEMPERATURE = 0.0  # Deterministic, consistent classifications
MAX_TOKENS = 800
REQUEST_TIMEOUT = 30  # seconds
RATE_LIMIT_DELAY = 0.5  # seconds between API calls
CHECKPOINT_FREQUENCY = 5  # Save progress every N companies

# Sosa Framework Context (Iván Sosa Gómez, 2024) - CONCISE VERSION
SOSA_FRAMEWORK_CONTEXT = """
TESIS IVÁN SOSA GÓMEZ (2024) - MARCO INSURTECH

ARQUETIPOS (7):
1. Innovators: Nuevos modelos (P2P, on-demand, paramétrico, microseguros)
2. Disruptors: Eficiencia extrema vía automatización/AI (full-stack carriers)
3. Enablers: Infraestructura tech B2B (SaaS, APIs, plataformas)
4. Connectors: Marketplaces, comparadores, brokers digitales
5. Protectors: Prevención proactiva (IoT, telemática, cyber)
6. Integrators: Embedded insurance (API-first, B2B2C)
7. Transformers: Consultoría de digitalización para legacy

DRIVING CAPABILITIES (5):
DC1: Infraestructura digital (IaaS, SaaS, cloud, APIs)
DC2: Datos & Analytics (AI, ML, Big Data, actuarial)
DC3: Experiencia Cliente (chatbots, omnicanal, UX/UI)
DC4: Diseño de Producto (on-demand, paramétrico, personalización)
DC5: Distribución Digital (venta 100% online, autoservicio)

OLAS DE INNOVACIÓN (3):
1.0 (2010-2015): Startups disruptivas, P2P, desintermediación
2.0 (2015-2020): Habilitadores B2B, APIs, colaboración
3.0 (2020-presente): Ecosistemas, embedded, open insurance
"""

# Classification prompt template - OPTIMIZED
CLASSIFICATION_PROMPT_TEMPLATE = """
{framework_context}

EMPRESA:
Nombre: {company_name}
Descripción: {description}
Industrias: {industries}

ANÁLISIS REQUERIDO:
Clasifica usando el marco Sosa. Devuelve SOLO JSON:

{{
  "archetype": "Nombre exacto del arquetipo",
  "secondary_archetypes": ["Otro1", "Otro2"] o [],
  "driving_capabilities": ["DC1", "DC2"],
  "innovation_wave": "1.0" | "2.0" | "3.0",
  "justification": "Max 150 caracteres",
  "confidence": "High" | "Medium" | "Low"
}}
"""

# Pricing (USD per 1M tokens) - gpt-4o-mini
PRICING_INPUT = 0.15
PRICING_OUTPUT = 0.60

"""
OpenAI Integration Module - OPTIMIZED & ROBUST
Features: Rate limiting, error recovery, checkpoint support
"""

import json
import time
from typing import Dict, Optional, Tuple
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config

# Global client variable
_client = None

def get_client():
    """Lazy initialization of OpenAI client"""
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception,))
)
def classify_with_openai(
    company_name: str,
    description: str,
    industries: str = "",
    model: str = None
) -> Tuple[str, str, str, list, str, str]:
    """
    Classify a company using OpenAI API based on Sosa framework.
    
    Returns:
        Tuple of (archetype, confidence, justification, secondary_archetypes, dcs, wave)
    """
    model = model or config.OPENAI_MODEL
    
    print(f"🔄 Classifying: {company_name[:50]}...")
    
    # Rate limiting
    time.sleep(config.RATE_LIMIT_DELAY)
    
    # Construct the prompt
    prompt = config.CLASSIFICATION_PROMPT_TEMPLATE.format(
        framework_context=config.SOSA_FRAMEWORK_CONTEXT,
        company_name=company_name,
        description=description[:500],  # Limit to avoid token overflow
        industries=industries
    )
    
    try:
        print(f"📡 Calling OpenAI API for {company_name[:30]}...")
        
        # Get client
        client = get_client()
        
        # Call OpenAI API with JSON mode
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Experto InsurTech. Framework Sosa 2025. Responde SOLO JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        print(f"✅ Got response for {company_name[:30]}")
        
        # Parse response
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        # Extract fields with defaults
        archetype = result.get('archetype', 'Unclassified')
        secondary_archetypes = result.get('secondary_archetypes', [])
        dcs = result.get('driving_capabilities', [])
        wave = result.get('innovation_wave', '')
        justification = result.get('justification', '')
        confidence = result.get('confidence', 'Medium')
        
        print(f"✅ Classified {company_name[:30]} as {archetype}")
        
        # Format justification for display
        keywords_display = justification[:200] + "..." if len(justification) > 200 else justification
        
        return (
            archetype,
            confidence,
            keywords_display,
            secondary_archetypes,
            dcs,
            wave
        )
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing error for {company_name}: {e}")
        return ("API Error - JSON", "Low", f"JSON parse error", [], "", "")
    
    except Exception as e:
        print(f"❌ API error for {company_name}: {type(e).__name__}: {str(e)[:150]}")
        import traceback
        traceback.print_exc()
        return ("API Error", "Low", f"Error: {str(e)[:80]}", [], "", "")


def get_token_estimate(text: str) -> int:
    """Rough estimate of tokens. 1 token ≈ 4 characters"""
    return len(text) // 4


def estimate_cost(num_companies: int, model: str = None) -> Dict[str, float]:
    """
    Estimate cost for analyzing a dataset.
    
    Returns:
        Dict with 'input_tokens', 'output_tokens', 'total_cost_usd'
    """
    model = model or config.OPENAI_MODEL
    
    # Estimates based on actual prompt structure
    avg_input_tokens = get_token_estimate(config.SOSA_FRAMEWORK_CONTEXT) + 200
    avg_output_tokens = 250
    
    total_input = num_companies * avg_input_tokens
    total_output = num_companies * avg_output_tokens
    
    # Calculate cost using config pricing
    input_cost = (total_input / 1_000_000) * config.PRICING_INPUT
    output_cost = (total_output / 1_000_000) * config.PRICING_OUTPUT
    
    return {
        'input_tokens': total_input,
        'output_tokens': total_output,
        'total_cost_usd': input_cost + output_cost
    }


def calculate_actual_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate actual cost from token usage"""
    input_cost = (input_tokens / 1_000_000) * config.PRICING_INPUT
    output_cost = (output_tokens / 1_000_000) * config.PRICING_OUTPUT
    return input_cost + output_cost

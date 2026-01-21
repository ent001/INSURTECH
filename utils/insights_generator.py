"""
Insights Generator - Auto-generate key findings from classification results
"""

import pandas as pd
from typing import Dict, List


def generate_insights(df: pd.DataFrame) -> Dict[str, str]:
    """
    Generate key insights from classification results
    
    Args:
        df: DataFrame with classification results
        
    Returns:
        Dictionary with insight categories and findings
    """
    insights = {}
    
    # Total companies
    total = len(df)
    
    # Success rate (non-errors)
    error_count = df['Predicted_Archetype'].str.contains('Error', na=False).sum()
    success_rate = ((total - error_count) / total * 100) if total > 0 else 0
    
    # Dominant archetype
    if 'Predicted_Archetype' in df.columns:
        archetypes = df[~df['Predicted_Archetype'].str.contains('Error', na=False)]['Predicted_Archetype']
        if len(archetypes) > 0:
            top = archetypes.value_counts().iloc[0]
            top_name = archetypes.value_counts().index[0]
            top_count = int(top)
            insights['dominant_archetype'] = f"**{top_name}** is the dominant archetype with {top_count} companies ({top_count/len(archetypes)*100:.1f}%)"
    
    # Innovation waves distribution
    if 'Innovation_Wave' in df.columns:
        waves = df[df['Innovation_Wave'].notna() & ~df['Innovation_Wave'].str.contains('', na=False)]
        if len(waves) > 0:
            wave_3_count = (waves['Innovation_Wave'] == '3.0').sum()
            wave_2_count = (waves['Innovation_Wave'] == '2.0').sum()
            wave_1_count = (waves['Innovation_Wave'] == '1.0').sum()
            
            if wave_3_count > 0:
                insights['innovation_maturity'] = f"**{wave_3_count/len(waves)*100:.1f}%** of companies are in Wave 3.0, indicating a highly evolved ecosystem with embedded insurance and open platforms"
            elif wave_2_count > 0:
                insights['innovation_maturity'] = f"**{wave_2_count/len(waves)*100:.1f}%** in Wave 2.0, showing strong B2B enabler presence"
    
    # Driving capabilities analysis
    dc_columns = [col for col in df.columns if col.startswith('DC')]
    if dc_columns:
        dc_counts = df[dc_columns].apply(lambda x: x.str.contains('DC', na=False).sum())
        if dc_counts.sum() > 0:
            top_dc = dc_counts.idxmax()
            insights['top_capability'] = f"**{top_dc}** is the most prevalent driving capability across the ecosystem"
            
            # Average capabilities per company
            avg_dcs = df[dc_columns].apply(lambda x: x.str.count('DC').sum(), axis=1).mean()
            insights['capability_density'] = f"Companies leverage an average of **{avg_dcs:.1f} capabilities**, showing {'high' if avg_dcs >= 3 else 'moderate'} technological sophistication"
    
    # Quality metric
    insights['classification_quality'] = f"**{success_rate:.1f}%** successful classifications ({total - error_count}/{total} companies)"
    
    # Archetype diversity
    if 'Predicted_Archetype' in df.columns:
        unique_archetypes = df[~df['Predicted_Archetype'].str.contains('Error', na=False)]['Predicted_Archetype'].nunique()
        insights['ecosystem_diversity'] = f"Ecosystem spans **{unique_archetypes} different archetypes** from the Sosa framework"
    
    # Secondary archetypes (hybrid models)
    if 'Secondary_Archetypes' in df.columns:
        has_secondary = df['Secondary_Archetypes'].notna() & (df['Secondary_Archetypes'] != '') & (df['Secondary_Archetypes'] != '[]')
        hybrid_count = has_secondary.sum()
        if hybrid_count > 0:
            insights['hybrid_models'] = f"**{hybrid_count/total*100:.1f}%** of companies exhibit hybrid characteristics, operating across multiple archetypes"
    
    return insights


def get_archetype_summary(df: pd.DataFrame, archetype: str) -> Dict:
    """Get summary statistics for a specific archetype"""
    arch_df = df[df['Predicted_Archetype'] == archetype]
    
    if len(arch_df) == 0:
        return {}
    
    summary = {
        'count': len(arch_df),
        'percentage': len(arch_df) / len(df) * 100,
    }
    
    # Most common wave for this archetype
    if 'Innovation_Wave' in arch_df.columns:
        wave_counts = arch_df['Innovation_Wave'].value_counts()
        if len(wave_counts) > 0:
            summary['dominant_wave'] = wave_counts.index[0]
    
    # Most common DCs
    dc_cols = [col for col in arch_df.columns if col.startswith('DC')]
    if dc_cols:
        dc_mentions = arch_df[dc_cols].apply(lambda x: x.str.contains('DC', na=False).sum())
        if dc_mentions.sum() > 0:
            summary['top_capabilities'] = dc_mentions.nlargest(3).index.tolist()
    
    return summary


def get_wave_characteristics(df: pd.DataFrame, wave: str) -> Dict:
    """Get characteristics of companies in a specific innovation wave"""
    wave_df = df[df['Innovation_Wave'] == wave]
    
    if len(wave_df) == 0:
        return {}
    
    characteristics = {
        'count': len(wave_df),
        'percentage': len(wave_df) / len(df) * 100,
    }
    
    # Most common archetypes in this wave
    if 'Predicted_Archetype' in wave_df.columns:
        arch_counts = wave_df['Predicted_Archetype'].value_counts().head(3)
        characteristics['top_archetypes'] = arch_counts.to_dict()
    
    return characteristics

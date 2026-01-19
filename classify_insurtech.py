import pandas as pd
import os
import re

# Import OpenAI classifier
try:
    from openai_classifier import classify_with_openai
    OPENAI_AVAILABLE = True
except Exception as e:
    OPENAI_AVAILABLE = False
    print(f"⚠️ OpenAI module not available: {e}")
    import traceback
    traceback.print_exc()

# --- CONFIGURATION: ARCHETYPES & KEYWORDS (Legacy Mode) ---
ARCHETYPES = {
    "Enablers": [
        "platform", "infrastructure", "saas", "cloud", "back-end", "white-label", 
        "technology provider", "software", "api", "core system", "digitize", 
        "analytics", "data provider", "underwriting platform", "claims management", "b2b"
    ],
    "Connectors": [
        "marketplace", "comparison", "broker", "aggregator", "connect", "match", 
        "distribution", "agency", "mga", "intermediary", "portal", "agent", "buying"
    ],
    "Innovators": [
        "on-demand", "p2p", "peer-to-peer", "parametric", "microinsurance", 
        "usage-based", "gig economy", "new model", "pay-per-mile", "innovative product", "crypto"
    ],
    "Disruptors": [
        "automation", "ai-driven", "instant", "machine learning", "disrupt", 
        "fully digital", "carrier", "full-stack", "replace", "artificial intelligence", "challenger"
    ],
    "Protectors": [
        "prevention", "mitigation", "monitoring", "iot", "wearables", "telematics", 
        "cyber", "security", "predict", "alert", "safety", "risk management", "health", "wellness"
    ],
    "Integrators": [
        "embedded", "point of sale", "b2b2c", "partner", "integration", "add-on", 
        "api-first", "checkout", "plugin", "ecommerce"
    ],
    "Transformers": [
        "digital transformation", "modernize", "legacy systems", 
        "change management", "insurance transformation", "tech advisory", 
        "implementation partner", "core replacement", "digitization strategy",
        "it consulting"
    ]
}

def load_data(filepath):
    """Loads a CSV or Excel file into a pandas DataFrame."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.csv':
            return pd.read_csv(filepath)
        elif ext in ['.xls', '.xlsx']:
            return pd.read_excel(filepath)
        else:
            raise ValueError("Unsupported file format. Please use CSV or Excel.")
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

def classify_description(text):
    """
    Keyword-based classification (Legacy mode).
    Analyzes text and returns the best matching archetype.
    """
    if not isinstance(text, str):
        return "Unclassified", "Low", ""

    text_lower = text.lower()
    scores = {}
    keywords_found_map = {}
    
    total_words = len(re.findall(r'\b\w+\b', text_lower))
    if total_words == 0:
         return "Unclassified", "Low", ""

    for archetype, keywords in ARCHETYPES.items():
        count = 0
        found = []
        for kw in keywords:
            if kw.lower() in text_lower:
                matches = text_lower.count(kw.lower())
                count += matches
                if matches > 0:
                    found.append(kw)
        
        scores[archetype] = count
        keywords_found_map[archetype] = found

    # Determine winner
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_archetype, best_score = sorted_scores[0]
    
    # Check for tie
    if best_score == 0:
        # Fallback / Rescue Logic for Generic Companies
        generic_keywords = ["insurance", "agency", "brokerage", "services", "ltd", "inc", "group", "solutions"]
        found_generics = [w for w in generic_keywords if w in text_lower]
        
        if found_generics:
            return "Traditional / Generalist", "Low", ", ".join(found_generics)
            
        return "Unclassified", "Low", ""
    
    if len(sorted_scores) > 1:
        second_archetype, second_score = sorted_scores[1]
        if second_score == best_score and best_score > 0:
            return "Hybrid", "Medium", ", ".join(keywords_found_map[best_archetype] + keywords_found_map[second_archetype])

    # Calculate confidence
    confidence = "Low"
    if best_score >= 3:
        confidence = "High"
    elif best_score >= 1:
        confidence = "Medium"
        
    return best_archetype, confidence, ", ".join(keywords_found_map[best_archetype])

def classify_company_row(row, main_desc_col, use_ai=False, ai_model=None):
    """
    Constructs the analysis text from multiple columns and runs classification.
    
    Args:
        row: DataFrame row
        main_desc_col: Main description column name
        use_ai: If True, use OpenAI classification. If False, use keywords.
        ai_model: OpenAI model to use (optional)
    
    Returns:
        Tuple: (archetype, confidence, keywords/justification, secondary_archetypes, dcs, wave)
    """
    # 1. Start with the main user-selected column
    text_parts = []
    if main_desc_col in row.index and pd.notna(row[main_desc_col]):
        text_parts.append(str(row[main_desc_col]))
        
    # 2. Append auxiliary columns if they exist and are not the same as main
    aux_cols = ['Industries', 'Industry Groups', 'Full Description', 'Description']
    
    for col in aux_cols:
        if col in row.index and col != main_desc_col:
            val = row[col]
            if pd.notna(val):
                text_parts.append(str(val))
    
    combined_text = " ".join(text_parts)
    
    # Get company name if available
    name_col_candidates = ['Company', 'Name', 'Organization', 'company_name']
    company_name = "Unknown Company"
    for col in name_col_candidates:
        if col in row.index and pd.notna(row[col]):
            company_name = str(row[col])
            break
    
    # Get industries separately for AI
    industries = ""
    if 'Industries' in row.index and pd.notna(row['Industries']):
        industries = str(row['Industries'])
    elif 'Industry Groups' in row.index and pd.notna(row['Industry Groups']):
        industries = str(row['Industry Groups'])
    
    # Choose classification method
    if use_ai and OPENAI_AVAILABLE:
        try:
            result = classify_with_openai(
                company_name=company_name,
                description=combined_text,
                industries=industries,
                model=ai_model
            )
            # Result format: (archetype, confidence, justification, secondary_archetypes, dcs, wave)
            return result
        except Exception as e:
            print(f"AI classification failed for {company_name}, falling back to keywords: {e}")
            # Fallback to keyword-based
            arch, conf, kw = classify_description(combined_text)
            return (arch, conf, kw, [], "", "")
    else:
        # Keyword-based classification
        arch, conf, kw = classify_description(combined_text)
        # Return in same format as AI (with empty secondary fields)
        return (arch, conf, kw, [], "", "")

def main():
    print("--- InsurTech Classifier (Sosa & Sosa 2025) - Hybrid Mode ---")
    
    # 1. Loading File
    filepath = input("Enter the path to your Excel/CSV file: ").strip().strip('"')
    if not filepath:
        print("No file path provided. Exiting.")
        return

    try:
        df = load_data(filepath)
        print(f"\nSuccessfully loaded '{filepath}'.")
        print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Select Columns
    print("\nAvailable Columns:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    
    try:
        id_idx = int(input("\nEnter the number for the COMPANY NAME (ID) column: "))
        desc_idx = int(input("Enter the number for the DESCRIPTION column: "))
        
        col_name_id = df.columns[id_idx]
        col_name_desc = df.columns[desc_idx]
        
        print(f"\nSelected: ID='{col_name_id}', Description='{col_name_desc}'")
        print("Note: The script will also automatically scan 'Industries' and 'Industry Groups' columns if present.")
    except (ValueError, IndexError):
        print("Invalid column selection. Exiting.")
        return

    # 3. Choose mode
    mode_choice = input("\nUse AI classification? (y/n, default=n): ").strip().lower()
    use_ai = mode_choice == 'y'
    
    if use_ai and not OPENAI_AVAILABLE:
        print("AI mode not available (missing dependencies). Using keyword mode.")
        use_ai = False

    # 4. Process Data
    print(f"\nClassifying companies ({'AI Mode' if use_ai else 'Keyword Mode'})... Please wait.")
    
    results = []
    for index, row in df.iterrows():
        arch, conf, kw, sec_archs, dcs, wave = classify_company_row(row, col_name_desc, use_ai=use_ai)
        results.append({
            "Predicted_Archetype": arch,
            "Confidence_Score": conf,
            "Keywords_Found": kw,
            "Secondary_Archetypes": ", ".join(sec_archs) if sec_archs else "",
            "Driving_Capabilities": ", ".join(dcs) if dcs else "",
            "Innovation_Wave": wave
        })
    
    # Append results to dataframe
    results_df = pd.DataFrame(results)
    final_df = pd.concat([df, results_df], axis=1)

    # 5. Save Output
    output_filename = "insurtech_classified_ai.xlsx" if use_ai else "insurtech_classified_v2.xlsx"
    output_path = os.path.join(os.path.dirname(filepath), output_filename)
    
    try:
        final_df.to_excel(output_path, index=False)
        print(f"\nSuccess! Classified data saved to:\n{output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()

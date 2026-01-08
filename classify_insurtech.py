import pandas as pd
import os
import re

# --- CONFIGURATION: ARCHETYPES & KEYWORDS (Updated S&S 2025) ---
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
    Analyzes text and returns the best matching archetype, 
    confidence score/level, and found keywords.
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
            # Simple substring match (case-insensitive)
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

def classify_company_row(row, main_desc_col):
    """
    Constructs the analysis text from multiple columns and runs classification.
    Prioritizes the selected main description column, but appends content from 
    'Industries', 'Industry Groups', and 'Full Description' if available.
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
    return classify_description(combined_text)

def main():
    print("--- InsurTech Classifier (Sosa & Sosa 2025) - Updated ---")
    
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
        print("Note: The script will also automatically scan 'Industries' and 'Primary Industry' columns if present.")
    except (ValueError, IndexError):
        print("Invalid column selection. Exiting.")
        return

    # 3. Process Data
    print("\nClassifying companies (Updated Logic)... Please wait.")
    
    results = []
    for index, row in df.iterrows():
        archetype, confidence, keywords = classify_company_row(row, col_name_desc)
        results.append({
            "Predicted_Archetype": archetype,
            "Confidence_Score": confidence,
            "Keywords_Found": keywords
        })
    
    # Append results to dataframe
    results_df = pd.DataFrame(results)
    final_df = pd.concat([df, results_df], axis=1)

    # 4. Save Output
    output_filename = "insurtech_classified_v2.xlsx"
    output_path = os.path.join(os.path.dirname(filepath), output_filename)
    
    try:
        final_df.to_excel(output_path, index=False)
        print(f"\nSuccess! Classified data saved to:\n{output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()

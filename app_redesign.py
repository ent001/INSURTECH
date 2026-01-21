"""
InsurTech Analyzer - Redesigned UI
AI-Powered Ecosystem Classification using Sosa & Sosa 2025 Framework
"""

import streamlit as st
import pandas as pd
import time
import os
import io

# Import screens
from screens.upload import render_upload_screen
from screens.loading import render_loading_screen
from screens.dashboard import render_dashboard

# Import classification logic
from classify_insurtech import classify_company_row
import config


# Page config
st.set_page_config(
    page_title="InsurTech Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="auto"  # Allow sidebar to be toggled
)

# Load custom CSS
try:
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass  # CSS is optional

# Initialize session state
if 'screen' not in st.session_state:
    st.session_state.screen = "upload"

if 'processed_count' not in st.session_state:
    st.session_state.processed_count = 0

if 'actual_cost' not in st.session_state:
    st.session_state.actual_cost = 0.0


def run_analysis():
    """Execute the classification analysis with real-time updates"""
    # Get data from session
    df = st.session_state.df_full
    col_mapping = st.session_state.column_mapping
    use_ai = st.session_state.use_ai
    
    # Initialize
    st.session_state.total_companies = len(df)
    st.session_state.processed_count = 0
    st.session_state.actual_cost = 0.0
    
    # Create placeholders for updates
    progress_container = st.empty()
    metrics_container = st.empty()
    
    # Process each company
    results = []
    start_time = time.time()
    
    col_desc = col_mapping['desc']
    
    for idx, row in df.iterrows():
        # Update current company
        company_name = row.get(col_mapping['name'], 'Unknown')
        st.session_state.current_company = company_name[:50]
        
        try:
            # Classify
            arch, conf, kw, sec_archs, dcs, wave = classify_company_row(
                row, col_desc, use_ai=use_ai, 
                ai_model=config.OPENAI_MODEL if use_ai else None
            )
            
            results.append({
                "Predicted_Archetype": arch,
                "Confidence_Score": conf,
                "Keywords_Found": kw,
                "Secondary_Archetypes": ", ".join(sec_archs) if sec_archs else "",
                "Driving_Capabilities": ", ".join(dcs) if dcs else "",
                "Innovation_Wave": wave
            })
            
            # Update session state
            st.session_state.processed_count = len(results)
            if use_ai and arch not in ["API Error", "Unclassified", "Processing Error"]:
                st.session_state.actual_cost += 0.0002
            
            # Update elapsed time
            st.session_state.elapsed_time = time.time() - start_time
            
            # Update UI every company
            progress_pct = (len(results) / len(df)) * 100
            with progress_container:
                st.markdown(f"""
                    <div style='text-align: center;'>
                        <div style='font-size: 48px; font-weight: 700; color: #4CAF50;'>{progress_pct:.0f}%</div>
                        <div style='font-size: 14px; color: #95A5A6;'>{company_name[:40]}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.progress(progress_pct / 100)
            
            with metrics_container:
                col1, col2, col3, col4 = st.columns(4)
                elapsed = time.time() - start_time
                speed = len(results) / elapsed if elapsed > 0 else 0
                
                with col1:
                    st.metric("📊 Progress", f"{len(results)}/{len(df)}")
                with col2:
                    st.metric("💰 Cost", f"${st.session_state.actual_cost:.4f}")
                with col3:
                    st.metric("⚡ Speed", f"{speed:.1f}/s")
                with col4:
                    remaining = len(df) - len(results)
                    eta = remaining / speed if speed > 0 else 0
                    st.metric("⏱️ ETA", f"{int(eta/60)}m {int(eta%60)}s")
            
            # Checkpoint save every 5
            if len(results) % 5 == 0:
                temp_df = pd.concat([
                    df.iloc[:len(results)].reset_index(drop=True), 
                    pd.DataFrame(results)
                ], axis=1)
                temp_df.to_csv("progress_backup.csv", index=False)
            
        except Exception as e:
            results.append({
                "Predicted_Archetype": "Processing Error",
                "Confidence_Score": "Low",
                "Keywords_Found": str(e)[:100],
                "Secondary_Archetypes": "",
                "Driving_Capabilities": "",
                "Innovation_Wave": ""
            })
            st.session_state.processed_count = len(results)
    
    # Combine results with original data
    results_df = pd.DataFrame(results)
    final_df = pd.concat([df.reset_index(drop=True), results_df], axis=1)
    
    # Store in session
    st.session_state.processed_data = final_df
    st.session_state.ai_mode_used = use_ai
    
    # Clean up checkpoint
    if os.path.exists("progress_backup.csv"):
        try:
            os.remove("progress_backup.csv")
        except:
            pass
    
    # Move to dashboard
    st.session_state.screen = "dashboard"
    st.session_state.dashboard_tab = "overview"


# Main app logic
def main():
    screen = st.session_state.screen
    
    if screen == "upload":
        render_upload_screen()
    
    elif screen == "loading":
        # Run analysis with real-time updates
        run_analysis()
        # After completion, rerun to show dashboard
        st.rerun()
    
    elif screen == "dashboard":
        render_dashboard()
        
        # Handle download trigger
        if st.session_state.get('trigger_download', False):
            st.session_state.trigger_download = False
            
            # Create Excel download
            df = st.session_state.processed_data
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Classifications', index=False)
            
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name=f"insurtech_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


if __name__ == "__main__":
    main()

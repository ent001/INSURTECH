import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
import time
import sys
from datetime import datetime
from classify_insurtech import classify_company_row

# Check if OpenAI is available
try:
    from openai_classifier import estimate_cost, calculate_actual_cost
    import config
    AI_MODE_AVAILABLE = True
except Exception as e:
    AI_MODE_AVAILABLE = False
    import traceback
    traceback.print_exc()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="InsurTech Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #e0e0e0;
        padding: 15px 25px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        background-color: #111111; color: white; border: none;
        border-radius: 6px; padding: 0.6rem 1.2rem; font-weight: 600;
        width: 100%; transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #333333; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #eeeeee; }
    h1 { font-size: 2.2rem; font-weight: 700; color: #1a1a1a; }
    h2 { font-size: 1.5rem; font-weight: 600; color: #333333; }
    h3 { font-size: 1.1rem; font-weight: 600; color: #555555; }
</style>
""", unsafe_allow_html=True)

# --- UTILS ---
@st.cache_data
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def save_checkpoint(df, filename="progress_backup.csv"):
    """Save progress checkpoint"""
    try:
        df.to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"Checkpoint save failed: {e}")
        return False

def load_checkpoint(filename="progress_backup.csv"):
    """Load progress checkpoint if exists"""
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return None
    return None

def parse_founding_year(df):
    """Extract founding year from various date formats"""
    candidates = ['founded', 'founding', 'year', 'establishment', 'launch']
    
    matched_col = None
    for col in df.columns:
        if any(cand in col.lower() for cand in candidates):
            matched_col = col
            break
            
    if not matched_col:
        return None, None
        
    years = pd.to_numeric(df[matched_col], errors='coerce')
    
    if years.notna().sum() < (len(df) * 0.3):
        try:
            dates = pd.to_datetime(df[matched_col], errors='coerce')
            years = dates.dt.year
        except:
            pass
            
    return matched_col, years

def main():
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'pause_requested' not in st.session_state:
        st.session_state.pause_requested = False
    if 'processed_count' not in st.session_state:
        st.session_state.processed_count = 0
    if 'actual_cost' not in st.session_state:
        st.session_state.actual_cost = 0.0
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.title("⚙️ Configuration")
        st.markdown("---")
        
        uploaded_file = st.file_uploader("Upload Dataset (CSV/Excel)", type=['xlsx', 'xls', 'csv'])
        
        classification_trigger = False
        use_ai = False
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_preview = pd.read_csv(uploaded_file)
                else:
                    df_preview = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Loaded {len(df_preview)} rows")
                
                # Column selection
                st.markdown("### Column Mapping")
                col_id = st.selectbox("Company Name", df_preview.columns, index=0)
                desc_index = next((i for i, c in enumerate(df_preview.columns) if "description" in c.lower()), 1)
                col_desc = st.selectbox("Description", df_preview.columns, index=min(desc_index, len(df_preview.columns)-1))
                
                st.markdown("---")
                st.markdown("### 🤖 AI Analysis Mode")
                
                if AI_MODE_AVAILABLE:
                    use_ai = st.toggle("Enable AI Expert (Sosa Framework)", value=True)
                    
                    if use_ai:
                        st.info(f"**Model**: {config.OPENAI_MODEL}")
                        st.info(f"**Temperature**: {config.TEMPERATURE} (Deterministic)")
                        
                        # Cost estimate
                        cost_info = estimate_cost(len(df_preview))
                        st.metric("💰 Estimated Cost", f"${cost_info['total_cost_usd']:.3f} USD")
                else:
                    st.error("⚠️ AI mode unavailable")
                    use_ai = False
                
                st.markdown("---")
                
                # Simple button
                classification_trigger = st.button("🚀 START ANALYSIS", type="primary")
                
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.info("📂 Upload a file to begin")

    # --- MAIN AREA ---
    st.title("InsurTech Ecosystem Analyzer")
    mode_badge = "🤖 AI-Powered (Sosa Framework)" if use_ai else "📊 Keyword-Based"
    st.markdown(f"**Mode**: {mode_badge}")

    # --- PROCESSING LOGIC ---
    if classification_trigger and uploaded_file is not None:
        # Initialize stats
        if 'processed_count' not in st.session_state:
            st.session_state.processed_count = 0
        if 'actual_cost' not in st.session_state:
            st.session_state.actual_cost = 0.0
        
        # Load data
        if uploaded_file.name.endswith('.csv'):
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file)
        else:
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file)
        
        # Check for resume
        start_idx = 0
        if 'checkpoint_data' in st.session_state:
            df = st.session_state['checkpoint_data']
            start_idx = len([r for r in df.to_dict('records') if 'Predicted_Archetype' in r and r['Predicted_Archetype']])
        
        results = []
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        # Create metrics placeholders
        metrics_container = st.container()
        with metrics_container:
            col1, col2, col3, col4 = st.columns(4)
            metric_progress = col1.empty()
            metric_cost = col2.empty()
            metric_speed = col3.empty()
            metric_eta = col4.empty()
        
        total = len(df)
        start_time = time.time()
        
        for idx, row in df.iterrows():
            if idx < start_idx:
                continue
            
            try:
                # Classify
                arch, conf, kw, sec_archs, dcs, wave = classify_company_row(
                    row, col_desc, use_ai=use_ai, ai_model=config.OPENAI_MODEL if use_ai else None
                )
                
                results.append({
                    "Predicted_Archetype": arch,
                    "Confidence_Score": conf,
                    "Keywords_Found": kw,
                    "Secondary_Archetypes": ", ".join(sec_archs) if sec_archs else "",
                    "Driving_Capabilities": ", ".join(dcs) if dcs else "",
                    "Innovation_Wave": wave
                })
                
                # Update stats
                st.session_state.processed_count = len(results)
                if use_ai and arch not in ["API Error", "Unclassified", "Processing Error"]:
                    st.session_state.actual_cost += 0.0002
                
                # Calculate metrics
                elapsed = time.time() - start_time
                companies_per_sec = len(results) / elapsed if elapsed > 0 else 0
                remaining_companies = total - len(results)
                eta_seconds = remaining_companies / companies_per_sec if companies_per_sec > 0 else 0
                
                # Update visual metrics
                metric_progress.metric("📊 Progress", f"{len(results)}/{total}", 
                                      f"{(len(results)/total)*100:.1f}%")
                metric_cost.metric("💰 Cost", f"${st.session_state.actual_cost:.4f}")
                metric_speed.metric("⚡ Speed", f"{companies_per_sec:.1f}/sec")
                
                if eta_seconds < 60:
                    eta_display = f"{int(eta_seconds)}s"
                elif eta_seconds < 3600:
                    eta_display = f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s"
                else:
                    eta_display = f"{int(eta_seconds/3600)}h {int((eta_seconds%3600)/60)}m"
                metric_eta.metric("⏱️ ETA", eta_display)
                
                # Update status and progress
                status_placeholder.text(f"Processing: {row.get('Organization Name', 'Unknown')} ({len(results)}/{total})")
                progress_bar.progress(len(results) / total)
                
            except Exception as e:
                st.error(f"⚠️ Error on row {idx}: {e}")
                results.append({
                    "Predicted_Archetype": "Processing Error",
                    "Confidence_Score": "Low",
                    "Keywords_Found": str(e)[:100],
                    "Secondary_Archetypes": "",
                    "Driving_Capabilities": "",
                    "Innovation_Wave": ""
                })
                st.session_state.processed_count = len(results)
            
            # Checkpoint save
            if len(results) % config.CHECKPOINT_FREQUENCY == 0 and len(results) > 0:
                temp_df = pd.concat([df.iloc[:len(results)].reset_index(drop=True), 
                                     pd.DataFrame(results)], axis=1)
                save_checkpoint(temp_df)
                status_placeholder.text(f"💾 Checkpoint saved at {len(results)}/{total}")
            
            # Progress update
            progress_bar.progress(len(results) / total)
        
        progress_bar.progress(1.0)
        status_placeholder.success(f"✅ Completed {len(results)} companies!")
        
        # Final results
        results_df = pd.DataFrame(results)
        
        # Age correction
        reclassified_count = 0
        col_year, year_series = parse_founding_year(df)
        if col_year is not None:
            results_df['Founded_Year'] = year_series
            mask = (results_df['Predicted_Archetype'].isin(['Disruptors', 'Innovators'])) & (results_df['Founded_Year'] < 2010)
            reclassified_count = mask.sum()
            if reclassified_count > 0:
                results_df.loc[mask, 'Predicted_Archetype'] = 'Traditional / Generalist'
                results_df.loc[mask, 'Age_Corrected'] = True
        
        final_df = pd.concat([df.reset_index(drop=True), results_df], axis=1)
        
        # Save to session
        st.session_state['processed_data'] = final_df
        st.session_state['reclassified_count'] = reclassified_count
        st.session_state['ai_mode_used'] = use_ai
        
        # Clean up checkpoint
        if os.path.exists("progress_backup.csv"):
            os.remove("progress_backup.csv")
        
        st.success("✅ Analysis Complete!")

    # --- DISPLAY RESULTS ---
    if 'processed_data' in st.session_state:
        final_df = st.session_state['processed_data']
        ai_used = st.session_state.get('ai_mode_used', False)
        
        st.divider()
        
        # KPI Cards
        kpi_cols = st.columns(4)
        total = len(final_df)
        classified = final_df[~final_df['Predicted_Archetype'].isin(['Unclassified', 'API Error'])].shape[0]
        success_rate = (classified / total) * 100
        top_arch = final_df['Predicted_Archetype'].mode()[0] if not final_df.empty else "N/A"
        
        kpi_cols[0].metric("Total", total)
        kpi_cols[1].metric("Success Rate", f"{success_rate:.1f}%")
        kpi_cols[2].metric("Top Archetype", top_arch)
        kpi_cols[3].metric("💰 Final Cost", f"${st.session_state.actual_cost:.4f}")
        
        st.divider()
        
        # Visualizations
        viz_col1, viz_col2 = st.columns([2, 1])
        
        with viz_col1:
            st.subheader("Archetype Distribution")
            counts = final_df['Predicted_Archetype'].value_counts().reset_index()
            counts.columns = ['Archetype', 'Count']
            fig = px.bar(counts, x='Archetype', y='Count', color='Archetype', text='Count',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(xaxis_title=None, yaxis_title=None, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with viz_col2:
            st.subheader("Distribution")
            fig_donut = px.pie(counts, values='Count', names='Archetype', hole=0.4,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)
        
        # AI-specific insights
        if ai_used:
            st.subheader("🧠 Sosa Framework Analysis")
            ai_col1, ai_col2 = st.columns(2)
            
            with ai_col1:
                st.markdown("### Driving Capabilities")
                dcs_data = final_df['Driving_Capabilities'].str.split(', ').explode()
                dcs_counts = dcs_data.value_counts().head(10).reset_index()
                dcs_counts.columns = ['DC', 'Count']
                if not dcs_counts.empty:
                    fig_dcs = px.bar(dcs_counts, x='DC', y='Count', color='DC')
                    fig_dcs.update_layout(showlegend=False)
                    st.plotly_chart(fig_dcs, use_container_width=True)
            
            with ai_col2:
                st.markdown("### Innovation Waves")
                wave_counts = final_df['Innovation_Wave'].value_counts().reset_index()
                wave_counts.columns = ['Wave', 'Count']
                if not wave_counts.empty:
                    fig_wave = px.pie(wave_counts, values='Count', names='Wave', hole=0.3)
                    st.plotly_chart(fig_wave, use_container_width=True)
        
        # Data explorer
        st.subheader("📋 Data Inspector")
        st.dataframe(final_df, use_container_width=True, height=400)
        
        # Export
        st.subheader("💾 Export")
        exp1, exp2 = st.columns(2)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        suffix = "_ai" if ai_used else "_keywords"
        
        csv_data = convert_df_to_csv(final_df)
        exp1.download_button("📥 CSV", csv_data, f"insurtech{suffix}_{timestamp}.csv", "text/csv")
        
        try:
            excel_data = convert_df_to_excel(final_df)
            exp2.download_button("📥 Excel", excel_data, f"insurtech{suffix}_{timestamp}.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except:
            exp2.warning("Excel export failed")

if __name__ == "__main__":
    main()

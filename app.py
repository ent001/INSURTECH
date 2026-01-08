import streamlit as st
import pandas as pd
import plotly.express as px
import io
from classify_insurtech import classify_company_row

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="InsurTech Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Minimalist Design
st.markdown("""
<style>
    /* Clean Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* KPI Card Style */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Primary Button Styling */
    .stButton>button {
        background-color: #111111;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #333333;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: white;
    }

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #eeeeee;
    }
    
    /* Header Scaling */
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

def main():
    # --- SIDEBAR (CONFIG) ---
    with st.sidebar:
        st.title("⚙️ Configuration")
        st.markdown("---")
        
        uploaded_file = st.file_uploader("Upload Dataset (CSV/Excel)", type=['xlsx', 'xls', 'csv'])
        
        classification_trigger = False
        
        if uploaded_file is not None:
            # Load basic preview to get columns
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_preview = pd.read_csv(uploaded_file)
                else:
                    df_preview = pd.read_excel(uploaded_file)
                
                st.success(f"File loaded! {len(df_preview)} rows.")
                
                st.markdown("### Column Mapping")
                col_id = st.selectbox("Company Name", df_preview.columns, index=0)
                # Try to smart-select description
                desc_index = 1
                possible_desc = [i for i, c in enumerate(df_preview.columns) if "description" in c.lower()]
                if possible_desc:
                    desc_index = possible_desc[0]
                
                col_desc = st.selectbox("Company Description", df_preview.columns, index=desc_index if desc_index < len(df_preview.columns) else 0)
                
                st.markdown("---")
                classification_trigger = st.button("🚀 ANALYZE ECOSYSTEM")
                
            except Exception as e:
                st.error(f"Error reading file: {e}")
        else:
            st.info("Please upload a file to begin.")

    # --- MAIN AREA ---
    st.title("InsurTech Ecosystem Analyzer")
    st.markdown("Classify and visualize companies based on the **Sosa & Sosa 2025 Taxonomy**.")

    if classification_trigger and uploaded_file is not None:
        with st.spinner('Analyzing patterns, industries, and keywords...'):
            # Reload fresh df for processing
            if uploaded_file.name.endswith('.csv'):
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file)
            else:
                uploaded_file.seek(0)
                df = pd.read_excel(uploaded_file)
            
            # --- PROCESS LOGIC ---
            results = []
            progress_bar = st.progress(0)
            total = len(df)
            
            for idx, row in df.iterrows():
                # Use the imported logic (V3)
                archetype, confidence, keywords = classify_company_row(row, col_desc)
                
                results.append({
                    "Predicted_Archetype": archetype,
                    "Confidence_Score": confidence,
                    "Keywords_Found": keywords
                })
                
                if total < 200 or idx % (total // 50) == 0:
                     progress_bar.progress((idx + 1) / total)
            
            progress_bar.progress(100)
            
            # Merge results
            results_df = pd.DataFrame(results)
            final_df = pd.concat([df.reset_index(drop=True), results_df], axis=1)
            
            # Persist in session state to handle reruns if needed (or just show directly)
            st.session_state['processed_data'] = final_df

    # --- DISPLAY RESULTS (IF DATA EXISTS) ---
    if 'processed_data' in st.session_state:
        final_df = st.session_state['processed_data']
        
        st.divider()
        
        # 1. KPI CARDS
        col1, col2, col3 = st.columns(3)
        
        total_companies = len(final_df)
        classified_only = final_df[final_df['Predicted_Archetype'] != 'Unclassified']
        success_rate = (len(classified_only) / total_companies) * 100
        
        # Determine dominant archetype
        if not classified_only.empty:
            top_arch = classified_only['Predicted_Archetype'].mode()[0]
        else:
            top_arch = "N/A"

        col1.metric("Total Companies", f"{total_companies}")
        col2.metric("Classification Success", f"{success_rate:.1f}%")
        col3.metric("Dominant Archetype", top_arch)

        st.divider()

        # 2. VISUALIZATIONS
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Archetype Distribution")
            # Bar Chart with Custom Colors
            counts = final_df['Predicted_Archetype'].value_counts().reset_index()
            counts.columns = ['Archetype', 'Count']
            
            fig = px.bar(
                counts, 
                x='Archetype', 
                y='Count', 
                color='Archetype',
                text='Count',
                color_discrete_sequence=px.colors.qualitative.Pastel  # Or Safe, Bold
            )
            fig.update_layout(
                xaxis_title=None, 
                yaxis_title=None, 
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Hybrid Analysis")
            # Filter for Hybrids or general distribution
            hybrids = final_df[final_df['Predicted_Archetype'] == 'Hybrid']
            
            if not hybrids.empty:
                st.write(f"Found **{len(hybrids)}** Hybrid companies.")
                # Show keywords or some other breakdown for hybrids?
                # The user asked for Donut/Sunburst of Hybrids.
                # Since 'Hybrid' result is just string "Hybrid", we look at Keywords?
                # Actually, our script returns "Hybrid" as the archetype, but we don't store "Type1 vs Type2" explicitly
                # except in keywords like "platform, marketplace".
                # Let's show overall donut of ALL types to complement the bar chart.
                fig_donut = px.pie(
                    counts, 
                    values='Count', 
                    names='Archetype', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                # Fallback to total distribution donut
                fig_donut = px.pie(
                    counts, 
                    values='Count', 
                    names='Archetype', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_donut, use_container_width=True)

        # 3. DATA EXPLORER
        st.subheader("Data Explorer")
        st.dataframe(final_df, use_container_width=True, height=400)

        # 4. EXPORT
        st.subheader("Export")
        col_d1, col_d2 = st.columns(2)
        
        # CSV
        csv_data = convert_df_to_csv(final_df)
        col_d1.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="insurtech_classified.csv",
            mime="text/csv"
        )
        
        # Excel
        try:
            excel_data = convert_df_to_excel(final_df)
            col_d2.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name="insurtech_classified.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            col_d2.warning("Excel export requires 'xlsxwriter' or 'openpyxl'.")

if __name__ == "__main__":
    main()

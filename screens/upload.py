"""
Upload Screen - Clean file upload interface
"""

import streamlit as st
import pandas as pd


def render_upload_screen():
    """Render the upload screen"""
    
    # Center content
    st.markdown("""
        <div style='text-align: center; padding-top: 80px;'>
            <h1 style='font-size: 48px; color: #2C3E50; margin-bottom: 8px;'>
                🧬 InsurTech Analyzer
            </h1>
            <p style='font-size: 18px; color: #95A5A6; margin-bottom: 60px;'>
                AI-Powered Ecosystem Classification using Sosa Framework
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Upload zone - centered
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        uploaded_file = st.file_uploader(
            "📁",
            type=['csv', 'xlsx'],
            help="Upload a CSV or Excel file with company data",
            label_visibility="collapsed",
            key="file_uploader"
        )
        
        if uploaded_file:
            # Load full data
            if uploaded_file.name.endswith('.csv'):
                df_full = pd.read_csv(uploaded_file)
            else:
                df_full = pd.read_excel(uploaded_file)
            
            st.success(f"✅ **{len(df_full)} companies** loaded from {uploaded_file.name}")
            
            # Compact settings in 2 columns
            st.markdown("---")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("#### 🗂️ Column Mapping")
                col_name = st.selectbox("Company Name", df_full.columns, index=0)
                col_desc = st.selectbox("Description", df_full.columns, index=min(1, len(df_full.columns)-1))
            
            with col_b:
                st.markdown("#### 🤖 Analysis Mode")
                use_ai = st.toggle(
                    "AI Expert (Sosa Framework)",
                    value=True,
                    help="Use GPT-4o-mini"
                )
                
                if use_ai:
                    from openai_classifier import estimate_cost
                    cost_info = estimate_cost(len(df_full))
                    time_est = len(df_full) / 2
                    mins = int(time_est // 60)
                    secs = int(time_est % 60)
                    
                    st.caption(f"💰 Cost: ${cost_info['total_cost_usd']:.3f} | ⏱️ Time: ~{mins}m {secs}s")
            
            # Start button
            st.markdown("---")
            if st.button("🚀 START ANALYSIS", type="primary", use_container_width=True):
                # Store in session state
                st.session_state.screen = "loading"
                st.session_state.uploaded_file = uploaded_file
                st.session_state.column_mapping = {
                    'name': col_name,
                    'desc': col_desc
                }
                st.session_state.use_ai = use_ai
                st.session_state.df_full = df_full
                st.session_state.processed_count = 0
                st.session_state.total_companies = len(df_full)
                st.session_state.current_company = ""
                st.rerun()
        
        else:
            # Empty state - clickable area
            st.markdown("""
                <div style='text-align: center; color: #95A5A6; margin-top: 20px;'>
                    <div style='font-size: 14px; margin-bottom: 8px;'>
                        Supported formats: CSV, XLSX
                    </div>
                    <div style='font-size: 12px;'>
                        Required columns: Company Name, Description
                    </div>
                </div>
            """, unsafe_allow_html=True)


"""
Dashboard Screen - Main insights and visualization hub
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.insights_generator import generate_insights


def render_sidebar():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.markdown("""
            <div class='sidebar-logo'>
                🧬 InsurTech Analyzer
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        tabs = {
            "📊 Overview": "overview",
            "🧬 Archetypes": "archetypes",
            "🔬 Capabilities": "capabilities",
            "🌊 Innovation Waves": "waves",
            "📁 Data Explorer": "data"
        }
        
        selected_tab = st.session_state.get('dashboard_tab', 'overview')
        
        for label, key in tabs.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.dashboard_tab = key
                st.rerun()
        
        st.markdown("---")
        
        # Export options
        st.markdown("### 📤 Export")
        if st.button("📊 Download Excel", use_container_width=True):
            # Trigger download
            st.session_state.trigger_download = True
            st.rerun()
        
        st.markdown("---")
        
        # New analysis
        if st.button("🔄 New Analysis", use_container_width=True):
            # Clear session and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.screen = "upload"
            st.rerun()


def render_overview_tab(df: pd.DataFrame):
    """Render the overview tab with key metrics and insights"""
    
    # Key metrics row - aligned with minimalist icons
    col1, col2, col3, col4 = st.columns(4)
    
    # Total companies
    with col1:
        total = len(df)
        st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='width: 48px; height: 48px; background: #E3F2FD; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; border: 2px solid #2196F3;'>
                    <span style='font-size: 24px; color: #2196F3;'>🏢</span>
                </div>
                <div style='font-size: 32px; font-weight: 700; color: #2C3E50; margin: 8px 0;'>{total}</div>
                <div style='font-size: 11px; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px;'>TOTAL COMPANIES</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Success rate
    with col2:
        errors = df['Predicted_Archetype'].str.contains('Error', na=False).sum()
        success_rate = ((total - errors) / total * 100) if total > 0 else 0
        st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='width: 48px; height: 48px; background: #E8F5E9; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; border: 2px solid #4CAF50;'>
                    <span style='font-size: 24px; color: #4CAF50;'>✓</span>
                </div>
                <div style='font-size: 32px; font-weight: 700; color: #4CAF50; margin: 8px 0;'>{success_rate:.1f}%</div>
                <div style='font-size: 11px; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px;'>SUCCESS RATE</div>
                <div style='font-size: 11px; color: #4CAF50; margin-top: 4px;'>+{total-errors} classified</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Top archetype
    with col3:
        clean_df = df[~df['Predicted_Archetype'].str.contains('Error', na=False)]
        if len(clean_df) > 0:
            top_arch = clean_df['Predicted_Archetype'].value_counts().index[0]
            top_count = clean_df['Predicted_Archetype'].value_counts().values[0]
        else:
            top_arch = "N/A"
            top_count = 0
        
        st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='width: 48px; height: 48px; background: #FFF3E0; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; border: 2px solid #FF9800;'>
                    <span style='font-size: 24px;'>🏆</span>
                </div>
                <div style='font-size: 18px; font-weight: 700; color: #2C3E50; margin: 8px 0;'>{top_arch}</div>
                <div style='font-size: 11px; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px;'>TOP ARCHETYPE</div>
                <div style='font-size: 11px; color: #666; margin-top: 4px;'>{top_count} companies</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Total cost
    with col4:
        cost = st.session_state.get('actual_cost', 0.0)
        cost_per_company = cost / total if total > 0 else 0
        st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='width: 48px; height: 48px; background: #FFF9C4; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; border: 2px solid #FBC02D;'>
                    <span style='font-size: 24px;'>💰</span>
                </div>
                <div style='font-size: 32px; font-weight: 700; color: #2C3E50; margin: 8px 0;'>${cost:.4f}</div>
                <div style='font-size: 11px; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px;'>TOTAL COST</div>
                <div style='font-size: 11px; color: #666; margin-top: 4px;'>${cost_per_company:.5f} per company</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Charts row
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📈 Distribution Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        # Archetype distribution pie chart
        clean_df = df[~df['Predicted_Archetype'].str.contains('Error', na=False)]
        if len(clean_df) > 0:
            arch_counts = clean_df['Predicted_Archetype'].value_counts()
            
            fig = px.pie(
                values=arch_counts.values,
                names=arch_counts.index,
                title="Archetype Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Innovation waves donut chart
        if 'Innovation_Wave' in df.columns:
            wave_data = df[df['Innovation_Wave'].notna()]
            if len(wave_data) > 0:
                wave_counts = wave_data['Innovation_Wave'].value_counts()
                
                fig = go.Figure(data=[go.Pie(
                    labels=wave_counts.index,
                    values=wave_counts.values,
                    hole=.4
                )])
                fig.update_layout(title="Innovation Waves", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # Recent classifications table
    st.markdown("### 📋 Recent Classifications")
    display_df = df[[
        'Organization Name' if 'Organization Name' in df.columns else df.columns[0],
        'Predicted_Archetype',
        'Confidence_Score',
        'Innovation_Wave' if 'Innovation_Wave' in df.columns else 'Keywords_Found'
    ]].head(10)
    
    st.dataframe(display_df, use_container_width=True, height=400)


def render_archetypes_tab(df: pd.DataFrame):
    """Render archetypes analysis tab"""
    st.markdown("## 🧬 Archetype Analysis")
    
    clean_df = df[~df['Predicted_Archetype'].str.contains('Error', na=False)]
    
    # Bar chart with discrete colors
    arch_counts = clean_df['Predicted_Archetype'].value_counts()
    
    fig = px.bar(
        x=arch_counts.index,
        y=arch_counts.values,
        title="Companies by Archetype",
        labels={'x': 'Archetype', 'y': 'Count'},
        color=arch_counts.index,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown
    st.markdown("### Breakdown by Archetype")
    
    for archetype in arch_counts.index:
        with st.expander(f"**{archetype}** ({arch_counts[archetype]} companies)"):
            arch_df = clean_df[clean_df['Predicted_Archetype'] == archetype]
            st.dataframe(arch_df[[
                'Organization Name' if 'Organization Name' in arch_df.columns else arch_df.columns[0],
                'Confidence_Score',
                'Keywords_Found'
            ]].head(5), use_container_width=True)


def render_capabilities_tab(df: pd.DataFrame):
    """Render capabilities analysis tab"""
    st.markdown("## 🔬 Driving Capabilities Analysis")
    
    # DC distribution
    dc_cols = [col for col in df.columns if 'Driving_Capabilities' in col or col.startswith('DC')]
    
    if dc_cols:
        st.info("DC1: Infrastructure | DC2: Data & Analytics | DC3: UX | DC4: Product Design | DC5: Distribution")
        
        # Parse and count DCs
        all_dcs = []
        for _, row in df.iterrows():
            if 'Driving_Capabilities' in df.columns and pd.notna(row['Driving_Capabilities']):
                dcs = str(row['Driving_Capabilities']).split(',')
                all_dcs.extend([dc.strip() for dc in dcs if dc.strip()])
        
        if all_dcs:
            dc_counts = pd.Series(all_dcs).value_counts()
            
            fig = px.bar(
                x=dc_counts.index,
                y=dc_counts.values,
                title="Driving Capabilities Distribution",
                labels={'x': 'Capability', 'y': 'Mentions'},
                color=dc_counts.index,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


def render_waves_tab(df: pd.DataFrame):
    """Render innovation waves tab"""
    st.markdown("## 🌊 Innovation Waves Analysis")
    
    if 'Innovation_Wave' in df.columns:
        wave_data = df[df['Innovation_Wave'].notna()]
        
        if len(wave_data) > 0:
            wave_counts = wave_data['Innovation_Wave'].value_counts().sort_index()
            
            # Single row layout - chart takes 2/3, info takes 1/3
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Larger bar chart with discrete colors
                fig = px.bar(
                    x=wave_counts.index,
                    y=wave_counts.values,
                    title="Companies by Innovation Wave",
                    labels={'x': 'Wave', 'y': 'Count'},
                    color=wave_counts.index,
                    color_discrete_sequence=['#80DEEA', '#26C6DA', '#00ACC1']
                )
                fig.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Wave characteristics in compact cards
                st.markdown("### Wave Characteristics")
                
                st.markdown("""
                    <div style='background: white; border-radius: 8px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.06);'>
                        <div style='font-weight: 700; color: #2C3E50; font-size: 14px; margin-bottom: 6px;'>Wave 1.0 (2010-2015)</div>
                        <div style='font-size: 12px; color: #666; line-height: 1.5;'>Disruptive startups, P2P models, desintermediación</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                    <div style='background: white; border-radius: 8px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.06);'>
                        <div style='font-weight: 700; color: #2C3E50; font-size: 14px; margin-bottom: 6px;'>Wave 2.0 (2015-2020)</div>
                        <div style='font-size: 12px; color: #666; line-height: 1.5;'>B2B enablers, APIs, colaboración con incumbentes</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                    <div style='background: white; border-radius: 8px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.06);'>
                        <div style='font-weight: 700; color: #2C3E50; font-size: 14px; margin-bottom: 6px;'>Wave 3.0 (2020-present)</div>
                        <div style='font-size: 12px; color: #666; line-height: 1.5;'>Ecosistemas, embedded insurance, open platforms</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Distribution summary
                st.markdown("<br>", unsafe_allow_html=True)
                for wave, count in wave_counts.items():
                    pct = (count / len(wave_data)) * 100
                    st.markdown(f"""
                        <div style='margin-bottom: 8px;'>
                            <div style='display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;'>
                                <span style='color: #666;'>Wave {wave}</span>
                                <span style='color: #2C3E50; font-weight: 600;'>{count} ({pct:.1f}%)</span>
                            </div>
                            <div style='background: #E0E0E0; height: 6px; border-radius: 3px; overflow: hidden;'>
                                <div style='background: #00ACC1; width: {pct}%; height: 100%;'></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)


def render_data_explorer_tab(df: pd.DataFrame):
    """Render full data explorer"""
    st.markdown("## 📁 Data Explorer")
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search companies", "")
    with col2:
        archetype_filter = st.multiselect(
            "Filter by Archetype",
            options=df['Predicted_Archetype'].unique()
        )
    
    # Apply filters
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
    if archetype_filter:
        filtered_df = filtered_df[filtered_df['Predicted_Archetype'].isin(archetype_filter)]
    
    st.info(f"Showing {len(filtered_df)} of {len(df)} companies")
    st.dataframe(filtered_df, use_container_width=True, height=600)


def render_dashboard():
    """Main dashboard rendering function"""
    # Load CSS
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Hide sidebar close button to keep it always open
    st.markdown("""
        <style>
        /* Hide the sidebar close button */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Keep sidebar always open */
        [data-testid="stSidebar"] {
            pointer-events: auto !important;
        }
        
        /* Hide the X button inside sidebar */
        [data-testid="stSidebar"] button[kind="header"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Get results data
    df = st.session_state.get('processed_data', pd.DataFrame())
    
    if df.empty:
        st.error("No data to display. Please run an analysis first.")
        return
    
    # Render selected tab
    tab = st.session_state.get('dashboard_tab', 'overview')
    
    if tab == 'overview':
        render_overview_tab(df)
    elif tab == 'archetypes':
        render_archetypes_tab(df)
    elif tab == 'capabilities':
        render_capabilities_tab(df)
    elif tab == 'waves':
        render_waves_tab(df)
    elif tab == 'data':
        render_data_explorer_tab(df)

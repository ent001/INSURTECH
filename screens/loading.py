"""
Loading Screen - Visual progress with live metrics
"""

import streamlit as st
import time


def render_loading_screen():
    """Render the loading/processing screen with centered design"""
    
    # Get progress from session
    progress = st.session_state.get('processed_count', 0)
    total = st.session_state.get('total_companies', 1)
    progress_pct = (progress / total * 100) if total > 0 else 0
    
    # Metrics at top
    elapsed = st.session_state.get('elapsed_time', 0.01)
    speed = (progress / elapsed) if elapsed > 0 and progress > 0 else 0
    cost = st.session_state.get('actual_cost', 0.0)
    
    remaining = total - progress
    eta_seconds = (remaining / speed) if speed > 0 else 0
    if eta_seconds < 60:
        eta_display = f"{int(eta_seconds)}s"
    elif eta_seconds < 3600:
        eta_display = f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s"
    else:
        eta_display = f"{int(eta_seconds/3600)}h {int((eta_seconds%3600)/60)}m"
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div style='text-align: center; padding: 16px; background: white; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);'>
                <div style='font-size: 11px; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;'>📊 Progress</div>
                <div style='font-size: 24px; font-weight: 700; color: #2C3E50;'>{progress}/{total}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='text-align: center; padding: 16px; background: white; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);'>
                <div style='font-size: 11px; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;'>💰 Cost</div>
                <div style='font-size: 24px; font-weight: 700; color: #2C3E50;'>${cost:.4f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='text-align: center; padding: 16px; background: white; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);'>
                <div style='font-size: 11px; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;'>⚡ Speed</div>
                <div style='font-size: 24px; font-weight: 700; color: #2C3E50;'>{speed:.1f}/s</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style='text-align: center; padding: 16px; background: white; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);'>
                <div style='font-size: 11px; color: #95A5A6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;'>⏱️ ETA</div>
                <div style='font-size: 24px; font-weight: 700; color: #2C3E50;'>{eta_display}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # BIG vertical spacer to push content to middle
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
    
    # Main title centered
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h2 style='color: #2C3E50; font-size: 22px; margin-bottom: 8px;'>
                🧬 Analyzing InsurTech Ecosystem
            </h2>
            <p style='color: #95A5A6; font-size: 13px;'>
                Using Sosa & Sosa 2025 Framework
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # HUGE PERCENTAGE - not in columns, full width
    st.markdown(f"""
        <div style='text-align: center; margin: 0 auto 30px; max-width: 800px;'>
            <div style='font-size: 96px; font-weight: 700; color: #4CAF50; margin-bottom: 16px; line-height: 1;'>
                {progress_pct:.0f}%
            </div>
            <div style='font-size: 16px; color: #666; margin-bottom: 24px;'>
                {st.session_state.get('current_company', 'Initializing...')[:60]}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar - centered in smaller container
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.progress(progress_pct / 100)
        
        # Text below bar
        st.markdown(f"""
            <div style='text-align: center; margin-top: 12px;'>
                <span style='font-size: 14px; color: #95A5A6; font-weight: 500;'>{progress} of {total} companies processed</span>
            </div>
        """, unsafe_allow_html=True)
    
    # Checkpoint info
    if progress > 0 and progress % 5 == 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='text-align: center;'>
                <span style='background: #E8F5E9; color: #2E7D32; padding: 8px 16px; border-radius: 16px; font-size: 13px;'>
                    💾 Checkpoint saved ({progress}/{total})
                </span>
            </div>
        """, unsafe_allow_html=True)

"""
Configuracoes de tema Hospitalar Moderno
"""

import streamlit as st

def aplicar_tema():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0EA5E9 0%, #0284C7 100%); color: white; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stMarkdown h2 { color: white !important; }
    [data-testid="stSidebar"] .stRadio > label { color: white !important; font-weight: 500; }
    [data-testid="stSidebar"] .stRadio > div { background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 8px; }
    .stCard, .element-container, .stMarkdown, .stDataFrame { background-color: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 6px rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.1); }
    h1, h2, h3, h4, h5, h6 { color: #0C4A6E !important; font-family: 'Segoe UI', system-ui, sans-serif; font-weight: 600; }
    h1 { font-size: 2.5rem; } h2 { font-size: 2rem; } h3 { font-size: 1.5rem; }
    .stButton > button { background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); border: none; border-radius: 8px; color: white; font-weight: 600; padding: 12px 24px; font-size: 14px; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(14, 165, 233, 0.2); }
    .stButton > button:hover { background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%); transform: translateY(-2px); box-shadow: 0 6px 12px rgba(14, 165, 233, 0.3); }
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #059669 0%, #047857 100%); box-shadow: 0 4px 6px rgba(5, 150, 105, 0.2); }
    .stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #047857 0%, #065F46 100%); box-shadow: 0 6px 12px rgba(5, 150, 105, 0.3); }
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > select { border: 2px solid #E0F2FE; border-radius: 8px; padding: 10px 14px; font-size: 14px; transition: all 0.3s ease; }
    .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus, .stSelectbox > div > div > select:focus { border-color: #0EA5E9; box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1); }
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label { color: #0C4A6E; font-weight: 600; font-size: 14px; margin-bottom: 6px; }
    .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(14, 165, 233, 0.1); }
    .stDataFrame thead { background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); color: white; }
    .stDataFrame tbody tr:nth-child(even) { background-color: #F0F9FF; }
    .stDataFrame tbody tr:hover { background-color: #E0F2FE; }
    .stMetric { background: linear-gradient(135deg, #FFFFFF 0%, #F0F9FF 100%); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.1); }
    .stMetricLabel { color: #0C4A6E !important; font-weight: 600; }
    .stMetricValue { color: #0EA5E9 !important; font-weight: 700; }
    .stSuccess { background-color: #D1FAE5; border-left: 4px solid #059669; color: #065F46; border-radius: 8px; padding: 12px 16px; }
    .stError { background-color: #FEE2E2; border-left: 4px solid #DC2626; color: #991B1B; border-radius: 8px; padding: 12px 16px; }
    .stWarning { background-color: #FEF3C7; border-left: 4px solid #F59E0B; color: #92400E; border-radius: 8px; padding: 12px 16px; }
    .stInfo { background-color: #E0F2FE; border-left: 4px solid #0EA5E9; color: #0C4A6E; border-radius: 8px; padding: 12px 16px; }
    hr { border-color: #E0F2FE !important; }
    .stCheckbox > label { color: #0C4A6E; font-weight: 500; }
    .stSpinner > div { border-top-color: #0EA5E9 !important; }
    [data-testid="stBalloon"] { color: #0EA5E9; }
    @media (max-width: 768px) { h1 { font-size: 2rem; } h2 { font-size: 1.5rem; } .stMetric { padding: 15px; } }
    </style>
    """, unsafe_allow_html=True)

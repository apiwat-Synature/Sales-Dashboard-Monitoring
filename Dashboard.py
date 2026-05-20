# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
import calendar
from datetime import datetime, timedelta
from st_keyup import st_keyup

# --- 1. CONFIG & STYLES ---
st.set_page_config(
    page_title="Sales Monitoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    [data-testid="stSidebarContent"] { padding-top: 0rem !important; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.8rem !important; }
    .block-container { padding-top: 2rem !important; padding-left: 1rem !important; padding-right: 1rem !important; padding-bottom: 0rem !important; }
    
    button[kind="primary"] { background-color: #28a745 !important; border-color: #28a745 !important; color: white !important; }
    .problem-item { font-size: 0.85rem; padding: 8px 10px; background-color: #fff5f5; border-left: 4px solid #ff4b4b; border-radius: 4px; margin-bottom: 6px; }
    footer { visibility: hidden; }

    /* ปรับแต่งปุ่ม Back to Main Page */
    div.stButton > button[key="back_to_welcome"] {
        background-color: #1e293b !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.4rem 0.8rem !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        width: 100% !important;
        margin-top: 10px !important;
    }

    /* ปรับขนาดตัวอักษรในช่อง Input ของหน้า Config */
    div[data-testid="stExpander"] input {
        font-size: 0.9rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA FETCHING ---
# ลิงก์รหัส npoint ต้นฉบับ (เปรียบเสมือนค่าที่ Get มาจากโค้ดบน GitHub)
BRAND_CONFIG = {
    "Eat Am Are": "506e2020f13e6d515726",
    "JonesSalad": "695d80e67b2a8c1ca2ee",
    "Laem Charoen Seafood": "98d3735c3a0a94a513f6",
    "Saemaeul/BHC/Solsot": "90a9e466a623369dfac4",
    "Tenjo": "da133cadd434914e0816",
    "Senju": "c9d33da3c6f38be07eb8",
    "Wisdom": "0ce6c62297f8f0e3405e",
    "Seefah": "41e908643e98b11931ee",
    "Bake Brother": "363e1bba0b9907b65532",
    "Ohsho": "abb1c88b8db54ca2ee87",
    "ตั่วเปา": "a8b719f0d97ea01d264c",
    "Maesriruen": "2e8f853bc23b3ba8b140",
    "You&I": "6111d22633f84f5ee575",
    "เสวย": "e7a4885887fc49db4765",
    "Shinkanzen": "5aae88055a5ff0d32c96"
}
CONFIG_API = "https://api.npoint.io/9898efa2a5853bf5f886"

def get_config():
    try:
        res = requests.get(CONFIG_API, timeout=5)
        return res.json() if res.status_code == 200 else {}
    except: return {}

def save_config(full_config):
    requests.post(CONFIG_API, json=full_config)

@st.cache_data(ttl=30)
def get_data_from_api(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            if not df.empty:
                # แปลงสถานะทุกฟิลด์ให้เป็นตัวเลขเพื่อความแม่นยำ
                for col in ['status_code', 'status_log', 'status_realtime']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                df['sync_date'] = pd.to_datetime(df['sync_date'])
                return df
    except: pass
    return pd.DataFrame()

# --- 3. SIDEBAR ---
with st.sidebar:
    now = datetime.utcnow() + timedelta(hours=7)
    current_full_config = get_config()
    monitors_config = current_full_config.get("_monitors", {})
    def sort_brands_logic(b_name):
        return int(monitors_config.get(b_name, {}).get("order", 999))
    brand_keys = sorted(list(BRAND_CONFIG.keys()), key=sort_brands_logic)
    DEFAULT_COLORS = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]
    
    if "selected_brand" not in st.session_state:
        st.session_state.selected_brand = "🛑 SELECT BRAND 🛑"

    st.markdown("""
        <style>
        div[data-testid="stSidebar"] button[kind="secondary"] { padding: 1px 2px !important; min-height: 32px !important; font-size: 0.6rem !important; }
        div[data-testid="stSidebar"] button[kind="primary"] {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
            border: none !important; color: #f1f5f9 !important; font-size: 0.75rem !important;
            font-weight: 600 !important; border-radius: 6px !important; padding: 6px 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. Date & Time card
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                    padding: 12px 15px; border-radius: 12px; margin-bottom: 10px; 
                    border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase; letter-spacing: 0.5px;">📅 Today</div>
                    <div style="font-size:0.95rem; font-weight:700; color:#f8fafc;">{now.strftime("%d %b %Y")}</div>
                </div>
                <div style="text-align: right; border-left: 1px solid rgba(148, 163, 184, 0.3); padding-left: 12px;">
                    <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase; letter-spacing: 0.5px;">🕒 Time</div>
                    <div style="font-size:1.1rem; font-weight:800; color:#38bdf8;">{now.strftime("%H:%M")}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mode Toggle under Date Card
    view_mode = st.radio(
        "Display Mode",
        ["📋 History (Log)", "⚡ Real-time"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    # 2. Brand selector
    st.markdown("<div style='font-size:0.65rem; font-weight:600; color:#64748b; text-transform:uppercase; margin-bottom:4px;'>เลือกแบรนด์</div>", unsafe_allow_html=True)

    selected_brand = st.session_state.selected_brand

    if selected_brand == "🛑 SELECT BRAND 🛑":
        display_brands = brand_keys
    else:
        display_brands = [selected_brand]

    for i, brand in enumerate(display_brands):
        original_idx = brand_keys.index(brand)
        cfg = monitors_config.get(brand, {})
        color = cfg.get("color", DEFAULT_COLORS[original_idx % len(DEFAULT_COLORS)])
        
        m1 = cfg.get("m1", "")
        m2 = cfg.get("m2", "")
        monitors_text = " / ".join([x for x in [m1, m2] if x]) or "—"
        
        is_active = (selected_brand == brand)
        bg = f"{color}25" if is_active else f"{color}10"
        border_w = "4px" if is_active else "2px"
        
        col_band, col_btn = st.columns([5, 1.2])
        with col_band:
            st.markdown(
                f'<div style="border-left:{border_w} solid {color}; background:{bg}; padding:4px 8px; border-radius:0 6px 6px 0; margin:2px 0;">'
                f'<div style="font-size:0.9rem; font-weight:{"700" if is_active else "500"}; color:{"#0f172a" if is_active else "#475569"}; line-height:1.2;">{brand}</div>'
                f'<div style="font-size:0.75rem; color:{color}; font-weight:600;">{monitors_text}</div>'
                f'</div>', unsafe_allow_html=True
            )
        with col_btn:
            btn_label = "▶" if selected_brand == "🛑 SELECT BRAND 🛑" else "🔄"
            if st.button(btn_label, key=f"brand_btn_{brand}", use_container_width=True):
                st.session_state.selected_brand = brand
                st.rerun()

    selected_brand = st.session_state.selected_brand

    # 3. ปี / เดือน
    st.markdown("<div style='margin-top:5px'></div>", unsafe_allow_html=True)
    col_y, col_m = st.columns(2)
    with col_y:
        y = st.selectbox("ปี", [2025, 2026], index=1, key="sb_year")
    with col_m:
        month_list = list(calendar.month_name)[1:]
        m_name = st.selectbox("เดือน", month_list, index=now.month - 1, key="sb_month")
        m = month_list.index(m_name) + 1

    summary_placeholder = st.empty()
    st.markdown("<hr style='border:none; border-top:1px solid #e2e8f0; margin:8px 0;'>", unsafe_allow_html=True)

    # 4. Settings (แสดงเฉพาะหน้าแรกตามปกติ)
    if selected_brand == "🛑 SELECT

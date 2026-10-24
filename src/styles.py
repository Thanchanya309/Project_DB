import streamlit as st


def apply_styles():
    st.markdown('''<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');
    html,body,[class*="css"], [data-testid="stApp"] {font-family:'Kanit',sans-serif;color:#43334C}
    .stApp {background:#F8F4EC} .block-container {padding-top:3.5rem;max-width:1540px}
    [data-testid="stSidebar"] {background:white;border-right:1px solid #f0e4ed}
    [data-testid="stSidebar"] h2 {color:#843A7D;letter-spacing:.03em}
    h1 {font-weight:500!important;letter-spacing:-.03em} h3 {font-weight:400!important}
    [data-testid="stMetric"] {padding:18px;border-radius:18px;background:linear-gradient(120deg,#E83C91,#843A7D);color:white;min-height:140px;box-shadow:0 8px 24px #843a7d16}
    [data-testid="stMetric"] * {color:white!important} [data-testid="stMetricValue"] {font-size:26px!important}
    [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {background:linear-gradient(120deg,#843A7D,#6551bb)}
    [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {background:linear-gradient(120deg,#39bfe8,#6e91d6)}
    [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {background:linear-gradient(120deg,#F7A531,#fa866b)}
    [data-testid="stVerticalBlockBorderWrapper"]>div {border-radius:18px!important;background:white}
    div[class*="st-key-card_"], .st-key-heatcard {background:#FFFFFF;border-radius:18px;box-shadow:0 6px 20px #43334c08} .eyebrow {color:#E83C91;font-size:12px;letter-spacing:.18em;font-weight:500}
    .chip {display:inline-block;background:#f6e8f2;color:#843A7D;padding:5px 12px;margin:3px;border-radius:20px;font-size:13px}
    .stTabs [data-baseweb="tab-list"] {gap:26px;margin-top:18px}
    .stTabs [data-baseweb="tab"] {font-family:'Kanit';font-size:16px}
    </style>''', unsafe_allow_html=True)


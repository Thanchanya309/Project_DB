import streamlit as st
from src.data_loader import DIMS


def reset():
    for dim in DIMS:
        st.session_state['f_' + dim] = []
    st.session_state['revision'] = st.session_state.get('revision', 0) + 1


def selection_update(state, event, dimensions):
    points = event.get('selection', {}).get('points', [])
    if not points:
        return False
    collected = {d: [] for d in dimensions}
    for point in points:
        custom = point.get('customdata')
        if custom is None or len(custom) != len(dimensions):
            continue
        for dim, value in zip(dimensions, custom):
            value = int(value) if dim in ['year','quarter'] else str(value)
            if value not in collected[dim]:
                collected[dim].append(value)
    changed = False
    for dim, values in collected.items():
        if values and state.get('f_' + dim, []) != values:
            state['f_' + dim] = values
            changed = True
    return changed


def chart_callback(key, dimensions):
    if selection_update(st.session_state, st.session_state.get(key, {}), dimensions):
        st.session_state.revision += 1


def sidebar(data):
    st.session_state.setdefault('revision', 0)
    st.sidebar.markdown('## ◈ LABOR\nตลาดแรงงานไทย')
    st.sidebar.caption('ศูนย์วิเคราะห์ข้อมูลแรงงาน')
    schemes = data.scheme.unique().tolist()
    scheme = st.sidebar.selectbox('ชุดนิยามภูมิภาค', schemes, on_change=reset)
    pool = data[data.scheme.eq(scheme)]
    st.sidebar.button('↺ ล้างตัวกรองทั้งหมด', on_click=reset, use_container_width=True)
    names = ['ปี พ.ศ.','ไตรมาส (0 = รายปี)','ภูมิภาค','พื้นที่','เพศ','กลุ่มอายุ']
    for dim, label in zip(DIMS, names):
        st.session_state.setdefault('f_' + dim, [])
        options = sorted(pool[dim].unique().tolist())
        st.sidebar.multiselect(label, options, key='f_' + dim, on_change=bump)
    st.sidebar.info('ไม่เลือกหมวดหมู่ = ใช้ยอดรวมที่มีอยู่จริง\n\nไม่เลือกเวลา = แสดงทุกช่วงเวลา และ KPI ใช้ช่วงล่าสุดที่ตรงเงื่อนไข')
    return pool, {d:st.session_state['f_' + d] for d in DIMS}


def bump():
    st.session_state.revision += 1

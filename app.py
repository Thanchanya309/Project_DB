from html import escape
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import load_data, prepare, DIMS
from src.filters import sidebar
from src.metrics import scalar, LABELS, slice_metric
from src.charts import trend, comparison, scatter, draw
from src.styles import apply_styles

st.set_page_config(page_title='ตลาดแรงงานไทย | Labor Intelligence', page_icon='◈', layout='wide')
apply_styles()

@st.cache_data
def get_data():
    raw = load_data()
    clean, conflicts = prepare(raw)
    return raw, clean, conflicts

try:
    raw, clean, conflicts = get_data()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(str(error))
    st.stop()

# Choose the latest period with the widest coverage of actual national totals.
if 'initialized' not in st.session_state:
    totals = clean[(clean.region == 'รวม') & (clean.area == 'รวม') & (clean.sex == 'รวม') & (clean.age_group == 'รวม') & (clean.scheme == 'ชุดชื่อภูมิภาคเดิม') & (clean.quarter > 0)]
    if not totals.empty:
        best = totals.groupby(['year','quarter']).metric.nunique().reset_index(name='coverage').sort_values(['coverage','year','quarter']).iloc[-1]
        st.session_state.f_year = [int(best.year)]
        st.session_state.f_quarter = [int(best.quarter)]
    st.session_state.initialized = True

data, filters = sidebar(clean)
st.markdown('<div class="eyebrow">THAILAND · LABOR INTELLIGENCE</div>', unsafe_allow_html=True)
st.title('เจาะลึกตลาดแรงงานไทย')
st.caption('สำรวจการมีงานทำ การว่างงาน และความแตกต่างของแรงงาน · ข้อมูล พ.ศ. 2555–2569')
chips = [f'{dim}: {", ".join(map(str,values))}' for dim,values in filters.items() if values]
names = dict(zip(DIMS,['ปี','ไตรมาส','ภูมิภาค','พื้นที่','เพศ','อายุ']))
chips = [f'{names[d]}: {", ".join(map(str,v))}' for d,v in filters.items() if v]
st.markdown(' '.join(f'<span class="chip">{escape(c)}</span>' for c in chips) or '<span class="chip">ยอดรวมที่มีอยู่จริง · ทุกช่วงเวลา</span>', unsafe_allow_html=True)
st.warning('หน่วยและนิยามตัวหารยังไม่มีเอกสารยืนยัน: แสดงค่าต้นฉบับ ไม่รวมหมวดหมู่ ไม่ประมาณค่าที่ขาด และตัดค่าที่ขัดแย้งออก')
cols = st.columns(4)
for col, metric in zip(cols, LABELS):
    value, period = scalar(data, metric, filters)
    with col:
        st.metric(LABELS[metric], f'{value:,.2f}' if value is not None else '—')
        st.caption(f'พ.ศ. {period[0]} · '+('รายปี' if period[1] == 0 else f'ไตรมาส {period[1]}') if period else 'ไม่มีระเบียนเดี่ยวที่ยืนยันได้')

overview, regions, demographics = st.tabs(['◉ ภาพรวมตลาดแรงงานไทย','◇ วิเคราะห์รายภูมิภาค','◎ ความแตกต่างของกลุ่มแรงงาน'])
with overview:
    st.caption('เลือกจุดบนกราฟเพื่อกรองทั้งแดชบอร์ด • ล้างปี/ไตรมาสในแถบซ้ายเพื่อดูแนวโน้มทั้งหมด')
    a,b = st.columns(2)
    with a:
        trend(data,'emp_rate',filters,'employment')
        trend(data,'avg_wage',filters,'wage')
    with b:
        trend(data,'unemp_rate',filters,'unemployment')
        trend(data,'emp_headcount',filters,'headcount')
    with st.container(border=True):
        st.markdown('#### ไตรมาสใดมีอัตราการว่างงานสูงที่สุด?')
        heat = slice_metric(data,'unemp_rate',filters)
        if not heat.empty and not heat.duplicated(['year','quarter']).any():
            grid = heat.pivot(index='year', columns='quarter',values='value')
            fig = px.imshow(grid, color_continuous_scale=['#faf0f5','#E83C91','#843A7D'], labels={'x':'ไตรมาส','y':'ปี พ.ศ.','color':'ค่าต้นฉบับ'},aspect='auto',text_auto='.2f')
            draw(fig,'heat')
            st.caption('ตารางสี: เลือกปีและไตรมาสผ่านแถบซ้าย เพื่อให้กรองข้ามกราฟได้แน่นอน')
        else:
            st.info('ไม่มีข้อมูล หรือมีหลายกลุ่มต่อช่วงเวลา กรุณาเลือกกลุ่มเดียว')

single_period = len(filters['year']) == 1 and len(filters['quarter']) == 1
with regions:
    st.caption('เปรียบเทียบเฉพาะชุดนิยามภูมิภาคที่เลือก ไม่รวมยอดของหลายภูมิภาค')
    if not single_period:
        st.info('กรุณาเลือกปีเดียวและไตรมาสเดียวในแถบซ้ายเพื่อเปรียบเทียบภูมิภาค')
    else:
        a,b = st.columns(2)
        with a:
            comparison(data,'emp_rate',filters,'region','ภูมิภาคใดมีอัตราการมีงานทำสูงที่สุด?','regional_rank')
            scatter(data,'unemp_rate',filters,'wage_unemp','ภูมิภาคใดว่างงานสูง แต่ค่าจ้างต่ำ?')
        with b:
            comparison(data,'unemp_rate',filters,'region','อัตราการว่างงานรายภูมิภาค','regional_unemployment')
            scatter(data,'emp_rate',filters,'wage_emp','การมีงานทำสูง ค่าจ้างสูงตามหรือไม่?')
with demographics:
    if not single_period:
        st.info('กรุณาเลือกปีเดียวและไตรมาสเดียวในแถบซ้ายเพื่อเปรียบเทียบกลุ่มแรงงาน')
    else:
        a,b = st.columns(2)
        with a:
            comparison(data,'avg_wage',filters,'sex','ค่าจ้างชายและหญิงแตกต่างกันอย่างไร?','gender')
            comparison(data,'unemp_rate',filters,'age_group','กลุ่มอายุใดมีอัตราการว่างงานสูงที่สุด?','age_unemployment')
        with b:
            comparison(data,'avg_wage',filters,'age_group','กลุ่มอายุใดมีค่าจ้างเฉลี่ยสูงที่สุด?','age_wage')
            comparison(data,'avg_wage',filters,'area','ค่าจ้างในและนอกเขตเทศบาลต่างกันอย่างไร?','area_wage')

with st.expander('ตรวจสอบข้อมูล · ข้อจำกัด · ดาวน์โหลด'):
    st.write(f'ข้อมูลต้นฉบับ {len(raw):,} แถว · ค่าที่ใช้ได้ {len(clean):,} คีย์ตัวชี้วัด · ค่าขัดแย้งที่ตัดออก {len(conflicts):,} คีย์')
    st.caption('ไม่มี GeoJSON ที่ตรวจสอบแล้ว จึงใช้กราฟแท่งแทนแผนที่ • แถวที่ไม่ระบุพื้นที่ไม่ถูกตีความว่าเป็นพื้นที่รวม • จำนวนผู้มีงานทำไม่รวมข้ามกลุ่มและยังไม่ยืนยันหน่วย')
    st.markdown(open('docs/DATA_AUDIT.md',encoding='utf-8-sig').read())
    selected = pd.concat([slice_metric(data,m,filters) for m in LABELS],ignore_index=True)
    st.dataframe(selected, use_container_width=True, hide_index=True)
    st.download_button('ดาวน์โหลดข้อมูลตามตัวกรอง',selected.to_csv(index=False).encode('utf-8-sig'),'filtered_labor_data.csv','text/csv')
    st.download_button('ดาวน์โหลดคีย์ที่ขัดแย้ง',conflicts.to_csv(index=False).encode('utf-8-sig'),'conflicting_keys.csv','text/csv')
st.caption('แหล่งข้อมูล: final_labor_master_data(1).csv · ไม่ประมาณค่า ไม่รวมอัตรา ไม่สร้างยอดรวมแทนข้อมูลที่ขาด')

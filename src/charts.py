import plotly.express as px
import streamlit as st
from src.filters import chart_callback
from src.metrics import slice_metric, LABELS
COLORS = ['#E83C91','#843A7D','#57C7FF','#F7A531','#b295c8','#43334C']


def draw(fig, key, dims=()):
    fig.update_layout(font={'family':'Kanit, sans-serif','color':'#43334C'}, paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=10,r=15,t=20,b=20), height=320, legend_title_text='', legend=dict(orientation='h', y=-0.28, font_size=10), clickmode='event+select')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#f2edf2', zeroline=False)
    chart_key = f'{key}_{st.session_state.revision}'
    st.plotly_chart(fig, key=chart_key, width='stretch', on_select=(lambda: chart_callback(chart_key, dims)) if dims else 'ignore', selection_mode=('points','box','lasso'), config={'displaylogo':False})


def chart_data(data, metric, filters, vary=()):
    frame = slice_metric(data, metric, filters, vary)
    for dim in vary:
        selected = filters.get(dim, [])
        frame = frame[frame[dim].isin(selected)] if selected else frame[~frame[dim].isin(['รวม','ไม่ระบุ'])]
    return frame


def trend(data, metric, filters, key):
    with st.container(border=True, key=f'card_{key}'):
        st.markdown('#### '+ LABELS[metric] + 'ตามเวลา')
        frame = slice_metric(data, metric, filters)
        if frame.empty:
            st.info('ไม่มีข้อมูลที่เข้ากันได้กับตัวกรอง — ลองระบุภูมิภาค พื้นที่ เพศ หรืออายุ')
            return
        frame['period'] = frame.year.astype(str) + frame.quarter.map(lambda q: ' · รายปี' if q == 0 else f' · Q{q}')
        frame['series'] = frame[['region','area','sex','age_group']].astype(str).agg(' / '.join, axis=1) + frame.quarter.map(lambda q: ' (รายปี)' if q == 0 else ' (รายไตรมาส)')
        fig = px.line(frame, x='period', y='value', color='series', markers=True, custom_data=['year','quarter'], color_discrete_sequence=COLORS, labels={'period':'ช่วงเวลา','value':'ค่าตามต้นฉบับ','series':'กลุ่ม'})
        # connectgaps=False preserves missing values; absent periods are inserted per series.
        periods = frame[['year','quarter','period']].drop_duplicates().sort_values(['year','quarter']).period.tolist()
        for trace in fig.data:
            points = dict(zip(trace.x, zip(trace.y, trace.customdata)))
            trace.x = periods
            trace.y = [points[p][0] if p in points else None for p in periods]
            trace.customdata = [points[p][1] if p in points else [None,None] for p in periods]
            trace.connectgaps = False
        draw(fig, key, ['year','quarter'])
        st.caption('เลือกจุดเพื่อกรองปีและไตรมาส • หน่วยตามต้นฉบับ')


def comparison(data, metric, filters, dimension, title, key):
    with st.container(border=True, key=f'card_{key}'):
        st.markdown('#### '+title)
        frame = chart_data(data, metric, filters, [dimension])
        if frame.empty:
            st.info('ไม่มีข้อมูลที่เข้ากันได้กับตัวกรองนี้')
            return
        fig = px.bar(frame.sort_values('value'), y=dimension, x='value', color=dimension, custom_data=[dimension], orientation='h', color_discrete_sequence=COLORS, labels={dimension:'กลุ่ม','value':'ค่าตามต้นฉบับ'})
        fig.update_layout(showlegend=False)
        draw(fig,key,[dimension])
        st.caption('เลือกแท่งหรือใช้กรอบเลือก เพื่อกรองทุกกราฟที่รองรับ')


def scatter(data, metric, filters, key, title):
    with st.container(border=True, key=f'card_{key}'):
        st.markdown('#### '+title)
        left = chart_data(data, metric, filters, ['region'])
        right = chart_data(data, 'avg_wage', filters, ['region'])
        keys = ['scheme','year','quarter','region','area','sex','age_group']
        frame = left.merge(right, on=keys, suffixes=('_x','_y'))
        if frame.empty:
            st.info('ไม่พบค่าที่จับคู่กันได้บนทุกมิติ')
            return
        fig = px.scatter(frame,x='value_x',y='value_y',color='region',custom_data=['region'],hover_name='region',color_discrete_sequence=COLORS, labels={'value_x':LABELS[metric],'value_y':'ค่าจ้างเฉลี่ย (หน่วยต้นฉบับ)'})
        fig.update_traces(marker_size=16,marker_line_width=2,marker_line_color='white')
        draw(fig,key,['region'])



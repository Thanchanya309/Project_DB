"""โหลดข้อมูลเดิม แยกนิยามภูมิภาคและตัดค่าที่ขัดแย้ง"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DIMS = ['year', 'quarter', 'region', 'area', 'sex', 'age_group']
METRICS = ['avg_wage', 'emp_rate', 'emp_headcount', 'unemp_rate']


def load_data(path=None):
    if path is None:
        files = sorted(ROOT.rglob('*labor*csv'))
        if not files:
            raise FileNotFoundError('ไม่พบ final_labor_master_data.csv หรือไฟล์เทียบเท่า')
        if len(files) != 1:
            raise ValueError('พบไฟล์ข้อมูลหลายไฟล์ กรุณาระบุไฟล์ต้นฉบับให้ชัดเจน')
        path = files[0]
    df = pd.read_csv(path)
    missing = set(DIMS + METRICS) - set(df.columns)
    if missing:
        raise ValueError(f'ขาดคอลัมน์: {sorted(missing)}')
    for col in ['year', 'quarter'] + METRICS:
        df[col] = pd.to_numeric(df[col], errors='raise')
    if df[['year', 'quarter']].isna().any().any() or not df.quarter.isin([0, 1, 2, 3, 4]).all():
        raise ValueError('ปีหรือไตรมาสไม่ถูกต้อง')
    if ((df[METRICS] < 0) | (df[METRICS] == float('inf'))).any().any():
        raise ValueError('พบค่าตัวชี้วัดนอกช่วงที่รองรับ')
    return df


def prepare(raw):
    df = raw.copy()
    # Preserve original region definitions: even apparently synonymous labels are not pooled.
    df['scheme'] = df.region.map(lambda x: 'ชุดเลขนำหน้า 7 ภูมิภาค' if x in ['2) กลาง','3) ใต้','4) ใต้ชายแดน','5) ตะวันออก','6) ตะวันออกเฉียงเหนือ','7) เหนือ'] else ('ชุดเลขนำหน้า 5 ภูมิภาค' if re.match(r'^\d\)', str(x)) else 'ชุดชื่อภูมิภาคเดิม'))
    for col in ['area', 'sex', 'age_group']:
        df[col] = df[col].fillna('ไม่ระบุ').astype(str).str.replace(r'^\d+[.)]\s*', '', regex=True)
        df[col] = df[col].replace({'Total':'รวม','60 ขึ้นไป':'60 ปีขึ้นไป','เขตเทศบาล':'ในเขตเทศบาล'})
    df.region = df.region.replace({'Total':'รวม'})
    keys = ['scheme'] + DIMS
    # Long metric table prevents a missing metric in one row from hiding another source row.
    long = df.melt(id_vars=keys, value_vars=METRICS, var_name='metric', value_name='value').dropna(subset=['value'])
    grouped = long.groupby(keys + ['metric'], dropna=False).value.agg(['nunique','first','size']).reset_index()
    conflicts = grouped[grouped['nunique'] > 1].copy()
    clean = grouped[grouped['nunique'] == 1].rename(columns={'first':'value'}).drop(columns=['nunique','size'])
    return clean, conflicts



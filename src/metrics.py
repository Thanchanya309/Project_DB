"""เปรียบเทียบระเบียนตรงระดับเท่านั้น ไม่บวกยอดรวมหรือเฉลี่ยอัตรา"""
from src.data_loader import DIMS
LABELS = {'avg_wage':'ค่าจ้างเฉลี่ย','emp_rate':'อัตราการมีงานทำ','unemp_rate':'อัตราการว่างงาน','emp_headcount':'จำนวนผู้มีงานทำ'}


def slice_metric(data, metric, filters, vary=()):
    frame = data[data.metric.eq(metric)].copy()
    for dim in DIMS:
        if dim in vary:
            continue
        values = filters.get(dim, [])
        if values:
            frame = frame[frame[dim].isin(values)]
        elif dim in ['region','area','sex','age_group']:
            frame = frame[frame[dim].eq('รวม')]
    # Missing total is deliberately not reconstructed from subgroups.
    return frame.sort_values(['year','quarter','region','sex','age_group'])


def scalar(data, metric, filters):
    frame = slice_metric(data, metric, filters)
    periods = frame[['year','quarter']].drop_duplicates()
    if periods.empty:
        return None, None
    latest = periods.sort_values(['year','quarter']).iloc[-1]
    frame = frame[(frame.year == latest.year) & (frame.quarter == latest.quarter)]
    if len(frame) != 1:
        return None, None
    return float(frame.iloc[0].value), (int(latest.year), int(latest.quarter))

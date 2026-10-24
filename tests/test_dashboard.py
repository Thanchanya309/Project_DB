import unittest
from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest
from src.data_loader import load_data, prepare
from src.metrics import scalar, slice_metric
from src.filters import selection_update


class DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_data()
        cls.data, cls.conflicts = prepare(cls.raw)

    def test_source_and_conflicts(self):
        self.assertEqual(self.raw.shape, (29530,10))
        self.assertEqual(len(self.conflicts),1080)
        keys = ['scheme','year','quarter','region','area','sex','age_group','metric']
        self.assertFalse(self.data.duplicated(keys).any())
        self.assertTrue(self.data.merge(self.conflicts,on=keys).empty)

    def test_no_invented_values(self):
        for metric in self.raw.columns[-4:]:
            self.assertTrue(set(self.data.loc[self.data.metric.eq(metric),'value']).issubset(set(self.raw[metric].dropna())))

    def test_missing_total_is_not_summed(self):
        value, _ = scalar(self.data,'emp_headcount',{'year':[2566],'quarter':[1]})
        self.assertIsNone(value)

    def test_annual_is_wage_only(self):
        self.assertEqual(set(self.raw[self.raw.quarter.eq(0)].dropna(subset=['avg_wage']).columns[-4:-3]), {'avg_wage'})
        self.assertTrue(self.data[self.data.quarter.eq(0)].empty)

    def test_filter_combination(self):
        filters = {'year':[2567],'quarter':[1],'region':['ภาคเหนือ'],'sex':['หญิง'],'area':['ในเขตเทศบาล'],'age_group':['20-24 ปี']}
        for metric in ['avg_wage','emp_rate','unemp_rate','emp_headcount']:
            frame = slice_metric(self.data,metric,filters)
            for dim, values in filters.items():
                self.assertTrue(frame[dim].isin(values).all())

    def test_selection_and_no_loop(self):
        state = {'f_region':[]}
        event = {'selection':{'points':[{'customdata':['ภาคเหนือ']}]}}
        self.assertTrue(selection_update(state,event,['region']))
        self.assertEqual(state['f_region'],['ภาคเหนือ'])
        self.assertFalse(selection_update(state,event,['region']))
        self.assertFalse(selection_update(state,{'selection':{'points':[]}},['region']))

    def test_multi_selection(self):
        state = {}
        event = {'selection':{'points':[{'customdata':[2567,1]},{'customdata':[2567,2]}]}}
        selection_update(state,event,['year','quarter'])
        self.assertEqual(state['f_year'],[2567])
        self.assertEqual(state['f_quarter'],[1,2])


class AppTests(unittest.TestCase):
    def test_app_filters_reset_and_empty(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=60).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric),4)
        # Actual widget rerun, then Reset callback.
        app.sidebar.multiselect[0].set_value([2567]).run()
        app.sidebar.multiselect[1].set_value([1]).run()
        app.sidebar.multiselect[2].set_value(['ภาคเหนือ']).run()
        app.sidebar.multiselect[4].set_value(['หญิง']).run()
        self.assertFalse(app.exception)
        app.sidebar.button[0].click().run()
        self.assertFalse(app.exception)
        for widget in app.sidebar.multiselect:
            self.assertEqual(widget.value,[])
        app.sidebar.selectbox[0].select('ชุดเลขนำหน้า 7 ภูมิภาค').run()
        self.assertFalse(app.exception)


if __name__ == '__main__':
    unittest.main()


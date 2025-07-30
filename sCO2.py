# -*- coding: utf-8 -*-

from tespy.networks import Network
from tespy.components import (
    Sink, Source, Turbine, SimpleHeatExchanger, Merge, Splitter,
    HeatExchanger, CycleCloser, Compressor)
from tespy.connections import Connection, Bus, Ref
import pandas as pd
import numpy as np
from tespy.tools import ExergyAnalysis

import plotly.graph_objects as go

fmt_dict = {
    'E_F': {
        'unit': ' in MW',
        'float': '{:.2f}',
        'factor': 1e6,
    },
    'E_P': {
        'unit': ' in MW',
        'float': '{:.2f}',
        'factor': 1e6,
    },
    'E_D': {
        'unit': ' in MW',
        'float': '{:.2f}',
        'factor': 1e6,
    },
    'E_L': {
        'unit': ' in MW',
        'float': '{:.2f}',
        'factor': 1e6,
    },
    'epsilon': {
        'unit': ' in %',
        'float': '{:.1f}',
        'factor': 1 / 100,
        'markdown_header': 'ε'
    },
    'y_Dk': {
        'unit': ' in %',
        'float': '{:.1f}',
        'factor': 1 / 100
    },
    'y*_Dk': {
        'unit': ' in %',
        'float': '{:.1f}',
        'factor': 1 / 100
    },
    'e_T': {
        'unit': ' in kJ/kg',
        'float': '{:.1f}',
        'factor': 1000
    },
    'e_M': {
        'unit': ' in kJ/kg',
        'float': '{:.1f}',
        'factor': 1000
    },
    'e_PH': {
        'unit': ' in kJ/kg',
        'float': '{:.1f}',
        'factor': 1000
    },
    'E_T': {
        'unit': ' in MW',
        'float': '{:.2f}',
        'factor': 1e6
    },
    'E_M': {
        'unit': ' in MW',
        'float': '{:.2f}',
        'factor': 1e6
    },
    'E_PH': {
        'unit': ' in MW',
        'float': '{:.2f}',
        'factor': 1e6
    },
    'T': {
        'unit': ' in °C',
        'float': '{:.1f}',
        'factor': 1
    },
    'p': {
        'unit': ' in bar',
        'float': '{:.2f}',
        'factor': 1
    },
    'h': {
        'unit': ' in kJ/kg',
        'float': '{:.1f}',
        'factor': 1
    }
}


def result_to_markdown(df, filename, prefix=''):

    for col in df.columns:
        fmt = fmt_dict[col]['float']
        if prefix == 'δ ':
            unit = ' in %'
            df[col] *= 100
        else:
            unit = fmt_dict[col]['unit']
            df[col] /= fmt_dict[col]['factor']
        for row in df.index:
            df.loc[row, col] = str(fmt.format(df.loc[row, col]))
        if 'markdown_header' not in fmt_dict[col]:
            fmt_dict[col]['markdown_header'] = col

        df = df.rename(columns={
            col: prefix + fmt_dict[col]['markdown_header'] + unit
        })
    df.to_markdown(
        filename, disable_numparse=True,
        colalign=['left'] + ['right' for _ in df.columns]
    )


# specification of ambient state
pamb = 1.01325
Tamb = 15


# setting up network
nw = Network(fluids=['CO2'])
nw.set_attr(
    T_unit='C', p_unit='bar', h_unit='kJ / kg', m_unit='kg / s',
    s_unit="kJ / kgK")

# components definition
water_in = Source('Water source')
water_out = Sink('Water sink')

closer = CycleCloser('Cycle closer')

cp1 = Compressor('Compressor 1', fkt_group='CMP')
cp2 = Compressor('Compressor 2', fkt_group='CMP')

rec1 = HeatExchanger('Recuperator 1', fkt_group='REC')
rec2 = HeatExchanger('Recuperator 2', fkt_group='REC')

cooler = SimpleHeatExchanger('Water cooler')
heater = SimpleHeatExchanger('Heater')

turb = Turbine('Turbine')

sp1 = Splitter('Splitter 1', fkt_group='REC')
m1 = Merge('Merge 1', fkt_group='REC')

# connections definition
# power cycle
c1 = Connection(cooler, 'out1', cp1, 'in1', label='1')
c2 = Connection(cp1, 'out1', rec1, 'in2', label='2')
c3 = Connection(rec2, 'out2', heater, 'in1', label='3')

c0 = Connection(heater, 'out1', closer, 'in1', label='0')
c4 = Connection(closer, 'out1', turb, 'in1', label='4')
c5 = Connection(turb, 'out1', rec2, 'in1', label='5')
c6 = Connection(sp1, 'out1', cooler, 'in1', label='6')

c10 = Connection(sp1, 'out2', cp2, 'in1', label='10')
c11 = Connection(cp2, 'out1', m1, 'in2', label='11')
c12 = Connection(rec1, 'out2', m1, 'in1', label='12')
c13 = Connection(m1, 'out1', rec2, 'in2', label='13')

c14 = Connection(rec2, 'out1', rec1, 'in1', label='14')
c15 = Connection(rec1, 'out1', sp1, 'in1', label='15')

# add connections to network
nw.add_conns(c0, c1, c2, c3, c4, c5, c6, c10, c11, c12, c13, c14, c15)

# power bus
power = Bus('total output power')
power.add_comps({'comp': turb, 'char': 0.99 * 0.99, 'base': 'component'},
                {'comp': cp1, 'char': 0.98 * 0.97, 'base': 'bus'},
                {'comp': cp2, 'char': 0.98 * 0.97, 'base': 'bus'})

heat_input_bus = Bus('heat input')
heat_input_bus.add_comps({'comp': heater, 'base': 'bus'})

nw.add_busses(power, heat_input_bus)

# connection parameters
c1.set_attr(T=35, p=75, fluid={'CO2': 1}, m=10)
c2.set_attr(p=258.4)
c3.set_attr(p=257, T=433.63)
c4.set_attr(T=600, p=250)
c5.set_attr(p=77.95)
c6.set_attr(p=75.15, T=128.26)
c11.set_attr(p=257.51)
c14.set_attr(p=76.94, T=269.11)

# component parameters
turb.set_attr(eta_s=0.9)
cp1.set_attr(eta_s=0.85)
cp2.set_attr(eta_s=0.85)
# rec1.set_attr(ttd_u=5)

# solve final state
nw.solve(mode='design')
rec2.set_attr(ttd_l=5)
rec1.set_attr(ttd_l=5)
c11.set_attr(T=Ref(c12, 1, 0))
c3.set_attr(T=None)
c6.set_attr(T=None)
c14.set_attr(T=None)
c1.set_attr(m=None)
power.set_attr(P=-100e6)
nw.solve(mode='design')
# print results to prompt and generate model documentation
nw.print_results()

# carry out exergy analysis
ean = ExergyAnalysis(nw, E_P=[power], E_F=[heat_input_bus])
ean.analyse(pamb=pamb, Tamb=Tamb)

# print exergy analysis results to prompt
ean.print_results()

# generate Grassmann diagram
links, nodes = ean.generate_plotly_sankey_input(
    node_order=[
        'E_F', 'heat input', 'Heater', 'Cycle closer', 'CMP', 'REC',
        'Turbine', 'Water cooler', 'total output power', 'E_P', 'E_L', 'E_D'
    ]
)

# norm values to to E_F
links['value'] = [val / links['value'][0] for val in links['value']]

fig = go.Figure(go.Sankey(
    arrangement="snap",
    textfont={"family": "Linux Libertine O"},
    node={
        "label": nodes,
        'pad': 11,
        'color': 'orange'},
    link=links))
fig.show()

# validation (connections)

df_original_data = pd.read_csv(
    'connection_validation.csv', sep=';', decimal=',', index_col='label'
)

df_tespy = pd.concat(
    # units of exergy are J/kg in TESPy, kJ/kg in original data
    [nw.results['Connection'], ean.connection_data / 1e3], axis=1
)
# make index numeric to match indices
df_tespy.index = pd.to_numeric(df_tespy.index, errors='coerce')
# select available indices
idx = np.intersect1d(df_tespy.index, df_original_data.index)
df_tespy = df_tespy.loc[idx, df_original_data.columns]

df_diff_abs = df_tespy - df_original_data
df_diff_rel = (df_tespy - df_original_data) / df_original_data

result_to_markdown(df_diff_abs, 'connections_delta_absolute', 'Δ ')
result_to_markdown(df_diff_rel, 'connections_delta_relative', 'δ ')

# validation (components, needs re-check)

df_original_data = pd.read_csv(
    'component_validation.csv', sep=';', decimal=',', index_col='label'
)

# use aggregated data, as these include mechanical losses of compressor/turbine
df_tespy = ean.aggregation_data.copy()
# # select available indices
idx = np.intersect1d(df_tespy.index, df_original_data.index)
cols = ['E_F', 'E_P', 'E_D']
# original data in MW
df_tespy = df_tespy.loc[idx, cols] / 1e6
df_original_data = df_original_data.loc[idx, cols]

df_diff_abs = (df_tespy - df_original_data).dropna()
df_diff_rel = ((df_tespy - df_original_data) / df_original_data).dropna()

result_to_markdown(df_diff_abs * 1e6, 'components_delta_absolute', 'Δ ')
result_to_markdown(df_diff_rel, 'components_delta_relative', 'δ ')

# export results

network_result = ean.network_data.to_frame().transpose()

ean.aggregation_data.drop(columns=['group'], inplace=True)
result_to_markdown(ean.aggregation_data, 'components_result')
result_to_markdown(ean.connection_data, 'connections_result')
result_to_markdown(network_result, 'network_result')
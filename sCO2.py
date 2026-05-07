# -*- coding: utf-8 -*-

from tespy.networks import Network
from tespy.components import (
    Sink, Source, Turbine, SimpleHeatExchanger, Merge, Splitter,
    HeatExchanger, CycleCloser, Compressor,
    Motor, Generator, PowerBus, PowerSink, PowerSource
)
from tespy.connections import Connection, PowerConnection, Ref
import pandas as pd
import numpy as np
from exerpy import ExergyAnalysis

# (format string, column header with unit) — all values in display units
_COL_FMT = {
    "T":       ("{:.1f}", "T in °C"),
    "p":       ("{:.2f}", "p in bar"),
    "h":       ("{:.1f}", "h in kJ/kg"),
    "e_T":     ("{:.1f}", "e_T in kJ/kg"),
    "e_M":     ("{:.1f}", "e_M in kJ/kg"),
    "e_PH":    ("{:.1f}", "e_PH in kJ/kg"),
    "E_T":     ("{:.2f}", "E_T in MW"),
    "E_M":     ("{:.2f}", "E_M in MW"),
    "E_PH":    ("{:.2f}", "E_PH in MW"),
    "E_F":     ("{:.2f}", "E_F in MW"),
    "E_P":     ("{:.2f}", "E_P in MW"),
    "E_D":     ("{:.2f}", "E_D in MW"),
    "E_L":     ("{:.2f}", "E_L in MW"),
    "epsilon": ("{:.1f}", "ε in %"),
    "y_Dk":    ("{:.1f}", "y_Dk in %"),
    "y*_Dk":   ("{:.1f}", "y*_Dk in %"),
}


def result_to_markdown(df, filename, prefix=""):
    df = df.copy()
    rename = {}
    for col in df.columns:
        fmt, header = _COL_FMT[col]
        if prefix == "δ ":
            df[col] = (df[col] * 100).apply(fmt.format)
            rename[col] = prefix + col + " in %"
        else:
            df[col] = df[col].apply(fmt.format)
            rename[col] = prefix + header
    df.rename(columns=rename, inplace=True)
    df.to_markdown(filename, disable_numparse=True,
                   colalign=["left"] + ["right"] * len(df.columns))


# specification of ambient state
pamb = 1.01325
Tamb = 15

# ambient state in SI units for exerpy
pamb_Pa = pamb * 1e5
Tamb_K = Tamb + 273.15

# setting up network
nw = Network()
nw.units.set_defaults(
    temperature="°C",
    pressure="bar",
    pressure_difference="bar",
    enthalpy="kJ / kg",
    entropy="kJ / kgK",
    power="MW",
    heat="MW"
)

# components definition
water_in = Source("Water source")
water_out = Sink("Water sink")

closer = CycleCloser("Cycle closer")

cp1 = Compressor("Compressor 1", fkt_group="CMP")
cp2 = Compressor("Compressor 2", fkt_group="CMP")

rec1 = HeatExchanger("Recuperator 1", fkt_group="REC")
rec2 = HeatExchanger("Recuperator 2", fkt_group="REC")

cooler = SimpleHeatExchanger("Water cooler")
heater = SimpleHeatExchanger("Heater")

turb = Turbine("Turbine")

sp1 = Splitter("Splitter 1", fkt_group="REC")
m1 = Merge("Merge 1", fkt_group="REC")

# connections definition
# power cycle
c1 = Connection(cooler, "out1", cp1, "in1", label="01")
c2 = Connection(cp1, "out1", rec1, "in2", label="02")
c3 = Connection(rec2, "out2", heater, "in1", label="03")

c0 = Connection(heater, "out1", closer, "in1", label="00")
c4 = Connection(closer, "out1", turb, "in1", label="04")
c5 = Connection(turb, "out1", rec2, "in1", label="05")
c6 = Connection(sp1, "out1", cooler, "in1", label="06")

c10 = Connection(sp1, "out2", cp2, "in1", label="10")
c11 = Connection(cp2, "out1", m1, "in2", label="11")
c12 = Connection(rec1, "out2", m1, "in1", label="12")
c13 = Connection(m1, "out1", rec2, "in2", label="13")

c14 = Connection(rec2, "out1", rec1, "in1", label="14")
c15 = Connection(rec1, "out1", sp1, "in1", label="15")

# add connections to network
nw.add_conns(c0, c1, c2, c3, c4, c5, c6, c10, c11, c12, c13, c14, c15)

# power system
grid = PowerSink("grid")
distribution = PowerBus("distribution", num_in=1, num_out=3)
motor1 = Motor("motor 1")
motor2 = Motor("motor 2")
generator = Generator("generator")

e1 = PowerConnection(distribution, "power_out3", grid, "power", label="e1")

e2 = PowerConnection(distribution, "power_out1", motor1, "power_in", label="e2")
e3 = PowerConnection(motor1, "power_out", cp1, "power", label="e3")

e4 = PowerConnection(distribution, "power_out2", motor2, "power_in", label="e4")
e5 = PowerConnection(motor2, "power_out", cp2, "power", label="e5")

e6 = PowerConnection(turb, "power", generator, "power_in", label="e6")
e7 = PowerConnection(generator, "power_out", distribution, "power_in1", label="e7")

nw.add_conns(e1, e2, e3, e4, e5, e6, e7)

heatsource = PowerSource("heatsource")
heater.set_attr(power_connector_location="inlet")
h1 = PowerConnection(heatsource, "power", heater, "heat", label="h1")

nw.add_conns(h1)

motor1.set_attr(eta=0.97*0.98)
motor2.set_attr(eta=0.97*0.98)
generator.set_attr(eta=0.99*0.99)

# connection parameters
c1.set_attr(T=35, p=75, fluid={"CO2": 1}, m=10)
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

c1.set_attr(m=None)
e1.set_attr(E=100)

rec2.set_attr(ttd_l=5)
c3.set_attr(T=None)

# solve final state
nw.solve(mode="design")

rec1.set_attr(ttd_l=5)
c14.set_attr(T=None)
c11.set_attr(T=Ref(c12, 1, 0))
c6.set_attr(T=None)

nw.solve(mode="design")
nw.assert_convergence()
nw.print_results()

# carry out exergy analysis
ean = ExergyAnalysis.from_tespy(nw, Tamb_K, pamb_Pa, split_physical_exergy=True)

fuel = {"inputs": ["h1"], "outputs": []}
product = {"inputs": ["e1"], "outputs": []}

ean.analyse(E_F=fuel, E_P=product)
df_components, df_connections, df_power = ean.exergy_results()

# validation (connections)

df_original_data = pd.read_csv(
    "connection_validation.csv", sep=";", decimal=",", index_col="label"
)

df_tespy = df_connections.set_index("Connection").rename(columns={
    "T [°C]": "T", "p [bar]": "p",
    "e^T [kJ/kg]": "e_T", "e^M [kJ/kg]": "e_M",
})
df_tespy.index = pd.to_numeric(df_tespy.index, errors="coerce")
idx = np.intersect1d(df_tespy.index, df_original_data.index)
df_tespy = df_tespy.loc[idx, df_original_data.columns]

df_diff_abs = df_tespy - df_original_data
df_diff_rel = (df_tespy - df_original_data) / df_original_data

result_to_markdown(df_diff_abs, "connections_delta_absolute", "Δ ")
result_to_markdown(df_diff_rel, "connections_delta_relative", "δ ")

# validation (components)

df_original_data = pd.read_csv(
    "component_validation.csv", sep=";", decimal=",", index_col="label"
)

df_tespy = df_components.set_index("Component").rename(columns={
    "E_F [kW]": "E_F", "E_P [kW]": "E_P", "E_D [kW]": "E_D",
}).drop(index="TOT", errors="ignore")
df_tespy[["E_F", "E_P", "E_D"]] /= 1e3  # kW -> MW

# add fkt_group aggregates
df_tespy.loc["CMP", ["E_F", "E_P", "E_D"]] = (
    df_tespy.loc[["Compressor 1", "Compressor 2"], ["E_F", "E_P", "E_D"]].sum()
)
df_tespy.loc["REC", ["E_F", "E_P", "E_D"]] = (
    df_tespy.loc[["Recuperator 1", "Recuperator 2", "Splitter 1", "Merge 1"], ["E_F", "E_P", "E_D"]].sum()
)

cols = ["E_F", "E_P", "E_D"]
idx = np.intersect1d(df_tespy.index, df_original_data.index)
df_tespy = df_tespy.loc[idx, cols]
df_original_data = df_original_data.loc[idx, cols]

df_diff_abs = (df_tespy - df_original_data).dropna()
df_diff_rel = ((df_tespy - df_original_data) / df_original_data).dropna()

result_to_markdown(df_diff_abs, "components_delta_absolute", "Δ ")
result_to_markdown(df_diff_rel, "components_delta_relative", "δ ")

# export results

# connections: specific exergy (kJ/kg) and exergy flow (MW)
df_conn_exp = df_connections.set_index("Connection").copy()
df_conn_exp.index = pd.to_numeric(df_conn_exp.index, errors="coerce")
df_conn_exp["e_PH"] = df_conn_exp["e^PH [kJ/kg]"]
df_conn_exp["e_T"] = df_conn_exp["e^T [kJ/kg]"]
df_conn_exp["e_M"] = df_conn_exp["e^M [kJ/kg]"]
df_conn_exp["E_PH"] = df_conn_exp["m [kg/s]"] * df_conn_exp["e_PH"] / 1e3
df_conn_exp["E_T"] = df_conn_exp["m [kg/s]"] * df_conn_exp["e_T"] / 1e3
df_conn_exp["E_M"] = df_conn_exp["m [kg/s]"] * df_conn_exp["e_M"] / 1e3
result_to_markdown(
    df_conn_exp[["e_PH", "e_T", "e_M", "E_PH", "E_T", "E_M"]],
    "connections_result"
)

# components: E in kW from exerpy -> MW; ε and y already in %
df_comp_exp = df_components.set_index("Component").rename(columns={
    "E_F [kW]": "E_F", "E_P [kW]": "E_P", "E_D [kW]": "E_D",
    "epsilon [%]": "epsilon", "y [%]": "y_Dk", "y* [%]": "y*_Dk",
}).drop(index="TOT", errors="ignore")
df_comp_exp[["E_F", "E_P", "E_D"]] /= 1e3
for agg, members in [
    ("CMP", ["Compressor 1", "Compressor 2"]),
    ("REC", ["Recuperator 1", "Recuperator 2", "Splitter 1", "Merge 1"]),
]:
    df_comp_exp.loc[agg, ["E_F", "E_P", "E_D"]] = (
        df_comp_exp.loc[members, ["E_F", "E_P", "E_D"]].sum()
    )
result_to_markdown(
    df_comp_exp[["E_F", "E_P", "E_D", "epsilon", "y_Dk", "y*_Dk"]],
    "components_result"
)

# network
network_result = pd.DataFrame({
    "E_F": [ean.E_F / 1e6],
    "E_P": [ean.E_P / 1e6],
    "E_D": [ean.E_D / 1e6],
    "E_L": [ean.E_L / 1e6],
    "epsilon": [ean.epsilon * 100],
})
result_to_markdown(network_result, "network_result")

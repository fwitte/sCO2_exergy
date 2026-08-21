# -*- coding: utf-8 -*-
"""Exergy analysis of a supercritical CO2 power cycle.

The model solves in a single solve call, the exergy analysis is carried
out with exerpy. Original data from:

M. Penkuhn, G. Tsatsaronis, Exergoeconomic analyses of different sCO2
cycle configurations, in: The 6th International Symposium - Supercritical
CO2 Power Cycles, 2018.
"""

import numpy as np
import pandas as pd
from fluprodia import FluidPropertyDiagram

from tespy.components import (
    Compressor, CycleCloser, Generator, HeatExchanger, HeatSource, Merge,
    Motor, PowerBus, PowerSink, SimpleHeatExchanger, Splitter, Turbine
)
from tespy.connections import Connection, HeatConnection, PowerConnection, Ref
from tespy.models.template import ModelTemplate
from tespy.networks import Network


class SCO2Model(ModelTemplate):
    """Supercritical CO2 power cycle with recompression and recuperators."""

    # specification of ambient state
    pamb = 1.01325  # bar
    Tamb = 15  # °C

    def _create_network(self):
        self.nw = Network()
        self.nw.units.set_defaults(
            temperature="°C",
            pressure="bar",
            pressure_difference="bar",
            enthalpy="kJ / kg",
            entropy="kJ / kgK",
            power="MW",
            heat="MW"
        )

        # components definition
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
        self.nw.add_conns(c0, c1, c2, c3, c4, c5, c6, c10, c11, c12, c13, c14, c15)

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

        self.nw.add_conns(e1, e2, e3, e4, e5, e6, e7)

        # heat input
        heatsource = HeatSource("heatsource")
        h1 = HeatConnection(heatsource, "heat", heater, "heat", label="h1")

        self.nw.add_conns(h1)

        motor1.set_attr(eta=0.97 * 0.98)
        motor2.set_attr(eta=0.97 * 0.98)
        generator.set_attr(eta=0.99 * 0.99)

        # connection parameters
        c1.set_attr(T=35, p=75, fluid={"CO2": 1})
        c2.set_attr(p=258.4)
        c3.set_attr(p=257)
        c4.set_attr(T=600, p=250)
        c5.set_attr(p=77.95)
        c6.set_attr(p=75.15)
        c11.set_attr(p=257.51, T=Ref(c12, 1, 0))
        c14.set_attr(p=76.94)

        # component parameters
        turb.set_attr(eta_s=0.9)
        cp1.set_attr(eta_s=0.85)
        cp2.set_attr(eta_s=0.85)
        rec1.set_attr(ttd_l=5)
        rec2.set_attr(ttd_l=5)

        # net power output
        e1.set_attr(E=100)

    def _parameter_lookup(self):
        return {
            "net power": ["Connections", "e1", "E"],
            "heat input": ["Connections", "h1", "E"],
            "turbine inlet temperature": ["Connections", "04", "T"],
            "turbine inlet pressure": ["Connections", "04", "p"],
            "compressor inlet temperature": ["Connections", "01", "T"],
            "compressor inlet pressure": ["Connections", "01", "p"],
            "turbine efficiency": ["Components", "Turbine", "eta_s"],
            "thermal efficiency": {"get": self._calc_thermal_efficiency},
        }

    def _calc_thermal_efficiency(self):
        return (
            self.nw.get_conn("e1").E.val_SI
            / self.nw.get_conn("h1").E.val_SI
        )

    def create_diagram(self, fluid_name):
        """Fluid property diagram with isolines suited for the cycle.

        The default isoline range of the base class ends at 200 °C and
        slightly above the critical pressure. The cycle however reaches
        turbine inlet temperatures of 600 °C and pressures of more than
        250 bar, so the temperature range and the pressure isolines are
        extended (including the internal iteration bound p_max, which the
        isotherms and isochores are calculated up to).
        """
        diagram = FluidPropertyDiagram(fluid_name)
        diagram.set_unit_system(self.nw.units)
        diagram.set_isolines_subcritical(-20, 650)
        diagram.set_isolines(
            p=np.array([1, 5, 10, 25, 50, 100, 150, 200, 250, 300])
        )
        diagram.p_max = 300e5
        diagram.calc_isolines()
        return diagram

    def solve_model(self, **kwargs):
        self.solve_model_design(**kwargs)

    def solve_design(self):
        self.nw.solve(mode="design")
        self.nw.assert_convergence()

    def run_exergy_analysis(self):
        from exerpy import ExergyAnalysis
        E_F = {"inputs": ["h1"], "outputs": []}
        E_P = {"inputs": ["e1"], "outputs": []}
        self._ean = ExergyAnalysis.from_tespy(
            self.nw, self.Tamb + 273.15, self.pamb * 1e5
        )
        # the cooler rejects heat to the ambient without a material cooling
        # stream; it is a dissipative component (as in the publication), its
        # exergy input is destroyed rather than delivered as a product
        self._ean.components["Water cooler"].dissipative = True
        self._ean.analyse(E_F=E_F, E_P=E_P)
        return self._ean


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


def _component_frame(df_components, E_F_tot=None, E_D_tot=None):
    """Component results in MW with the electric machines chained into the
    turbomachinery.

    The publication lumps the electric machines into the turbomachinery
    (compressor fuel is electrical power including motor losses, turbine
    product is electrical power after the generator). exerpy resolves
    motors and generator as separate components, so chain them for the
    comparison: E_F from the first component of the chain, E_P from the
    last, E_D as the sum.
    """
    df = df_components.set_index("Component").rename(columns={
        "E_F [kW]": "E_F", "E_P [kW]": "E_P", "E_D [kW]": "E_D",
        "epsilon [%]": "epsilon", "y [%]": "y_Dk", "y* [%]": "y*_Dk",
    }).drop(index="TOT", errors="ignore")
    df[["E_F", "E_P", "E_D"]] /= 1e3  # kW -> MW

    chains = {
        "Compressor 1": ["motor 1", "Compressor 1"],
        "Compressor 2": ["motor 2", "Compressor 2"],
        "Turbine": ["Turbine", "generator"],
    }
    for label, (fuel_comp, prod_comp) in chains.items():
        df.loc[label, "E_D"] = df.loc[[fuel_comp, prod_comp], "E_D"].sum()
        df.loc[label, "E_F"] = df.loc[fuel_comp, "E_F"]
        df.loc[label, "E_P"] = df.loc[prod_comp, "E_P"]
        df.loc[label, "epsilon"] = df.loc[label, "E_P"] / df.loc[label, "E_F"] * 100
        if E_F_tot is not None:
            df.loc[label, "y_Dk"] = df.loc[label, "E_D"] / E_F_tot * 100
        if E_D_tot is not None:
            df.loc[label, "y*_Dk"] = df.loc[label, "E_D"] / E_D_tot * 100
    df.drop(index=["motor 1", "motor 2", "generator"], inplace=True)

    # add fkt_group aggregates
    df.loc["CMP", ["E_F", "E_P", "E_D"]] = (
        df.loc[["Compressor 1", "Compressor 2"], ["E_F", "E_P", "E_D"]].sum()
    )
    df.loc["REC", ["E_F", "E_P", "E_D"]] = (
        df.loc[
            ["Recuperator 1", "Recuperator 2", "Splitter 1", "Merge 1"],
            ["E_F", "E_P", "E_D"]
        ].sum()
    )
    return df


def validate(model):
    """Compare the results against the original publication data."""
    ean = model._ean
    df_components, df_connections, _ = ean.exergy_results(print_results=False)

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

    df_tespy = _component_frame(df_components)

    cols = ["E_F", "E_P", "E_D"]
    idx = np.intersect1d(df_tespy.index, df_original_data.index)
    df_tespy = df_tespy.loc[idx, cols]
    df_original_data = df_original_data.loc[idx, cols]

    df_diff_abs = (df_tespy - df_original_data).dropna()
    df_diff_rel = ((df_tespy - df_original_data) / df_original_data).dropna()

    result_to_markdown(df_diff_abs, "components_delta_absolute", "Δ ")
    result_to_markdown(df_diff_rel, "components_delta_relative", "δ ")

    return df_diff_rel


def export_results(model):
    """Export exergy analysis results to markdown tables."""
    ean = model._ean
    df_components, df_connections, _ = ean.exergy_results(print_results=False)

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

    # components incl. chained aggregates
    df_comp_exp = _component_frame(
        df_components, E_F_tot=ean.E_F / 1e6, E_D_tot=ean.E_D / 1e6
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


def main():
    model = SCO2Model()
    model.solve_design()
    model.nw.print_results()

    model.run_exergy_analysis()
    validate(model)
    export_results(model)


if __name__ == "__main__":
    main()

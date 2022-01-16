# Exergy Analysis of a Supercritical CO<sub>2</sub> Power Cycle in TESPy

Example for the exergy analysis in [TESPy][]. Find more information
about the exergy analysis feature in the respective [online
documentation][].

The supercritical CO<sub>2</sub> power cycle model has the following
topology:

<figure>
<img src="./flowsheet.svg" class="align-center" />
</figure>

Find the model specifications and results in the sCO2.py script and the
corresponding [pdf model report][].

## Usage

Clone the repository and build a new python environment. From the base
directory of the repository run

``` bash
pip install -r ./requirements.txt
```

to install the version requirements for the sCO2.py python script.

The original data of the plant are obtained from the following
publication:

*M. Penkuhn, G. Tsatsaronis, Exergoeconomic analyses of different sCO2
cycle configurations, in: The 6th International Symposium –
Supercritical CO2 Power Cycles, 2018.*

## Valdiation and Results of Exergy Analysis

The tables below show the results of the simulation as well as the
validation results. The original data from the publication are provided
in the .csv files [component_validation.csv][] and
[connection_validation.csv][].

### Connection data

**TESPy simulation**

|    |   e_PH in kJ/kg |   e_T in kJ/kg |   e_M in kJ/kg |   E_PH in MW |   E_T in MW |   E_M in MW |
|:---|----------------:|---------------:|---------------:|-------------:|------------:|------------:|
| 0  |           580.2 |          362.9 |          217.2 |       683.34 |      427.47 |      255.86 |
| 1  |           206.1 |            7.6 |          198.5 |       176.65 |        6.51 |      170.14 |
| 2  |           252.9 |           34.8 |          218.1 |       216.85 |       29.87 |      186.98 |
| 3  |           449.4 |          231.4 |          218.0 |       529.24 |      272.54 |      256.70 |
| 4  |           580.2 |          362.9 |          217.2 |       683.34 |      427.47 |      255.86 |
| 5  |           412.8 |          214.0 |          198.8 |       486.14 |      252.00 |      234.15 |
| 6  |           232.0 |           33.6 |          198.5 |       198.93 |       28.77 |      170.16 |
| 10 |           232.0 |           33.6 |          198.5 |        74.36 |       10.75 |       63.61 |
| 11 |           334.4 |          116.4 |          218.0 |       107.17 |       37.31 |       69.86 |
| 12 |           334.4 |          116.4 |          218.0 |       286.71 |       99.81 |      186.90 |
| 13 |           334.4 |          116.4 |          218.0 |       393.88 |      137.12 |      256.76 |
| 14 |           294.6 |           95.9 |          198.7 |       347.02 |      113.01 |      234.01 |
| 15 |           232.0 |           33.6 |          198.5 |       273.28 |       39.52 |      233.77 |

**Absolute difference in the values Δ**

|    |   Δ T in °C |   Δ p in bar |   Δ e_T in kJ/kg |   Δ e_M in kJ/kg |
|:---|------------:|-------------:|-----------------:|-----------------:|
| 1  |        -0.0 |        -0.00 |             -0.0 |              0.0 |
| 2  |        -0.0 |         0.00 |             -0.0 |              0.0 |
| 3  |         0.1 |         0.00 |              0.0 |              0.0 |
| 4  |         0.0 |         0.00 |              0.0 |              0.0 |
| 5  |         0.2 |        -0.00 |              0.0 |              0.0 |
| 6  |        -0.0 |         0.00 |             -0.0 |             -0.0 |
| 10 |        -0.0 |         0.00 |             -0.0 |             -0.0 |
| 11 |         0.0 |         0.00 |             -0.0 |              0.0 |
| 12 |         0.0 |         0.00 |             -0.0 |              0.0 |
| 13 |         0.0 |         0.00 |             -0.0 |              0.0 |
| 14 |         0.0 |         0.00 |              0.0 |              0.0 |
| 15 |        -0.0 |         0.00 |             -0.0 |             -0.0 |

**Relative deviation in the values δ**

|    |   δ T in % |   δ p in % |   δ e_T in % |   δ e_M in % |
|:---|-----------:|-----------:|-------------:|-------------:|
| 1  |       -0.0 |       -0.0 |         -0.0 |          0.0 |
| 2  |       -0.0 |        0.0 |         -0.0 |          0.0 |
| 3  |        0.0 |        0.0 |          0.1 |          0.0 |
| 4  |        0.0 |        0.0 |          0.1 |          0.0 |
| 5  |        0.0 |       -0.0 |          0.1 |          0.0 |
| 6  |       -0.0 |        0.0 |         -0.0 |         -0.0 |
| 10 |       -0.0 |        0.0 |         -0.0 |         -0.0 |
| 11 |        0.0 |        0.0 |         -0.0 |          0.0 |
| 12 |        0.0 |        0.0 |         -0.0 |          0.0 |
| 13 |        0.0 |        0.0 |         -0.0 |          0.0 |
| 14 |        0.0 |        0.0 |          0.0 |          0.0 |
| 15 |       -0.0 |        0.0 |         -0.0 |         -0.0 |

*Deviation due to differences in fluid property data*

### Component data

**TESPy simulation**

|               |   E_F in MW |   E_P in MW |   E_D in MW |   ε in % |   y_Dk in % |   y*_Dk in % |
|:--------------|------------:|------------:|------------:|---------:|------------:|-------------:|
| Heater        |      154.93 |      154.09 |        0.84 |     99.5 |         0.5 |          1.5 |
| Cycle closer  |         nan |         nan |         nan |      nan |         nan |          nan |
| Water cooler  |       22.28 |         nan |       22.28 |      nan |        14.4 |         40.6 |
| Compressor 1  |       47.49 |       40.20 |        7.29 |     84.6 |         4.7 |         13.3 |
| Recuperator 1 |       73.81 |       69.93 |        3.87 |     94.8 |         2.5 |          7.1 |
| Recuperator 2 |      139.19 |      135.43 |        3.76 |     97.3 |         2.4 |          6.8 |
| Turbine       |      197.19 |      185.07 |       12.12 |     93.9 |         7.8 |         22.1 |
| Splitter 1    |         nan |         nan |         nan |      nan |         nan |          nan |
| Compressor 2  |       37.58 |       32.81 |        4.76 |     87.3 |         3.1 |          8.7 |
| Merge 1       |        0.00 |        0.00 |        0.00 |      0.0 |         0.0 |          0.0 |

**Absolute difference in the values Δ**

|               |   Δ E_F in MW |   Δ E_P in MW |   Δ E_D in MW |
|:--------------|--------------:|--------------:|--------------:|
| Compressor 1  |         -0.11 |         -0.00 |         -0.01 |
| Compressor 2  |         -0.12 |         -0.09 |         -0.04 |
| Heater        |         -3.07 |         -1.01 |         -2.06 |
| Recuperator 1 |         -0.09 |         -0.07 |         -0.03 |
| Recuperator 2 |         -0.01 |          0.03 |         -0.04 |
| Turbine       |         -0.21 |         -0.23 |         -0.08 |

**Relative deviation in the values δ**

|               |   δ E_F in % |   δ E_P in % |   δ E_D in % |
|:--------------|-------------:|-------------:|-------------:|
| Compressor 1  |        -0.23 |        -0.00 |        -0.09 |
| Compressor 2  |        -0.33 |        -0.26 |        -0.75 |
| Heater        |        -1.94 |        -0.65 |       -71.11 |
| Recuperator 1 |        -0.12 |        -0.09 |        -0.65 |
| Recuperator 2 |        -0.01 |         0.02 |        -0.99 |
| Turbine       |        -0.11 |        -0.12 |        -0.63 |

*High deviation due to differences in component exergy balances*

### Network data (results only)

|   E_F in MW |   E_P in MW |   E_D in MW |   E_L in MW |   ε in % |
|------------:|------------:|------------:|------------:|---------:|
|      154.93 |      100.00 |       54.93 |        0.00 |     64.5 |

## Citation

The state of this repository is archived via zenodo. If you are using the
TESPy model within your own research, you can refer to this model via the
zenodo doi: [10.5281/zenodo.4751796][].

## MIT License

Copyright (c) 2022 Francesco Witte, Julius Meier, Ilja Tuschy,
Mathias Hofmann

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


  [TESPy]: https://github.com/oemof/tespy
  [online documentation]: https://tespy.readthedocs.io/
  [pdf model report]: sCO2_model_report.pdf
  [component_validation.csv]: component_validation.csv
  [connection_validation.csv]: connection_validation.csv
  [10.5281/zenodo.4751796]: https://zenodo.org/record/4751796
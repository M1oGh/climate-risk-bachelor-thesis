from math import ceil, floor

import pandas as pd
import pyam
import wbdata as wb
from matplotlib import pyplot as plt

import crisk2.connections.limits_connection
import crisk2.tools.calculator as cc
from crisk2.connections.iiasa_connection import IIASAConnection


ic = IIASAConnection()
print(ic.get_scenarios())

"""
model = "GCAM"
scenario = "LIMITS-RefPol-500"
region = "AFRICA"
var = ["Secondary Energy", "Secondary Energy|Electricity"]
rr = "Range Rover"

path = "C:\\Users\\henri\\PycharmProjects\\bachelor-project-2\\crisk2\\tools\\loans_csv.csv"

df1 = cc.get_shocks(model, scenario, 2030, path, 0, 1)
df1.sort_values(by=["amount", "region"], ascending=False, inplace=True)
df2 = cc.get_shocks(model, scenario, 2070, path, 0, 1)
df2.sort_values(by=["amount", "region"], ascending=False, inplace=True)
df1["shock"] = df1["shock"].astype(int)
df2["shock"] = df2["shock"].astype(int)

# df1.sort_values(by="shock", ascending=False, inplace=True)
# df2.sort_values(by="amount", ascending=False, inplace=True)
df1["later"] = df2["shock"]
df1.sort_values(by="shock", ascending=False, inplace=True)
df1 = df1.head(15)
df1.rename(
    columns={
        "amount": "Wert",
        "shock": "Schock 2030",
        "later": "Schock 2070",
        "region": "Region",
    },
    inplace=True,
)
df1["sector"] = df1["sector"].str.replace("Secondary Energy|Electricity", "S")
df1["sector"] = df1["sector"].str.replace("Primary Energy", "P")
df1["key"] = df1["Region"] + "|" + df1["sector"]
df1.set_index("key", inplace=True)

df1.plot(kind="bar")
plt.tight_layout()

plt.show()

# topdf1.set_index("key", inplace=True)
# topdf1.plot(kind="bar", xlabel="region sector")
# plt.show()
"""

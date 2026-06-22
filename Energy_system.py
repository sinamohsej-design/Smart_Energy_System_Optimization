



from pulp import *
import numpy as np
import matplotlib.pyplot as plt


# 1. DATA


hours = range(24)

demand = [2.5, 2.3, 2.2, 2.1, 2.0, 2.2,2.8, 3.5, 4.0, 4.2, 4.5, 4.8,5.0, 4.8, 4.5, 4.2, 4.0, 4.5,5.2, 5.5, 5.0, 4.2, 3.5, 3.0]

pv = [0, 0, 0, 0, 0, 0,
    0.5, 1.5, 3.0, 4.5, 5.5, 6.0,
    6.5, 6.0, 5.0, 4.0, 2.5, 1.0,
    0.2, 0, 0, 0, 0, 0]

price_import = [0.12, 0.12, 0.11, 0.11, 0.11, 0.12,
    0.15, 0.18, 0.20, 0.22, 0.24, 0.25,
    0.25, 0.24, 0.22, 0.20, 0.21, 0.24,
    0.30, 0.32, 0.28, 0.22, 0.18, 0.15]

price_export = [0.08] * 24

co2_factor = 0.4


# 2. BATTERY PARAMETERS


battery_capacity = 10
soc_initial = 5
charge_limit = 3
discharge_limit = 3
efficiency = 0.95


# 3. MODEL


model = LpProblem("Smart_Energy_System", LpMinimize)


# 4. VARIABLES


grid_import = LpVariable.dicts("GridImport", hours, lowBound=0)
grid_export = LpVariable.dicts("GridExport", hours, lowBound=0)

charge = LpVariable.dicts("Charge", hours, lowBound=0, upBound=charge_limit)
discharge = LpVariable.dicts("Discharge", hours, lowBound=0, upBound=discharge_limit)

soc = LpVariable.dicts("SOC", hours, lowBound=0, upBound=battery_capacity)


# 5. OBJECTIVE FUNCTION


model += lpSum([price_import[t] * grid_import[t]- price_export[t] * grid_export[t]for t in hours])


# 6. CONSTRAINTS


for t in hours:

    # Energy balance
    model += (pv[t]+ grid_import[t]+ discharge[t]==demand[t]+ charge[t]+ grid_export[t])

    # Battery SOC dynamics
    if t == 0:
        model += soc[t] == soc_initial + efficiency * charge[t] - discharge[t] / efficiency
    else:
        model += soc[t] == soc[t-1] + efficiency * charge[t] - discharge[t] / efficiency


# 7. SOLVE


model.solve()


# 8. RESULTS EXTRACTION


grid_import_val = [value(grid_import[t]) for t in hours]
grid_export_val = [value(grid_export[t]) for t in hours]
charge_val = [value(charge[t]) for t in hours]
discharge_val = [value(discharge[t]) for t in hours]
soc_val = [value(soc[t]) for t in hours]


# 9. results


total_cost = value(model.objective)
total_import = sum(grid_import_val)
co2_emissions_total = total_import * co2_factor

print("\n===== RESULTS =====")
print("Total Cost:", total_cost)
print("Grid Import:", total_import)
print("CO2 Emissions (Total):", co2_emissions_total)


# 10. CO2 HOURLY CALCULATION 


co2_hourly = [grid_import_val[t] * co2_factor for t in hours]


# 11. PLOTS(show graphically)


x = list(hours)

## 1. Demand vs PV
plt.figure()
plt.plot(x, demand, label="Demand")
plt.plot(x, pv, label="PV")
plt.legend()
plt.title("Demand vs PV")
plt.show()

## 2. Battery State of charge
plt.figure()
plt.plot(x, soc_val)
plt.title("Battery SOC")
plt.show()

## 3. Grid interaction
plt.figure()
plt.bar(x, grid_import_val, label="Import")
plt.bar(x, [-g for g in grid_export_val], label="Export")
plt.legend()
plt.title("Grid Interaction")
plt.show()

## 4. CO2 EMISSIONS 
plt.figure()
plt.plot(x, co2_hourly, marker='o')
plt.title("Hourly CO2 Emissions")
plt.xlabel("Hour")
plt.ylabel("CO2 (kg)")
plt.grid()
plt.show()

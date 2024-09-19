"""
Task3, Lab2, Modelado Simulacion y optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""

from pyomo.environ import *
import pandas as pd

model = ConcreteModel()

# Carga de datos
installation_costs = pd.read_csv('data/installation_costs.csv')
communication_costs = pd.read_csv('data/communication_costs.csv')
energy_consumption = pd.read_csv('data/energy_consumption.csv')
sensor_coverage = pd.read_csv('data/sensor_coverage.csv')

# Transformar datos en diccionarios
installation_costs = dict(zip(installation_costs['Location'], installation_costs['InstallationCost']))
energy_consumption = dict(zip(energy_consumption['SensorType'], energy_consumption['EnergyConsumption']))
communication_costs = (
    communication_costs.groupby('Location')
    .apply(lambda x: dict(zip(x['SensorType'], x['CommunicationCost'])))
    .to_dict()
)

# Transformar sensor_coverage para crear el parámetro delta
sensor_coverage = sensor_coverage.set_index('Location').T.to_dict()
delta = {(l, s): sensor_coverage[l].get(s, 0) for l in sensor_coverage for s in sensor_coverage[l]}

# Adjacencias
Adj = {
    'L1': {'L1', 'L2', 'L3', 'L5'},
    'L2': {'L2', 'L1', 'L5'},
    'L3': {'L3', 'L1', 'L5', 'L4', 'L6', 'L8', 'L7'},
    'L4': {'L4', 'L3', 'L5', 'L6', 'L11'},
    'L5': {'L5', 'L1', 'L2', 'L3', 'L4', 'L11', 'L10'},
    'L6': {'L6', 'L3', 'L4', 'L8', 'L11'},
    'L7': {'L7', 'L3', 'L8', 'L12'},
    'L8': {'L8', 'L7', 'L6', 'L3', 'L11', 'L9', 'L12'},
    'L9': {'L9', 'L10', 'L11', 'L8', 'L12'},
    'L10': {'L10', 'L5', 'L11', 'L9'},
    'L11': {'L11', 'L5', 'L4', 'L6', 'L8', 'L9', 'L10'},
    'L12': {'L12', 'L7', 'L8', 'L9'}
}

# Conjuntos
model.L = Set(initialize=sorted(installation_costs.keys()))  
model.S = Set(initialize=sorted(energy_consumption.keys()))

# Parámetros
model.installation_costs = Param(model.L, initialize=installation_costs)
model.energy_consumption = Param(model.S, initialize=energy_consumption)
model.communication_costs = Param(model.L, model.S, initialize=lambda model, l, s: communication_costs[l][s])
model.delta = Param(model.L, model.S, initialize=lambda model, l, s: delta[(l, s)])

# Variables de decisión
model.x = Var(model.L, model.S, within=Binary)

# Función objetivo
def objective_rule(model):
    return sum((model.installation_costs[l] + model.energy_consumption[s] + model.communication_costs[l, s]) * model.x[l, s] for l in model.L for s in model.S)
model.Objective = Objective(rule=objective_rule, sense=minimize)

# Restricción de cobertura
def sensor_need_rule(model, l, s):
    return sum(model.x[k, s] * model.delta[l, s] for k in Adj[l].union({l})) >= model.delta[l, s]
model.Sensor_Need_Constraint = Constraint(model.L, model.S, rule=sensor_need_rule)

# Resolución del modelo
solver = SolverFactory('glpk')
solver.solve(model)
model.display()

def print_results(model):
    print("Resultados de la Optimización de la Colocación de Sensores:")
    for l in model.L:
        any_sensor_installed = False
        for s in model.S:
            if model.x[l, s].value == 1:
                print(f"Localización {l}:")
                print(f"   Sensor {s} instalado.")
    print(f"\nCosto total de la solución: {model.Objective.expr()}")

print_results(model)

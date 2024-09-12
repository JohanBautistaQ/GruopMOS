"""
Task1, Lab2, Modelado Simulacion y optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""

from pyomo.environ import *
import pandas as pd

model = ConcreteModel()

#carga de datos

installation_costs = pd.read_csv('data/installation_costs.csv')
communication_costs = pd.read_csv('data/communication_costs.csv')
energy_consumption = pd.read_csv('data/energy_consumption.csv')
sensor_coverage = pd.read_csv('data/sensor_coverage.csv')

#transform to dicc

installation_costs = dict(zip(installation_costs['Location'], installation_costs['InstallationCost']))
energy_consumption = dict(zip(energy_consumption['SensorType'], energy_consumption['EnergyConsumption']))

locations = set(['L1', 'L11', 'L4', 'L5', 'L7', 'L2', 'L10', 'L12', 'L3', 'L9', 'L6', 'L8'])
sensors = set(['S1','S2','S3'])

communication_costs = communication_costs.groupby('Location').apply(
    lambda x: dict(zip(x['SensorType'], x['CommunicationCost']))
).to_dict()

sensor_coverage = sensor_coverage.set_index('Location').T.to_dict()

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
    'L11': {'L11', 'L5', 'L4', 'L6', 'L8', 'L9', '10'},
    'L12': {'L12', 'L7', 'L8', 'L9'}
}

"""print('locations:')
print(locations)
print('Sensors:')
print(sensors)
print('Installation costs:')
print(installation_costs)
print('Energy consumption:')
print(energy_consumption)
print('Communication cost:')
print(communication_costs)
print('Sensor coverage:')
print(sensor_coverage)
print('Matriz de adjacency:')
print(Adj)
"""
# Conjuntos
model.L = Set(initialize=sorted(locations))  # Usamos 'sorted' para evitar problemas de orden no determinístico
model.S = Set(initialize=sorted(sensors))

# Parámetros
model.installation_costs = Param(model.L, initialize=installation_costs)
model.energy_consumption = Param(model.S, initialize=energy_consumption)

# Dado que communication_costs es un diccionario de diccionarios, necesitamos una forma de acceder a los valores correctamente
def get_comm_cost(model, l, s):
    return communication_costs[l][s]
model.communication_costs = Param(model.L, model.S, initialize=get_comm_cost)

# De manera similar para sensor_coverage
def get_sensor_cov(model, l, s):
    return sensor_coverage[l][s]
model.sensor_coverage = Param(model.L, model.S, initialize=get_sensor_cov)

# Variables de decisión
model.x = Var(model.L, model.S, within=Binary)
model.y = Var(model.L, within=Binary)

# Función objetivo
def objective_rule(model):
    return sum(model.installation_costs[l] * model.y[l] for l in model.L) + \
           sum((model.energy_consumption[s] + model.communication_costs[l, s]) * model.x[l, s] 
               for l in model.L for s in model.S)
model.Objective = Objective(rule=objective_rule, sense=minimize)

# Restricciones
def coverage_constraint(model, l, s):
    return model.x[l, s] <= model.sensor_coverage[l, s]
model.Coverage_Constraint = Constraint(model.L, model.S, rule=coverage_constraint)

def locality_coverage_rule(model, l):
    return sum(model.x[k, s] for k in Adj[l] for s in model.S if k in model.L) >= 1
model.Locality_Coverage_Constraint = Constraint(model.L, rule=locality_coverage_rule)

def xy_link_rule(model, l):
    return model.y[l] >= sum(model.x[l, s] for s in model.S)
model.XY_Link_Constraint = Constraint(model.L, rule=xy_link_rule)

def installation_limit_rule(model, l):
    return sum(model.x[l, s] for s in model.S) <= 1
model.Installation_Limit_Constraint = Constraint(model.L, rule=installation_limit_rule)

solver = SolverFactory('glpk')
solver.solve(model)
# Resultados
for l in model.L:
    print(f'Location {l}: Sensor Installed? {int(model.y[l].value)}')
    for s in model.S:
        if model.x[l, s].value == 1:
            print(f'   Sensor Type {s} Installed')
            
model.display()
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

locations = pd.read_csv('data/locations.csv')
sensors = pd.read_csv('data/sensors.csv')  
installation_costs = pd.read_csv('data/installation_costs.csv')
communication_costs = pd.read_csv('data/communication_costs.csv')
energy_consumption = pd.read_csv('data/energy_consumption.csv')
sensor_coverage = pd.read_csv('data/sensor_coverage.csv')

#transform to dicc

installation_costs = dict(zip(installation_costs['Location'], installation_costs['InstallationCost']))
energy_consumption = dict(zip(energy_consumption['SensorType'], energy_consumption['EnergyConsumption']))

locations = set(locations.columns)
sensors = set(sensors.columns)

communication_costs = communication_costs.groupby('Location').apply(
    lambda x: dict(zip(x['SensorType'], x['CommunicationCost']))
).to_dict()

sensor_coverage = sensor_coverage.set_index('Location').T.to_dict()

# Matriz de adyacentes
Adj = {
    'L1': set('L2','L3','L5'),
    'L2': set('L1', 'L5'),
    'L3': set('L1', 'L5','L4','L6','L8','L7'),
    'L4': set('L3', 'L5', 'L6','L11'),  
    'L5': set('L1', 'L2', 'L3', 'L4','L11','L10'),
    'L6': set('L3', 'L4', 'L8', 'L11'),   
    'L7': set('L3', 'L8', '12'),
    
    'L8': set('L7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1'),
    'L9': set('L8', 'L7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1'),
    'L10': set('L9', 'L8', 'L7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1'),
    'L11': set('L10', 'L9', 'L8', 'L7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1'),
    'L12': set('L1')
}

print('locations:')
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
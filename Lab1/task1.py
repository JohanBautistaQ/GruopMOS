"""
Task1, Lab1, Modelado Simulacion y optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""

from pyomo.environ import *

"""
Priority : priority in numbers

Maxima:     7
Alta:       6
Media alta: 5
Media:      4
Media baja: 3
Baja:       2
Minima:     1
"""

tasks = {1: (5,7), 
         2: (3,5), 
         3: (13,6), 
         4: (1,3), 
         5:(21,1), 
         6: (2,4), 
         7: (2,6), 
         8: (5,4), 
         9: (8,2), 
         10: (13,7), 
         11:(21,6)
}

model = ConcreteModel()

#Indice T 
model.T = RangeSet(len(tasks))

#Variable de desicion
model.x = Var(model.T, within=Binary)

#Funcion Objetivo
model.objective = Objective(expr=sum(model.x[t]*tasks[t][1] for t in model.T), sense=maximize)

#Restriccion
model.constraint = Constraint(expr=sum(model.x[t]*tasks[t][0] for t in model.T) <= 94)

solver = SolverFactory('glpk')
result = solver.solve(model)

for t in model.T:
    if model.x[t].value > 0:
        print(f"Task {t} yes")
    else:
        print(f"Task {t} no")
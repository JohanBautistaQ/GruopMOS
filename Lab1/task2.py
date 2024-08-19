"""
Task2, Lab1, Modelado Simulacion y optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""

from pyomo.environ import *

"""workers = {trabajador : horas}"""
workers = {
    1: 8,
    2: 10,
    3: 6
}
"""tasks = {tarea: (ganancia, tiempo)}"""
tasks = {
    1: (50,4),
    2: (60,5),
    3: (40,3),
    4: (70,6),
    5: (30,2)
}

model = ConcreteModel()

# Indice T para las tareas
model.T = RangeSet(len(tasks))

# Indice W para los trabajadores
model.W = RangeSet(len(workers))

# Variable de desicion
model.x = Var(model.T, model.W, within=Binary)

# Funcion Objetivo
model.objective = Objective(expr=sum(model.x[t,w]*tasks[t][0] for t in model.T for w in model.W), sense=maximize)

# Restriccion 1: Una tarea debe ser asignada una unica vez
model.constraint1 = ConstraintList()
for t in model.T:
    model.constraint1.add(sum(model.x[t,w] for w in model.W) <= 1)
    
#restriccion 2: Horas del trabajador
model.constraint2 = ConstraintList()
for w in model.W:
    model.constraint2.add(sum(model.x[t,w]*tasks[t][1] for t in model.T)<=workers[w])

solver = SolverFactory('glpk')
result = solver.solve(model)

for t in model.T:
    print(f"Tarea {t}:")
    for w in model.W:
        if model.x[t,w].value == 1:
            print(f"Seleccionada por trabajador {w}")
    if all(model.x[t,w].value == 0 for w in model.W):
        print("No seleccionada")
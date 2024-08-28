"""
Task3, Lab1, Modelado Simulacion y optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""

from pyomo.environ import *

"""recursos = {recurso: (Valor, Peso, Volumen)}"""
recursos = {
    1: (50,15,8),
    2: (100,5,2),
    3: (120,20,10),
    4: (60,18,12),
    5: (40,10,6),
}

"""aviones : {avion: (Capacidad Peso, Capacidad Volumen)}"""
aviones = {
    1: (30,25),
    2: (40,30),
    3: (50,35)
}

model = ConcreteModel()

# Indice R para los recursos
model.R = RangeSet(len(recursos))

# Indice A para los aviones
model.A = RangeSet(len(aviones))

# Variable de desicion
model.x = Var(model.A, model.R, within=Binary)

# Funcion Objetivo
model.objetive = Objective(expr=sum(model.x[a,r]*recursos[r][0] for a in model.A for r in model.R),sense=maximize)

# Restriccion 1: No se puede exceder la capacidad de Peso del avion a 
model.constraint1 = ConstraintList()
for a in model.A:
    model.constraint1.add(sum(model.x[a,r]*recursos[r][1] for r in model.R) <= aviones[a][0])
    
# Restriccion 2: No se puede exceder la capacidad volumetrica del avion a 
model.constraint2 = ConstraintList()
for a in model.A:
    model.constraint2.add(sum(model.x[a,r]*recursos[r][2] for r in model.R) <= aviones[a][1])
    
# Restriccion 3: No puede haber medicinas en el avion 1
model.constraint3 = Constraint(
    expr=model.x[1,2]<= 0
)
"""r = 2 medicinas y a = 1 avion 1"""

#restriccion 4: No puede haber equipos medicos y agua potable en el mismo avion 
model.constraint4 = ConstraintList()
for a in model.A:
    model.constraint4.add(model.x[a,3] +model.x[a,4]<= 1)  # agua potable y equipos medicos
"""r = 3 equipos medicos y 4 agua potable"""


# Restriccion 5: Un recurso puede ser asignado una unica vez
model.constraint5 = ConstraintList()
for r in model.R:
    model.constraint5.add(sum(model.x[a,r] for a in model.A) <= 1)

solver = SolverFactory('glpk')
result = solver.solve(model)

model.display()

import matplotlib.pyplot as plt

# Lista de aviones
P = list(model.A) 

# Valores de los recursos
resources = list(recursos.keys())  # IDs de los recursos
values = [recursos[r][0] for r in resources]  # Valor de cada recurso

# Estado de selección para cada avión
selected = [[model.x[p, r].value for r in resources] for p in P]

colors = ['red', 'blue', 'green']  
plt.figure(figsize=(10, 6))

for i, p in enumerate(P):
    plt.bar(
        [f"Recurso {r}" for r in resources], 
        [v * sel for v, sel in zip(values, selected[i])],  # Multiplica el valor por el estado de selección
        color=colors[i],
        label=f'Avión {p}',
        bottom=[sum(selected[k][r] * values[r] for k in range(i)) for r in range(len(resources))]
    )

plt.xlabel("Recursos")
plt.ylabel("Valor")
plt.title("Asignación de recursos a aviones")

plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.show()
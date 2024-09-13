"""
Task1, Lab2, Modelado Simulacion y optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""

from pyomo.environ import *

model = ConcreteModel()
#Conjuntos
model.productores = Set(initialize=["Bogota", "Medellin"])
model.consumidores = Set(initialize=["Cali", "Barranquilla", "Pasto", "Tunja", "Chia", "Manizales"])

#Parameters 
Oferta = {"Bogota": 550, 
          "Medellin":700}
demanda = {"Cali":125, 
           "Barranquilla":175, 
           "Pasto":225,
           "Tunja":250, 
           "Chia": 225,
           "Manizales": 200}

"""c_pc: costo de transportar del productor p al consumidor c"""
costos = {"Bogota": {"Cali":9999, 
           "Barranquilla":2.5, 
           "Pasto":1.6,
           "Tunja":1.4, 
           "Chia": 0.8,
           "Manizales": 1.4},
          "Medellin": {"Cali":2.5, 
           "Barranquilla":9999, 
           "Pasto":2.0,
           "Tunja":1.0, 
           "Chia": 1.0,
           "Manizales": 0.8}}


# Variables de decision
model.x = Var(model.productores, model.consumidores, domain=NonNegativeReals)

# Funcion objetivo
model.obj = Objective(expr=sum(model.x[p, c]*costos[p][c] for p in model.productores for c in model.consumidores), sense=minimize)

# Restricciones
def enviado_equals_to_oferta(model, p):
    return sum(model.x[p, c] for c in model.consumidores) <= Oferta[p]
    
def recibido_equals_to_demanda(model, c):
    return sum(model.x[p, c] for p in model.productores) == demanda[c]

#TODO: Verificar que esta restriccion sea necesaria o no, ya que la oferta > demanda 
model.enviado_equals_to_oferta = Constraint(model.productores, rule=enviado_equals_to_oferta)
model.recibido_equals_to_demanda = Constraint(model.consumidores, rule=recibido_equals_to_demanda)

solver = SolverFactory('glpk')
results = solver.solve(model)

print("Costo mínimo:", value(model.obj))
for p in model.productores:
    for c in model.consumidores:
        if model.x[p, c].value > 0:
            print(f"Transportar {model.x[p, c].value} toneladas de {p} a {c} con costo {costos[p][c]}")
            
            
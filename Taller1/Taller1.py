"""
Task1, Taller1, Modelado Simulacion y optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""
from pyomo.environ import *

precio = {'C': 3000, 'A': 1000, 'L': 600, 'P': 700}
nutrient_values = {
    'calorias': {'C': 287, 'A': 204, 'L': 146, 'P': 245},
    'proteinas': {'C': 26, 'A': 4.2, 'L': 8, 'P': 6},
    'grasas': {'C': 19.3, 'A': 0.5, 'L': 8, 'P': 0.8},
    'azucares': {'C': 0, 'A': 0.01, 'L': 13, 'P': 25},
    'carbohidratos': {'C': 0, 'A': 44.1, 'L': 11, 'P': 55}
}
Max_Min = {'caloria': 1500, 'proteina': 63, 'grasa': 50, 'azucar': 25, 'carbohidrato': 200}

# Multiplicadores: 1 para >=, -1 para <= 
multipliers = {'caloria': 1, 'proteina': 1, 'grasa': -1, 'azucar': -1, 'carbohidrato': -1}


model = ConcreteModel()

# Conjuntos
model.Foods = Set(initialize=['C', 'A', 'L', 'P'])  
model.Nutrients = Set(initialize=['caloria', 'proteina', 'grasa', 'azucar', 'carbohidrato'])

# Variable de decisión 
model.x = Var(model.Foods, domain=NonNegativeReals)

# Función objetivo: minimizar el costo total
model.obj = Objective(expr=sum(precio[f] * model.x[f] for f in model.Foods), sense=minimize)

# Restriccion
model.nutrient_constraints = ConstraintList()
for n in model.Nutrients:
    model.nutrient_constraints.add(
        multipliers[n] * sum(nutrient_values[n][f] * model.x[f] for f in model.Foods) >= 
        multipliers[n] * Max_Min[n]
    )

solver = SolverFactory('glpk')
results = solver.solve(model)

print("Costo mínimo:", value(model.obj))
for food in model.Foods:
    print(f"Cantidad de {food}:", value(model.x[food]))

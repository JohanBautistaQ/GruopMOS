"""
Task2, Lab2, Modelado Simulación y optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""

from pyomo.environ import *
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Cargar la matriz de distancias directamente sin función separada
matriz_distancias = pd.read_csv('data/proof_case.csv', header=0).values
print(matriz_distancias)

# Crear el modelo
modelo = ConcreteModel()

# Parámetros básicos
num_localidades = len(matriz_distancias)
num_equipos = 3
localidad_origen = 0  # Localidad de origen

# Definir conjuntos en Pyomo
modelo.equipos = RangeSet(1, num_equipos)
modelo.localidades = RangeSet(0, num_localidades - 1)

# Parametrizar las distancias entre localidades
modelo.distancias = Param(modelo.localidades, modelo.localidades, initialize=lambda modelo, i, j: matriz_distancias[i][j])

# Variables de decisión: x[e, i, j] = 1 si el equipo e viaja de i a j
modelo.x = Var(modelo.equipos, modelo.localidades, modelo.localidades, domain=Binary)

# Función objetivo: minimizar la distancia total recorrida
modelo.objetivo = Objective(
    expr=sum(modelo.distancias[i, j] * modelo.x[e, i, j] for e in modelo.equipos for i in modelo.localidades for j in modelo.localidades),
    sense=minimize
)

# Restricción: cada equipo debe salir de la localidad de origen
modelo.salida_origen = Constraint(modelo.equipos, rule=lambda modelo, e: sum(modelo.x[e, localidad_origen, j] for j in modelo.localidades if j != localidad_origen) == 1)

# Restricción: cada equipo debe regresar a la localidad de origen
modelo.regreso_origen = Constraint(modelo.equipos, rule=lambda modelo, e: sum(modelo.x[e, i, localidad_origen] for i in modelo.localidades if i != localidad_origen) == 1)

# Restricción: cada localidad debe ser visitada exactamente una vez por algún equipo
def regla_visita_unica(modelo, i):
    if i != localidad_origen:
        return sum(modelo.x[e, i, j] for e in modelo.equipos for j in modelo.localidades if j != i) == 1
    return Constraint.Skip
modelo.visita_unica = Constraint(modelo.localidades, rule=regla_visita_unica)

# Restricción de continuidad (lo que entra debe salir de una localidad)
def regla_continua(modelo, e, i):
    if i != localidad_origen:
        return sum(modelo.x[e, i, j] for j in modelo.localidades if j != i) == sum(modelo.x[e, j, i] for j in modelo.localidades if j != i)
    return Constraint.Skip
modelo.continua = Constraint(modelo.equipos, modelo.localidades, rule=regla_continua)

# Restricción MTZ para evitar subtours (eliminación de subtours)
modelo.u = Var(modelo.equipos, modelo.localidades, domain=NonNegativeIntegers)
modelo.subtours = Constraint(
    modelo.equipos, modelo.localidades, modelo.localidades,
    rule=lambda modelo, e, i, j: (modelo.u[e, i] - modelo.u[e, j] + num_localidades * modelo.x[e, i, j] <= num_localidades - 1)
    if i != localidad_origen and j != localidad_origen else Constraint.Skip
)

# Resolver el modelo utilizando GLPK
solver = SolverFactory('glpk')
solver.solve(modelo)
modelo.display()

# Imprimir resultados en la terminal
def imprimir_resultados(modelo):
    total_modelo = 0
    for e in modelo.equipos:
        print(f"\nEquipo {e}:")
        distancia_total_equipo = 0
        for i in modelo.localidades:
            for j in modelo.localidades:
                if modelo.x[e, i, j].value == 1:  # Si el equipo viaja de i a j
                    print(f"Ruta: Localidad {i} a Localidad {j}, Distancia: {modelo.distancias[i, j]}")
                    distancia_total_equipo += modelo.distancias[i, j]
        total_modelo += distancia_total_equipo
        print(f"Distancia total recorrida por el equipo {e}: {distancia_total_equipo} unidades.")
    print(f"\nDistancia total recorrida por todos los equipos: {total_modelo} unidades.")

# Visualización de rutas (sin cambios)
def visualizar_rutas(modelo):
    G = nx.DiGraph()
    localidades = [i for i in modelo.localidades]
    G.add_nodes_from(localidades)

    for e in modelo.equipos:
        for i in modelo.localidades:
            for j in modelo.localidades:
                if modelo.x[e, i, j].value == 1:
                    G.add_edge(i, j, label=f'Equipo {e}')

    pos = nx.shell_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue", font_size=10, font_weight="bold")
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, edge_color="black", width=2)
    plt.title("Rutas óptimas de los equipos de trabajo")
    plt.show()

# Ejecutar la impresión y visualización
imprimir_resultados(modelo)
visualizar_rutas(modelo)

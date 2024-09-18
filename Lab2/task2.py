"""
Task2, Lab2, Modelado Simulación y Optimización 
Uniandes
Developed by:
@Johan Alexis Bautista Quinayas & @Danny Camilo Muñoz Sanabria
"""

from pyomo.environ import *
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

ruta_archivo = 'data/proof_case.csv'
matriz_distancias = pd.read_csv(ruta_archivo, header=0).values
modelo_rutas = ConcreteModel()
total_localidades = len(matriz_distancias)
total_equipos = 3
localidad_inicio = 0 

modelo_rutas.equipos = RangeSet(1, total_equipos)
modelo_rutas.localidades = RangeSet(0, total_localidades - 1)

modelo_rutas.distancias = Param(modelo_rutas.localidades, modelo_rutas.localidades, initialize=lambda modelo_rutas, i, j: matriz_distancias[i][j])

# Variable de decisión: x[e, i, j] = 1 si el equipo e viaja de i a j
modelo_rutas.decision = Var(modelo_rutas.equipos, modelo_rutas.localidades, modelo_rutas.localidades, domain=Binary)

modelo_rutas.objetivo = Objective(
    expr=sum(modelo_rutas.distancias[i, j] * modelo_rutas.decision[e, i, j] for e in modelo_rutas.equipos for i in modelo_rutas.localidades for j in modelo_rutas.localidades),
    sense=minimize
)

# Restricción: cada equipo debe salir de la localidad de origen
modelo_rutas.salida_origen = Constraint(
    modelo_rutas.equipos, 
    rule=lambda modelo_rutas, e: sum(modelo_rutas.decision[e, localidad_inicio, j] for j in modelo_rutas.localidades if j != localidad_inicio) == 1
)

# Restricción: cada equipo debe regresar a la localidad de origen
modelo_rutas.regreso_origen = Constraint(
    modelo_rutas.equipos, 
    rule=lambda modelo_rutas, e: sum(modelo_rutas.decision[e, i, localidad_inicio] for i in modelo_rutas.localidades if i != localidad_inicio) == 1
)

# Restricción: cada localidad debe ser visitada exactamente una vez
def restriccion_visita(modelo_rutas, i):
    if i != localidad_inicio:
        return sum(modelo_rutas.decision[e, i, j] for e in modelo_rutas.equipos for j in modelo_rutas.localidades if j != i) == 1
    return Constraint.Skip
modelo_rutas.visita_unica = Constraint(modelo_rutas.localidades, rule=restriccion_visita)

# Restricción de continuidad (lo que entra debe salir)
def restriccion_continuidad(modelo_rutas, e, i):
    if i != localidad_inicio:
        return sum(modelo_rutas.decision[e, i, j] for j in modelo_rutas.localidades if j != i) == sum(modelo_rutas.decision[e, j, i] for j in modelo_rutas.localidades if j != i)
    return Constraint.Skip
modelo_rutas.continua = Constraint(modelo_rutas.equipos, modelo_rutas.localidades, rule=restriccion_continuidad)

# Restricción MTZ para evitar subtours
modelo_rutas.u = Var(modelo_rutas.equipos, modelo_rutas.localidades, domain=NonNegativeIntegers)
modelo_rutas.subtours = Constraint(
    modelo_rutas.equipos, modelo_rutas.localidades, modelo_rutas.localidades,
    rule=lambda modelo_rutas, e, i, j: Constraint.Skip if i == localidad_inicio or j == localidad_inicio else (modelo_rutas.u[e, i] - modelo_rutas.u[e, j] + total_localidades * modelo_rutas.decision[e, i, j] <= total_localidades - 1)
)

solver = SolverFactory('glpk')
solver.solve(modelo_rutas)
modelo_rutas.display()

def imprimir_resultados(modelo_rutas):
    print("\n=== Resultados de las Rutas de los Equipos ===")
    distancia_total_modelo = 0
    for e in modelo_rutas.equipos:
        print(f"\nEquipo {e}:")
        distancia_equipo = 0
        for i in modelo_rutas.localidades:
            for j in modelo_rutas.localidades:
                if modelo_rutas.decision[e, i, j].value == 1:  # Si el equipo viaja de i a j
                    print(f"De {i} a {j} - Distancia: {modelo_rutas.distancias[i, j]}")
                    distancia_equipo += modelo_rutas.distancias[i, j]
        distancia_total_modelo += distancia_equipo
        print(f"Distancia total recorrida por el equipo {e}: {distancia_equipo}")
    print(f"\nDistancia total recorrida por todos los equipos: {distancia_total_modelo}")

def visualizar_rutas(modelo_rutas):
    G = nx.DiGraph()
    localidades = [i for i in modelo_rutas.localidades]
    G.add_nodes_from(localidades)

    for e in modelo_rutas.equipos:
        for i in modelo_rutas.localidades:
            for j in modelo_rutas.localidades:
                if modelo_rutas.decision[e, i, j].value == 1:
                    G.add_edge(i, j, label=f'Equipo {e}')

    pos = nx.shell_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue", font_size=10, font_weight="bold")
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, edge_color="black", width=2)
    plt.title("Rutas óptimas de los equipos de trabajo")
    plt.show()

imprimir_resultados(modelo_rutas)
visualizar_rutas(modelo_rutas)

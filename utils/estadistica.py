import pandas as pd
import numpy as np
import math

def calcular_frecuencias(datos):
    """
    Calcula la tabla de distribución de frecuencias para datos cuantitativos
    agrupados, aplicando la Regla de Sturges para determinar el número de intervalos.

    Args:
        datos (list): Lista de valores numéricos (datos brutos).

    Returns:
        pd.DataFrame: Tabla de frecuencias completa con límites, marca de clase,
                      frecuencias absoluta, relativa y acumulada.
    """
    # 1. Preparación de los datos
    datos = sorted(datos)  # Ordena los datos de menor a mayor
    n = len(datos)        # Tamaño de la muestra (N)
    minimo, maximo = min(datos), max(datos)
    rango = maximo - minimo # Rango de los datos (Max - Min)

    # 2. Determinación de Parámetros (Regla de Sturges)
    # Regla de Sturges: k = 1 + 3.322 * log10(n)
    # Se usa para estimar el número óptimo de intervalos de clase (k).
    k = int(1 + 3.322 * math.log10(n))
    
    # Amplitud (tamaño) del intervalo: A = Rango / k
    # math.ceil asegura que la amplitud sea un entero superior para cubrir el rango.
    amplitud = math.ceil(rango / k)

    # 3. Creación de Intervalos de Clase
    # Genera los límites inferiores (li) y superiores (ls) para 'k' intervalos.
    # El bucle va de 0 a k-1.
    limites = [(minimo + i * amplitud, minimo + (i + 1) * amplitud) for i in range(k)]

    # 4. Cálculo de Frecuencias Absolutas (fa)
    filas = []
    for li, ls in limites:
        # Frecuencia absoluta (fa): Cuenta cuántos datos caen en el intervalo.
        # Condición: li <= x < ls (intervalo cerrado por izquierda, abierto por derecha)
        fa = sum(li <= x < ls for x in datos)
        
        # Almacena los resultados del intervalo actual
        filas.append({
            'Límite inferior': li,
            'Límite superior': ls,
            # Marca de clase: Punto medio del intervalo (li + ls) / 2
            'Marca de clase': round((li + ls) / 2, 2),
            'Frecuencia absoluta': fa
        })

    # 5. Construcción y Finalización del DataFrame
    tabla = pd.DataFrame(filas)
    
    # Frecuencia relativa (fr): fa / N
    tabla['Frecuencia relativa'] = (tabla['Frecuencia absoluta'] / n).round(3)
    
    # Frecuencia acumulada (Fa): Suma acumulativa de fa
    tabla['Frecuencia acumulada'] = tabla['Frecuencia absoluta'].cumsum()
    
    return tabla
"""
Funciones Utilitarias
=====================

Funciones de apoyo para el algoritmo de Newton-Bernstein.
"""

import numpy as np
from typing import List, Tuple, Callable


def sign_changes(sequence: np.ndarray) -> int:
    """
    Cuenta el número de cambios de signo en una secuencia.
    
    Args:
        sequence: Array de valores numéricos
        
    Returns:
        Número de cambios de signo
    """
    signs = np.sign(sequence)
    # Eliminar ceros
    signs = signs[signs != 0]
    
    if len(signs) <= 1:
        return 0
    
    changes = 0
    for i in range(len(signs) - 1):
        if signs[i] * signs[i + 1] < 0:
            changes += 1
    
    return changes


def interval_width(interval: Tuple[float, float]) -> float:
    """
    Calcula el ancho de un intervalo.
    
    Args:
        interval: Tupla (a, b)
        
    Returns:
        b - a
    """
    return interval[1] - interval[0]


def newton_step(f: Callable, df: Callable, x0: float) -> float:
    """
    Realiza un paso del método de Newton.
    
    Args:
        f: Función
        df: Derivada de la función
        x0: Punto actual
        
    Returns:
        Siguiente iteración x1 = x0 - f(x0)/df(x0)
    """
    fx = f(x0)
    dfx = df(x0)
    
    if abs(dfx) < 1e-14:
        raise ValueError("Derivada muy pequeña, posible raíz múltiple")
    
    return x0 - fx / dfx


def newton_raphson(f: Callable, df: Callable, x0: float, 
                   tol: float = 1e-10, max_iter: int = 100) -> Tuple[float, bool]:
    """
    Método de Newton-Raphson completo.
    
    Args:
        f: Función
        df: Derivada de la función
        x0: Aproximación inicial
        tol: Tolerancia para |f(x)|
        max_iter: Número máximo de iteraciones
        
    Returns:
        Tupla (raíz, convergió)
    """
    x = x0
    
    for _ in range(max_iter):
        try:
            fx = f(x)
            
            if abs(fx) < tol:
                return x, True
            
            x_new = newton_step(f, df, x)
            
            # Verificar convergencia
            if abs(x_new - x) < tol:
                return x_new, abs(f(x_new)) < tol
            
            x = x_new
            
        except (ValueError, ZeroDivisionError, OverflowError):
            return x, False
    
    return x, abs(f(x)) < tol


def is_in_interval(x: float, interval: Tuple[float, float], 
                   margin: float = 0) -> bool:
    """
    Verifica si un punto está dentro de un intervalo.
    
    Args:
        x: Punto a verificar
        interval: Tupla (a, b)
        margin: Margen adicional (por defecto 0)
        
    Returns:
        True si x está en [a-margin, b+margin]
    """
    a, b = interval
    return a - margin <= x <= b + margin


def merge_close_roots(roots: List[float], tol: float = 1e-6) -> List[float]:
    """
    Fusiona raíces que están muy cercanas.
    
    Args:
        roots: Lista de raíces
        tol: Tolerancia para considerar raíces como iguales
        
    Returns:
        Lista de raíces sin duplicados
    """
    if not roots:
        return []
    
    roots_sorted = sorted(roots)
    merged = [roots_sorted[0]]
    
    for root in roots_sorted[1:]:
        if abs(root - merged[-1]) > tol:
            merged.append(root)
    
    return merged


def polynomial_from_coeffs(coeffs: np.ndarray) -> Callable:
    """
    Crea una función polinomial a partir de sus coeficientes.
    
    Args:
        coeffs: Coeficientes [a_0, a_1, ..., a_n] para p(x) = sum a_i * x^i
        
    Returns:
        Función que evalúa el polinomio
    """
    return lambda x: np.polyval(coeffs[::-1], x)


def polynomial_derivative_coeffs(coeffs: np.ndarray) -> np.ndarray:
    """
    Calcula los coeficientes de la derivada de un polinomio.
    
    Args:
        coeffs: Coeficientes [a_0, a_1, ..., a_n]
        
    Returns:
        Coeficientes de la derivada [a_1, 2*a_2, ..., n*a_n]
    """
    if len(coeffs) <= 1:
        return np.array([0.0])
    
    n = len(coeffs)
    return np.array([i * coeffs[i] for i in range(1, n)])


def format_root(root: float, precision: int = 10) -> str:
    """
    Formatea una raíz para impresión.
    
    Args:
        root: Valor de la raíz
        precision: Número de decimales
        
    Returns:
        String formateado
    """
    return f"{root:.{precision}f}"


def evaluate_polynomial_error(coeffs: np.ndarray, root: float) -> float:
    """
    Evalúa el error al sustituir una raíz en el polinomio.
    
    Args:
        coeffs: Coeficientes del polinomio en base de potencias
        root: Raíz aproximada
        
    Returns:
        |p(root)|
    """
    p = polynomial_from_coeffs(coeffs)
    return abs(p(root))


def plot_polynomial_with_roots(coeffs: np.ndarray, roots: List[float], 
                               interval: Tuple[float, float] = None,
                               num_points: int = 1000):
    """
    Grafica un polinomio con sus raíces (requiere matplotlib).
    
    Args:
        coeffs: Coeficientes del polinomio
        roots: Lista de raíces
        interval: Intervalo a graficar (si None, se calcula automáticamente)
        num_points: Número de puntos para la gráfica
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no está instalado. No se puede graficar.")
        return
    
    if interval is None:
        if roots:
            margin = max(1.0, max(abs(r) for r in roots) * 0.2)
            interval = (min(roots) - margin, max(roots) + margin)
        else:
            interval = (-10, 10)
    
    x = np.linspace(interval[0], interval[1], num_points)
    p = polynomial_from_coeffs(coeffs)
    y = [p(xi) for xi in x]
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', linewidth=2, label='p(x)')
    plt.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    plt.axvline(x=0, color='k', linestyle='--', linewidth=0.5)
    
    if roots:
        plt.plot(roots, [0] * len(roots), 'ro', markersize=10, 
                label=f'Raíces ({len(roots)})')
    
    plt.xlabel('x', fontsize=12)
    plt.ylabel('p(x)', fontsize=12)
    plt.title('Polinomio y sus raíces', fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

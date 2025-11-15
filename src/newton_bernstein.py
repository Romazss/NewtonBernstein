"""
Algoritmo de Newton-Bernstein
==============================

Implementación del algoritmo de Newton-Bernstein para encontrar todas las
raíces de un polinomio en un intervalo dado.
"""

import numpy as np
from typing import List, Tuple, Optional
from .bernstein import BernsteinPolynomial
from .utils import (
    newton_raphson, is_in_interval, merge_close_roots,
    polynomial_from_coeffs, polynomial_derivative_coeffs
)


class NewtonBernstein:
    """
    Clase que implementa el algoritmo de Newton-Bernstein para encontrar
    raíces de polinomios.
    """
    
    def __init__(self, power_coefficients: np.ndarray, 
                 tolerance: float = 1e-10,
                 max_subdivisions: int = 100):
        """
        Inicializa el solver de Newton-Bernstein.
        
        Args:
            power_coefficients: Coeficientes del polinomio [a_0, a_1, ..., a_n]
                               donde p(x) = a_0 + a_1*x + ... + a_n*x^n
            tolerance: Tolerancia para considerar una raíz encontrada
            max_subdivisions: Número máximo de subdivisiones permitidas
        """
        self.power_coeffs = np.array(power_coefficients, dtype=float)
        self.degree = len(power_coefficients) - 1
        self.tolerance = tolerance
        self.max_subdivisions = max_subdivisions
        
        # Preparar función y derivada para Newton
        self.f = polynomial_from_coeffs(self.power_coeffs)
        deriv_coeffs = polynomial_derivative_coeffs(self.power_coeffs)
        self.df = polynomial_from_coeffs(deriv_coeffs)
        
        # Estadísticas
        self.num_subdivisions = 0
        self.num_newton_steps = 0
        self.num_exclusions = 0
    
    def find_roots(self, interval: Tuple[float, float]) -> List[float]:
        """
        Encuentra todas las raíces del polinomio en el intervalo dado.
        
        Args:
            interval: Tupla (a, b) que define el intervalo de búsqueda
            
        Returns:
            Lista ordenada de raíces encontradas
        """
        self.num_subdivisions = 0
        self.num_newton_steps = 0
        self.num_exclusions = 0
        
        roots = self._find_roots_recursive(interval, depth=0)
        
        # Fusionar raíces cercanas y ordenar
        roots = merge_close_roots(roots, self.tolerance)
        
        return sorted(roots)
    
    def _find_roots_recursive(self, interval: Tuple[float, float], 
                             depth: int) -> List[float]:
        """
        Búsqueda recursiva de raíces usando Newton-Bernstein.
        
        Args:
            interval: Intervalo actual [a, b]
            depth: Profundidad de recursión actual
            
        Returns:
            Lista de raíces encontradas en este intervalo
        """
        a, b = interval
        
        # Verificar profundidad máxima
        if depth > self.max_subdivisions:
            # Retornar punto medio si el intervalo es suficientemente pequeño
            if b - a < self.tolerance:
                mid = (a + b) / 2
                if abs(self.f(mid)) < self.tolerance:
                    return [mid]
            return []
        
        # Convertir a forma de Bernstein
        bernstein_poly = BernsteinPolynomial.from_power_basis(
            self.power_coeffs, interval
        )
        
        # Obtener cotas del polinomio
        min_val, max_val = bernstein_poly.bounds()
        
        # Criterio de exclusión: si todos los coeficientes tienen el mismo signo
        if min_val > 0 or max_val < 0:
            self.num_exclusions += 1
            return []
        
        # Si el intervalo es muy pequeño, retornar el punto medio
        if b - a < self.tolerance:
            mid = (a + b) / 2
            if abs(self.f(mid)) < self.tolerance:
                return [mid]
            return []
        
        # Intentar método de Newton desde el punto medio
        mid = (a + b) / 2
        root, converged = newton_raphson(
            self.f, self.df, mid, 
            tol=self.tolerance, 
            max_iter=50
        )
        self.num_newton_steps += 1
        
        # Si Newton convergió y la raíz está en el intervalo
        if converged and is_in_interval(root, interval, margin=self.tolerance):
            # Verificar que realmente es una raíz
            if abs(self.f(root)) < self.tolerance:
                return [root]
        
        # Subdividir el intervalo
        self.num_subdivisions += 1
        left_interval = (a, mid)
        right_interval = (mid, b)
        
        # Buscar recursivamente en ambos subintervalos
        left_roots = self._find_roots_recursive(left_interval, depth + 1)
        right_roots = self._find_roots_recursive(right_interval, depth + 1)
        
        return left_roots + right_roots
    
    def verify_roots(self, roots: List[float]) -> List[Tuple[float, float]]:
        """
        Verifica la calidad de las raíces encontradas.
        
        Args:
            roots: Lista de raíces a verificar
            
        Returns:
            Lista de tuplas (raíz, error) donde error = |p(raíz)|
        """
        return [(root, abs(self.f(root))) for root in roots]
    
    def get_statistics(self) -> dict:
        """
        Obtiene estadísticas sobre la última ejecución.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'num_subdivisions': self.num_subdivisions,
            'num_newton_steps': self.num_newton_steps,
            'num_exclusions': self.num_exclusions,
            'polynomial_degree': self.degree
        }
    
    def __repr__(self) -> str:
        return f"NewtonBernstein(degree={self.degree}, tolerance={self.tolerance})"


def find_roots(power_coefficients: np.ndarray, 
               interval: Tuple[float, float],
               tolerance: float = 1e-10) -> List[float]:
    """
    Función auxiliar para encontrar raíces de un polinomio.
    
    Args:
        power_coefficients: Coeficientes [a_0, a_1, ..., a_n]
        interval: Intervalo de búsqueda (a, b)
        tolerance: Tolerancia para las raíces
        
    Returns:
        Lista de raíces encontradas
        
    Example:
        >>> coeffs = [-6, 11, -6, 1]  # x^3 - 6x^2 + 11x - 6
        >>> roots = find_roots(coeffs, (0, 4))
        >>> print(roots)  # [1.0, 2.0, 3.0]
    """
    solver = NewtonBernstein(power_coefficients, tolerance)
    return solver.find_roots(interval)

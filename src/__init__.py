"""
Newton-Bernstein Algorithm Package
===================================

Este paquete implementa el algoritmo de Newton-Bernstein para encontrar
raíces de polinomios en una dimensión usando la representación de Bernstein.
"""

from .newton_bernstein import NewtonBernstein, find_roots
from .bernstein import BernsteinPolynomial
from .utils import sign_changes, interval_width

__version__ = "1.0.0"
__all__ = [
    "NewtonBernstein",
    "find_roots",
    "BernsteinPolynomial",
    "sign_changes",
    "interval_width"
]

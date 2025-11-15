"""
Módulo de Polinomios de Bernstein
==================================

Este módulo contiene la implementación de operaciones con polinomios
en la forma de Bernstein.
"""

import numpy as np
from typing import List, Tuple
from math import comb


class BernsteinPolynomial:
    """
    Clase para representar y manipular polinomios en forma de Bernstein.
    
    Un polinomio en forma de Bernstein en el intervalo [a, b] se representa como:
    p(x) = sum_{i=0}^n c_i * B_i^n((x-a)/(b-a))
    
    donde B_i^n(t) son los polinomios base de Bernstein.
    """
    
    def __init__(self, coefficients: np.ndarray, interval: Tuple[float, float] = (0, 1)):
        """
        Inicializa un polinomio de Bernstein.
        
        Args:
            coefficients: Coeficientes de Bernstein [c_0, c_1, ..., c_n]
            interval: Tupla (a, b) que define el intervalo del polinomio
        """
        self.coefficients = np.array(coefficients, dtype=float)
        self.degree = len(coefficients) - 1
        self.interval = interval
    
    @classmethod
    def from_power_basis(cls, power_coeffs: np.ndarray, 
                        interval: Tuple[float, float] = (0, 1)):
        """
        Convierte un polinomio desde la base de potencias a la base de Bernstein.
        
        Args:
            power_coeffs: Coeficientes [a_0, a_1, ..., a_n] donde p(x) = sum a_i * x^i
            interval: Intervalo [a, b] para el polinomio
            
        Returns:
            BernsteinPolynomial en el intervalo dado
        """
        n = len(power_coeffs) - 1
        a, b = interval
        
        # Primero transformamos el polinomio al intervalo [0, 1]
        # mediante el cambio de variable t = (x - a) / (b - a)
        transformed_coeffs = cls._transform_to_unit_interval(power_coeffs, a, b)
        
        # Luego convertimos a forma de Bernstein
        bernstein_coeffs = np.zeros(n + 1)
        for i in range(n + 1):
            for j in range(n + 1):
                if j <= i:
                    bernstein_coeffs[i] += transformed_coeffs[j] * comb(j, i) / comb(n, i)
        
        return cls(bernstein_coeffs, interval)
    
    @staticmethod
    def _transform_to_unit_interval(coeffs: np.ndarray, a: float, b: float) -> np.ndarray:
        """
        Transforma coeficientes de potencias de [a, b] a [0, 1].
        
        Si p(x) = sum a_i * x^i, queremos q(t) = p(a + t*(b-a))
        """
        n = len(coeffs) - 1
        h = b - a
        new_coeffs = np.zeros(n + 1)
        
        # Usamos la fórmula binomial para expandir (a + t*h)^i
        for i in range(n + 1):
            for j in range(i, n + 1):
                new_coeffs[i] += coeffs[j] * comb(j, i) * (a ** (j - i)) * (h ** i)
        
        return new_coeffs
    
    def evaluate(self, x: float) -> float:
        """
        Evalúa el polinomio en un punto x usando el algoritmo de De Casteljau.
        
        Args:
            x: Punto donde evaluar
            
        Returns:
            Valor del polinomio en x
        """
        a, b = self.interval
        t = (x - a) / (b - a)
        
        # Algoritmo de De Casteljau
        coeffs = self.coefficients.copy()
        n = self.degree
        
        for j in range(1, n + 1):
            for i in range(n - j + 1):
                coeffs[i] = (1 - t) * coeffs[i] + t * coeffs[i + 1]
        
        return coeffs[0]
    
    def derivative(self) -> 'BernsteinPolynomial':
        """
        Calcula la derivada del polinomio en forma de Bernstein.
        
        Returns:
            Nuevo BernsteinPolynomial representando la derivada
        """
        if self.degree == 0:
            return BernsteinPolynomial([0], self.interval)
        
        n = self.degree
        a, b = self.interval
        h = b - a
        
        # Coeficientes de la derivada en forma de Bernstein
        deriv_coeffs = np.zeros(n)
        for i in range(n):
            deriv_coeffs[i] = (n / h) * (self.coefficients[i + 1] - self.coefficients[i])
        
        return BernsteinPolynomial(deriv_coeffs, self.interval)
    
    def subdivide(self, t: float = 0.5) -> Tuple['BernsteinPolynomial', 'BernsteinPolynomial']:
        """
        Subdivide el polinomio en el punto t usando el algoritmo de De Casteljau.
        
        Args:
            t: Punto de subdivisión en [0, 1] (por defecto en el punto medio)
            
        Returns:
            Tupla (left_poly, right_poly) con los polinomios subdivididos
        """
        n = self.degree
        a, b = self.interval
        split_point = a + t * (b - a)
        
        # Matriz para almacenar los valores intermedios del algoritmo de De Casteljau
        matrix = np.zeros((n + 1, n + 1))
        matrix[:, 0] = self.coefficients
        
        # Algoritmo de De Casteljau
        for j in range(1, n + 1):
            for i in range(n - j + 1):
                matrix[i, j] = (1 - t) * matrix[i, j - 1] + t * matrix[i + 1, j - 1]
        
        # Los coeficientes del polinomio izquierdo están en la primera fila
        left_coeffs = matrix[0, :]
        
        # Los coeficientes del polinomio derecho están en la diagonal
        right_coeffs = np.array([matrix[i, n - i] for i in range(n + 1)])
        
        left_poly = BernsteinPolynomial(left_coeffs, (a, split_point))
        right_poly = BernsteinPolynomial(right_coeffs, (split_point, b))
        
        return left_poly, right_poly
    
    def bounds(self) -> Tuple[float, float]:
        """
        Calcula cotas inferior y superior del polinomio en su intervalo.
        
        Por la propiedad de la envolvente convexa, el polinomio está
        acotado por el mínimo y máximo de sus coeficientes de Bernstein.
        
        Returns:
            Tupla (min, max) con las cotas
        """
        return np.min(self.coefficients), np.max(self.coefficients)
    
    def sign_changes(self) -> int:
        """
        Cuenta el número de cambios de signo en la secuencia de coeficientes.
        
        Returns:
            Número de cambios de signo
        """
        signs = np.sign(self.coefficients)
        # Eliminar ceros
        signs = signs[signs != 0]
        
        if len(signs) <= 1:
            return 0
        
        changes = 0
        for i in range(len(signs) - 1):
            if signs[i] * signs[i + 1] < 0:
                changes += 1
        
        return changes
    
    def to_power_basis(self) -> np.ndarray:
        """
        Convierte el polinomio de Bernstein de vuelta a la base de potencias.
        
        Returns:
            Array con coeficientes [a_0, a_1, ..., a_n]
        """
        n = self.degree
        power_coeffs = np.zeros(n + 1)
        
        for j in range(n + 1):
            for i in range(j + 1):
                sign = (-1) ** (j - i)
                power_coeffs[j] += sign * comb(n, j) * comb(j, i) * self.coefficients[i]
        
        a, b = self.interval
        h = b - a
        
        # Transformar de [0, 1] a [a, b]
        scaled_coeffs = np.zeros(n + 1)
        for i in range(n + 1):
            for j in range(i, n + 1):
                scaled_coeffs[j] += power_coeffs[i] * comb(j, i) * ((-a) ** (j - i)) / (h ** i)
        
        return scaled_coeffs
    
    def __repr__(self) -> str:
        return f"BernsteinPolynomial(degree={self.degree}, interval={self.interval})"
    
    def __str__(self) -> str:
        return f"Bernstein polynomial of degree {self.degree} on [{self.interval[0]}, {self.interval[1]}]"

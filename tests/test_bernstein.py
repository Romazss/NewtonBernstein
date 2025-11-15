"""
Tests para el módulo de polinomios de Bernstein
"""

import pytest
import numpy as np
from src.bernstein import BernsteinPolynomial


class TestBernsteinPolynomial:
    
    def test_initialization(self):
        """Test de inicialización básica."""
        coeffs = [1, 2, 3]
        poly = BernsteinPolynomial(coeffs, (0, 1))
        
        assert poly.degree == 2
        assert poly.interval == (0, 1)
        assert len(poly.coefficients) == 3
    
    def test_from_power_basis_linear(self):
        """Test de conversión desde base de potencias para polinomio lineal."""
        # p(x) = 1 + 2x en [0, 1]
        power_coeffs = np.array([1, 2])
        poly = BernsteinPolynomial.from_power_basis(power_coeffs, (0, 1))
        
        # Verificar evaluación en puntos conocidos
        assert np.isclose(poly.evaluate(0), 1.0)
        assert np.isclose(poly.evaluate(1), 3.0)
    
    def test_from_power_basis_quadratic(self):
        """Test de conversión para polinomio cuadrático."""
        # p(x) = x² en [0, 1]
        power_coeffs = np.array([0, 0, 1])
        poly = BernsteinPolynomial.from_power_basis(power_coeffs, (0, 1))
        
        assert np.isclose(poly.evaluate(0), 0.0)
        assert np.isclose(poly.evaluate(1), 1.0)
        assert np.isclose(poly.evaluate(0.5), 0.25)
    
    def test_evaluate(self):
        """Test de evaluación del polinomio."""
        coeffs = np.array([0, 0.5, 1])  # Interpolación lineal de 0 a 1
        poly = BernsteinPolynomial(coeffs, (0, 1))
        
        # Evaluar en varios puntos
        assert np.isclose(poly.evaluate(0), 0.0, atol=1e-10)
        assert np.isclose(poly.evaluate(1), 1.0, atol=1e-10)
    
    def test_bounds(self):
        """Test de cotas del polinomio."""
        coeffs = np.array([1, 3, 2, 4])
        poly = BernsteinPolynomial(coeffs, (0, 1))
        
        min_val, max_val = poly.bounds()
        
        assert min_val == 1
        assert max_val == 4
    
    def test_derivative(self):
        """Test de derivada."""
        # p(x) = x² en [0, 1], p'(x) = 2x
        power_coeffs = np.array([0, 0, 1])
        poly = BernsteinPolynomial.from_power_basis(power_coeffs, (0, 1))
        
        deriv = poly.derivative()
        
        # La derivada en x=0 debe ser 0, en x=1 debe ser 2
        assert np.isclose(deriv.evaluate(0), 0.0, atol=1e-10)
        assert np.isclose(deriv.evaluate(1), 2.0, atol=1e-10)
    
    def test_subdivide(self):
        """Test de subdivisión."""
        # p(x) = x en [0, 1]
        power_coeffs = np.array([0, 1])
        poly = BernsteinPolynomial.from_power_basis(power_coeffs, (0, 1))
        
        left, right = poly.subdivide(t=0.5)
        
        # Verificar intervalos
        assert left.interval == (0, 0.5)
        assert right.interval == (0.5, 1)
        
        # Verificar que las evaluaciones coinciden
        test_point = 0.25
        assert np.isclose(poly.evaluate(test_point), left.evaluate(test_point))
        
        test_point = 0.75
        assert np.isclose(poly.evaluate(test_point), right.evaluate(test_point))
    
    def test_sign_changes(self):
        """Test de conteo de cambios de signo."""
        # Sin cambios de signo
        coeffs1 = np.array([1, 2, 3])
        poly1 = BernsteinPolynomial(coeffs1, (0, 1))
        assert poly1.sign_changes() == 0
        
        # Un cambio de signo
        coeffs2 = np.array([1, -1, 2])
        poly2 = BernsteinPolynomial(coeffs2, (0, 1))
        assert poly2.sign_changes() == 2
        
        # Con ceros
        coeffs3 = np.array([1, 0, -1])
        poly3 = BernsteinPolynomial(coeffs3, (0, 1))
        assert poly3.sign_changes() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

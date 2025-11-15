"""
Tests para el módulo de utilidades
"""

import pytest
import numpy as np
from src.utils import (
    sign_changes, interval_width, newton_step, newton_raphson,
    is_in_interval, merge_close_roots, polynomial_from_coeffs,
    polynomial_derivative_coeffs, evaluate_polynomial_error
)


class TestUtils:
    
    def test_sign_changes(self):
        """Test de conteo de cambios de signo."""
        # Sin cambios
        assert sign_changes(np.array([1, 2, 3])) == 0
        
        # Un cambio
        assert sign_changes(np.array([1, -1])) == 1
        
        # Dos cambios
        assert sign_changes(np.array([1, -1, 2])) == 2
        
        # Con ceros (se ignoran)
        assert sign_changes(np.array([1, 0, -1])) == 1
    
    def test_interval_width(self):
        """Test de cálculo de ancho de intervalo."""
        assert interval_width((0, 1)) == 1
        assert interval_width((-1, 1)) == 2
        assert interval_width((2, 5)) == 3
    
    def test_newton_step(self):
        """Test de un paso de Newton."""
        # f(x) = x² - 4, f'(x) = 2x
        f = lambda x: x**2 - 4
        df = lambda x: 2*x
        
        x0 = 3.0
        x1 = newton_step(f, df, x0)
        
        # x1 = x0 - f(x0)/f'(x0) = 3 - 5/6 = 2.166...
        assert np.isclose(x1, 2.166666666666667)
    
    def test_newton_raphson_convergence(self):
        """Test de convergencia de Newton-Raphson."""
        # f(x) = x² - 4, raíz en x = 2
        f = lambda x: x**2 - 4
        df = lambda x: 2*x
        
        root, converged = newton_raphson(f, df, 3.0)
        
        assert converged
        assert np.isclose(root, 2.0, atol=1e-8)
    
    def test_is_in_interval(self):
        """Test de verificación si un punto está en un intervalo."""
        assert is_in_interval(1.5, (1, 2))
        assert is_in_interval(1, (1, 2))
        assert is_in_interval(2, (1, 2))
        assert not is_in_interval(0, (1, 2))
        assert not is_in_interval(3, (1, 2))
        
        # Con margen
        assert is_in_interval(0.9, (1, 2), margin=0.2)
    
    def test_merge_close_roots(self):
        """Test de fusión de raíces cercanas."""
        roots = [1.0, 1.00001, 2.0, 2.00001]
        merged = merge_close_roots(roots, tol=1e-4)
        
        assert len(merged) == 2
        assert np.isclose(merged[0], 1.0, atol=1e-4)
        assert np.isclose(merged[1], 2.0, atol=1e-4)
    
    def test_polynomial_from_coeffs(self):
        """Test de creación de función polinomial."""
        # p(x) = 1 + 2x + 3x²
        coeffs = np.array([1, 2, 3])
        p = polynomial_from_coeffs(coeffs)
        
        assert p(0) == 1
        assert p(1) == 6
        assert p(2) == 17
    
    def test_polynomial_derivative_coeffs(self):
        """Test de cálculo de coeficientes de la derivada."""
        # p(x) = 1 + 2x + 3x²
        # p'(x) = 2 + 6x
        coeffs = np.array([1, 2, 3])
        deriv_coeffs = polynomial_derivative_coeffs(coeffs)
        
        assert len(deriv_coeffs) == 2
        assert deriv_coeffs[0] == 2
        assert deriv_coeffs[1] == 6
    
    def test_evaluate_polynomial_error(self):
        """Test de evaluación del error."""
        # p(x) = x - 2
        coeffs = np.array([-2, 1])
        
        # En x = 2, el error debe ser 0
        error = evaluate_polynomial_error(coeffs, 2.0)
        assert np.isclose(error, 0.0, atol=1e-10)
        
        # En x = 3, el error debe ser 1
        error = evaluate_polynomial_error(coeffs, 3.0)
        assert np.isclose(error, 1.0, atol=1e-10)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

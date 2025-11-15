"""
Tests para el algoritmo de Newton-Bernstein
"""

import pytest
import numpy as np
from src.newton_bernstein import NewtonBernstein, find_roots


class TestNewtonBernstein:
    
    def test_linear_polynomial(self):
        """Test con polinomio lineal."""
        # p(x) = x - 2
        coeffs = np.array([-2, 1])
        roots = find_roots(coeffs, (0, 5))
        
        assert len(roots) == 1
        assert np.isclose(roots[0], 2.0, atol=1e-8)
    
    def test_quadratic_two_roots(self):
        """Test con polinomio cuadrático con dos raíces."""
        # p(x) = (x-1)(x-3) = x² - 4x + 3
        coeffs = np.array([3, -4, 1])
        roots = find_roots(coeffs, (0, 5))
        
        assert len(roots) == 2
        assert np.isclose(roots[0], 1.0, atol=1e-8)
        assert np.isclose(roots[1], 3.0, atol=1e-8)
    
    def test_cubic_three_roots(self):
        """Test con polinomio cúbico con tres raíces."""
        # p(x) = (x-1)(x-2)(x-3) = x³ - 6x² + 11x - 6
        coeffs = np.array([-6, 11, -6, 1])
        roots = find_roots(coeffs, (0, 4))
        
        assert len(roots) == 3
        assert np.isclose(roots[0], 1.0, atol=1e-8)
        assert np.isclose(roots[1], 2.0, atol=1e-8)
        assert np.isclose(roots[2], 3.0, atol=1e-8)
    
    def test_no_roots(self):
        """Test con polinomio sin raíces en el intervalo."""
        # p(x) = x² + 1 (no tiene raíces reales)
        coeffs = np.array([1, 0, 1])
        roots = find_roots(coeffs, (-5, 5))
        
        assert len(roots) == 0
    
    def test_root_at_boundary(self):
        """Test con raíz en el borde del intervalo."""
        # p(x) = x - 1
        coeffs = np.array([-1, 1])
        roots = find_roots(coeffs, (1, 3))
        
        assert len(roots) == 1
        assert np.isclose(roots[0], 1.0, atol=1e-8)
    
    def test_multiple_root(self):
        """Test con raíz múltiple."""
        # p(x) = (x-2)² = x² - 4x + 4
        coeffs = np.array([4, -4, 1])
        roots = find_roots(coeffs, (0, 5))
        
        # Puede encontrar la raíz una o dos veces debido a la multiplicidad
        assert len(roots) >= 1
        assert any(np.isclose(root, 2.0, atol=1e-6) for root in roots)
    
    def test_verify_roots(self):
        """Test de verificación de raíces."""
        coeffs = np.array([-6, 11, -6, 1])
        solver = NewtonBernstein(coeffs)
        roots = solver.find_roots((0, 4))
        
        verification = solver.verify_roots(roots)
        
        # Todas las raíces deben tener error pequeño
        for root, error in verification:
            assert error < 1e-8
    
    def test_statistics(self):
        """Test de estadísticas del algoritmo."""
        coeffs = np.array([-6, 11, -6, 1])
        solver = NewtonBernstein(coeffs)
        solver.find_roots((0, 4))
        
        stats = solver.get_statistics()
        
        assert 'num_subdivisions' in stats
        assert 'num_newton_steps' in stats
        assert 'num_exclusions' in stats
        assert stats['polynomial_degree'] == 3
    
    def test_different_tolerance(self):
        """Test con diferentes tolerancias."""
        coeffs = np.array([-2, 1])  # x - 2
        
        # Tolerancia estricta
        roots1 = find_roots(coeffs, (0, 5), tolerance=1e-12)
        
        # Tolerancia laxa
        roots2 = find_roots(coeffs, (0, 5), tolerance=1e-4)
        
        # Ambas deben encontrar la raíz
        assert len(roots1) == 1
        assert len(roots2) == 1
        assert np.isclose(roots1[0], roots2[0], atol=1e-4)
    
    def test_negative_roots(self):
        """Test con raíces negativas."""
        # p(x) = (x+1)(x+2) = x² + 3x + 2
        coeffs = np.array([2, 3, 1])
        roots = find_roots(coeffs, (-5, 0))
        
        assert len(roots) == 2
        assert np.isclose(roots[0], -2.0, atol=1e-8)
        assert np.isclose(roots[1], -1.0, atol=1e-8)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

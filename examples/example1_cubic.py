"""
Ejemplo 1: Polinomio Cúbico con Tres Raíces Simples
====================================================

Este ejemplo reproduce el caso clásico del polinomio:
p(x) = x^3 - 6x^2 + 11x - 6 = (x-1)(x-2)(x-3)

Este polinomio tiene tres raíces simples en x = 1, 2, 3.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.newton_bernstein import NewtonBernstein, find_roots
from src.utils import format_root, evaluate_polynomial_error


def example1_cubic_polynomial():
    """
    Encuentra las raíces de p(x) = x^3 - 6x^2 + 11x - 6
    """
    print("=" * 70)
    print("EJEMPLO 1: Polinomio Cúbico")
    print("=" * 70)
    print()
    
    # Definir el polinomio: p(x) = x^3 - 6x^2 + 11x - 6
    # Coeficientes en orden: [a_0, a_1, a_2, a_3] para a_0 + a_1*x + a_2*x^2 + a_3*x^3
    coeffs = np.array([-6, 11, -6, 1], dtype=float)
    
    print("Polinomio: p(x) = x³ - 6x² + 11x - 6")
    print("Factorización: p(x) = (x-1)(x-2)(x-3)")
    print("Raíces exactas: x = 1, 2, 3")
    print()
    
    # Configurar el intervalo de búsqueda
    interval = (0, 4)
    tolerance = 1e-10
    
    print(f"Intervalo de búsqueda: [{interval[0]}, {interval[1]}]")
    print(f"Tolerancia: {tolerance}")
    print()
    
    # Crear el solver
    solver = NewtonBernstein(coeffs, tolerance=tolerance)
    
    # Encontrar raíces
    print("Ejecutando algoritmo de Newton-Bernstein...")
    roots = solver.find_roots(interval)
    
    print()
    print("-" * 70)
    print("RESULTADOS")
    print("-" * 70)
    print(f"Número de raíces encontradas: {len(roots)}")
    print()
    
    # Mostrar raíces y verificación
    expected_roots = [1.0, 2.0, 3.0]
    
    print(f"{'Raíz':<15} {'Valor Aproximado':<20} {'Error |p(x)|':<20} {'Error vs Exacta'}")
    print("-" * 70)
    
    for i, root in enumerate(roots):
        error_eval = evaluate_polynomial_error(coeffs, root)
        error_exact = abs(root - expected_roots[i]) if i < len(expected_roots) else float('nan')
        print(f"x_{i+1:<13} {format_root(root, 12):<20} {error_eval:<20.2e} {error_exact:<.2e}")
    
    print()
    print("-" * 70)
    print("ESTADÍSTICAS DEL ALGORITMO")
    print("-" * 70)
    
    stats = solver.get_statistics()
    print(f"Número de subdivisiones: {stats['num_subdivisions']}")
    print(f"Número de pasos de Newton: {stats['num_newton_steps']}")
    print(f"Número de exclusiones: {stats['num_exclusions']}")
    print(f"Grado del polinomio: {stats['polynomial_degree']}")
    print()
    
    # Verificación adicional
    print("-" * 70)
    print("VERIFICACIÓN")
    print("-" * 70)
    
    verification = solver.verify_roots(roots)
    max_error = max(error for _, error in verification)
    
    print(f"Error máximo |p(x)|: {max_error:.2e}")
    
    if max_error < tolerance:
        print("✓ Todas las raíces cumplen con la tolerancia especificada")
    else:
        print("✗ Algunas raíces no cumplen con la tolerancia")
    
    print()
    
    return roots, stats


def plot_example1(roots):
    """
    Grafica el polinomio y sus raíces (opcional, requiere matplotlib).
    """
    try:
        import matplotlib.pyplot as plt
        
        coeffs = np.array([-6, 11, -6, 1], dtype=float)
        x = np.linspace(-0.5, 4.5, 1000)
        y = np.polyval(coeffs[::-1], x)
        
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, 'b-', linewidth=2, label='p(x) = x³ - 6x² + 11x - 6')
        plt.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
        plt.axvline(x=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Marcar las raíces
        plt.plot(roots, [0] * len(roots), 'ro', markersize=10, 
                label=f'Raíces encontradas ({len(roots)})', zorder=5)
        
        # Marcar las raíces exactas
        exact_roots = [1, 2, 3]
        plt.plot(exact_roots, [0] * len(exact_roots), 'g^', markersize=8, 
                label='Raíces exactas', zorder=4, alpha=0.6)
        
        plt.xlabel('x', fontsize=12)
        plt.ylabel('p(x)', fontsize=12)
        plt.title('Ejemplo 1: Polinomio Cúbico y sus Raíces', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Guardar la figura
        output_path = os.path.join(os.path.dirname(__file__), 'example1_plot.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Gráfica guardada en: {output_path}")
        
        plt.show()
        
    except ImportError:
        print("matplotlib no está instalado. Saltando visualización.")


if __name__ == "__main__":
    # Ejecutar el ejemplo
    roots, stats = example1_cubic_polynomial()
    
    # Intentar graficar (opcional)
    try:
        plot_example1(roots)
    except Exception as e:
        print(f"No se pudo generar la gráfica: {e}")

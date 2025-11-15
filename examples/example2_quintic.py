"""
Ejemplo 2: Polinomio de Quinto Grado con Raíces Múltiples
==========================================================

Este ejemplo presenta un polinomio de grado 5 con raíces de diferentes
multiplicidades y algunas raíces irracionales:

p(x) = (x - 0.5)² * (x + 1) * (x - 2) * (x - 3.5)

Raíces:
- x = 0.5 (multiplicidad 2)
- x = -1 (simple)
- x = 2 (simple)
- x = 3.5 (simple)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.newton_bernstein import NewtonBernstein, find_roots
from src.utils import format_root, evaluate_polynomial_error


def expand_polynomial():
    """
    Expande el polinomio (x - 0.5)² * (x + 1) * (x - 2) * (x - 3.5)
    """
    # (x - 0.5)² = x² - x + 0.25
    factor1 = np.array([0.25, -1, 1])  # 0.25 - x + x²
    
    # (x + 1)
    factor2 = np.array([1, 1])  # 1 + x
    
    # (x - 2)
    factor3 = np.array([-2, 1])  # -2 + x
    
    # (x - 3.5)
    factor4 = np.array([-3.5, 1])  # -3.5 + x
    
    # Multiplicar progresivamente
    result = np.convolve(factor1, factor2)
    result = np.convolve(result, factor3)
    result = np.convolve(result, factor4)
    
    return result


def example2_quintic_polynomial():
    """
    Encuentra las raíces de p(x) = (x - 0.5)² * (x + 1) * (x - 2) * (x - 3.5)
    """
    print("=" * 70)
    print("EJEMPLO 2: Polinomio de Quinto Grado")
    print("=" * 70)
    print()
    
    # Expandir el polinomio
    coeffs = expand_polynomial()
    
    print("Polinomio: p(x) = (x - 0.5)² · (x + 1) · (x - 2) · (x - 3.5)")
    print()
    print("Forma expandida:")
    terms = []
    for i, c in enumerate(coeffs):
        if abs(c) > 1e-10:
            if i == 0:
                terms.append(f"{c:.4f}")
            elif i == 1:
                terms.append(f"{c:+.4f}x")
            else:
                terms.append(f"{c:+.4f}x^{i}")
    print("p(x) = " + " ".join(terms))
    print()
    
    print("Raíces exactas:")
    print("  x = -1.0    (multiplicidad 1)")
    print("  x =  0.5    (multiplicidad 2)")
    print("  x =  2.0    (multiplicidad 1)")
    print("  x =  3.5    (multiplicidad 1)")
    print()
    
    # Configurar el intervalo de búsqueda
    interval = (-2, 5)
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
    expected_roots = [-1.0, 0.5, 2.0, 3.5]
    
    print(f"{'Raíz':<15} {'Valor Aproximado':<20} {'Error |p(x)|':<20} {'Multiplicidad Esperada'}")
    print("-" * 70)
    
    expected_mult = {-1.0: 1, 0.5: 2, 2.0: 1, 3.5: 1}
    
    for i, root in enumerate(roots):
        error_eval = evaluate_polynomial_error(coeffs, root)
        
        # Encontrar la raíz exacta más cercana
        closest_exact = min(expected_roots, key=lambda x: abs(x - root))
        mult = expected_mult.get(closest_exact, '?')
        
        print(f"x_{i+1:<13} {format_root(root, 12):<20} {error_eval:<20.2e} {mult}")
    
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
    
    # Verificar si se encontraron todas las raíces únicas
    print()
    print("Comparación con raíces exactas:")
    for exact in expected_roots:
        mult = expected_mult[exact]
        found = [r for r in roots if abs(r - exact) < 1e-3]
        print(f"  x = {exact:5.1f} (mult {mult}): ", end="")
        if found:
            print(f"✓ Encontrada ({len(found)} instancia(s))")
        else:
            print("✗ NO encontrada")
    
    print()
    
    # Nota sobre raíces múltiples
    print("-" * 70)
    print("NOTA SOBRE RAÍCES MÚLTIPLES")
    print("-" * 70)
    print("La raíz x = 0.5 tiene multiplicidad 2.")
    print("El algoritmo puede encontrarla una o dos veces dependiendo de la")
    print("subdivisión y los criterios de fusión de raíces cercanas.")
    print("En la práctica, las raíces múltiples presentan desafíos debido a que")
    print("la derivada también se anula en ese punto, afectando la convergencia")
    print("del método de Newton.")
    print()
    
    return roots, stats, coeffs


def plot_example2(roots, coeffs):
    """
    Grafica el polinomio y sus raíces (opcional, requiere matplotlib).
    """
    try:
        import matplotlib.pyplot as plt
        
        x = np.linspace(-2.5, 5.5, 1000)
        y = np.polyval(coeffs[::-1], x)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfica completa
        ax1.plot(x, y, 'b-', linewidth=2, label='p(x)')
        ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
        ax1.axvline(x=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Marcar las raíces encontradas
        ax1.plot(roots, [0] * len(roots), 'ro', markersize=10, 
                label=f'Raíces encontradas ({len(roots)})', zorder=5)
        
        # Marcar las raíces exactas
        exact_roots = [-1, 0.5, 2, 3.5]
        ax1.plot(exact_roots, [0] * len(exact_roots), 'g^', markersize=8, 
                label='Raíces exactas', zorder=4, alpha=0.6)
        
        ax1.set_xlabel('x', fontsize=12)
        ax1.set_ylabel('p(x)', fontsize=12)
        ax1.set_title('Ejemplo 2: Polinomio de Quinto Grado', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Zoom cerca de las raíces
        x_zoom = np.linspace(-1.5, 4, 1000)
        y_zoom = np.polyval(coeffs[::-1], x_zoom)
        
        ax2.plot(x_zoom, y_zoom, 'b-', linewidth=2)
        ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Marcar raíces
        ax2.plot(roots, [0] * len(roots), 'ro', markersize=10, zorder=5)
        ax2.plot(exact_roots, [0] * len(exact_roots), 'g^', markersize=8, zorder=4, alpha=0.6)
        
        ax2.set_xlabel('x', fontsize=12)
        ax2.set_ylabel('p(x)', fontsize=12)
        ax2.set_title('Vista Ampliada cerca de las Raíces', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([-5, 5])
        
        plt.tight_layout()
        
        # Guardar la figura
        output_path = os.path.join(os.path.dirname(__file__), 'example2_plot.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Gráfica guardada en: {output_path}")
        
        plt.show()
        
    except ImportError:
        print("matplotlib no está instalado. Saltando visualización.")


if __name__ == "__main__":
    # Ejecutar el ejemplo
    roots, stats, coeffs = example2_quintic_polynomial()
    
    # Intentar graficar (opcional)
    try:
        plot_example2(roots, coeffs)
    except Exception as e:
        print(f"No se pudo generar la gráfica: {e}")

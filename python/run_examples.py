"""
Script principal para ejecutar todos los ejemplos del proyecto
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    Ejecuta todos los ejemplos del proyecto.
    """
    print("=" * 80)
    print(" " * 20 + "ALGORITMO DE NEWTON-BERNSTEIN")
    print(" " * 20 + "Ejemplos Numéricos")
    print("=" * 80)
    print()
    
    # Importar y ejecutar ejemplo 1
    try:
        from examples.example1_cubic import example1_cubic_polynomial
        roots1, stats1 = example1_cubic_polynomial()
        print("\n" + "=" * 80 + "\n")
    except Exception as e:
        print(f"Error al ejecutar ejemplo 1: {e}")
        print()
    
    # Importar y ejecutar ejemplo 2
    try:
        from examples.example2_quintic import example2_quintic_polynomial
        roots2, stats2, coeffs2 = example2_quintic_polynomial()
        print("\n" + "=" * 80 + "\n")
    except Exception as e:
        print(f"Error al ejecutar ejemplo 2: {e}")
        print()
    
    print("=" * 80)
    print(" " * 25 + "Ejemplos completados")
    print("=" * 80)


if __name__ == "__main__":
    main()

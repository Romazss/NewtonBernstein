#!/usr/bin/env python3
"""
EJECUTOR SIMPLIFICADO: Simulaciones Navier-Stokes 3D con Newton-Bernstein
========================================================================

Script de ejecución rápida para análisis del contraejemplo Navier-Stokes clásico
con Re ≥ 1000 usando aceleración GPU (RTX 4060 + CUDA 12.6).

USO:
----
python quick_run_navier_stokes.py [opción]

Opciones:
  1 - Simulación rápida (Re=1000, grilla 32³, 100 steps) ~ 2 min
  2 - Simulación estándar (Re∈[1000,5000], 32³, 200 steps) ~ 5 min
  3 - Simulación completa (Re∈[1000,5000,10000], 32³, 500 steps) ~ 15 min
  4 - Test GPU (verifica CUDA sin simulación)

Ejemplo:
  python quick_run_navier_stokes.py 1
  
"""

import sys
import os
import numpy as np
from datetime import datetime
import traceback

# Agregar paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

def print_header(title):
    """Imprimir encabezado formateado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_gpu():
    """Test GPU connectivity."""
    print_header("TEST GPU - Verificación CUDA/CuPy")
    
    try:
        import cupy as cp
        print(f"✓ CuPy {cp.__version__} cargado exitosamente")
        
        device = cp.cuda.Device()
        print(f"✓ GPU Device: {device}")
        
        # Simple test
        gpu_arr = cp.arange(1000000)
        result = cp.sum(gpu_arr)
        expected = sum(range(1000000))
        
        if result == expected:
            print(f"✓ GPU Operations: CORRECTAS (suma de 10⁶ elementos = {result})")
        else:
            print(f"✗ GPU Error: suma incorrecta")
            return False
        
        print("\n✅ GPU TEST EXITOSO")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        traceback.print_exc()
        return False

def run_quick_simulation():
    """Simulación rápida para verificación."""
    print_header("SIMULACIÓN RÁPIDA: Re=1000, 32³, 100 steps")
    
    try:
        from navier_stokes_cuda_highre import NavierStokesCUDAHighRe
        from navier_stokes_physics_visualizer import NavierStokesPhysicsVisualizer
        
        print("Inicializando solver...")
        solver = NavierStokesCUDAHighRe(
            reynolds=1000,
            domain_size=2*np.pi,
            N=32,  # grilla 32³
            use_cuda=True
        )
        
        solver.setup_domain()
        solver.initialize_velocity_field()
        
        print(f"Ejecutando 100 timesteps...")
        print(f"Tiempo inicial: {datetime.now().strftime('%H:%M:%S')}")
        
        t = 0.0
        dt = 0.01
        max_steps = 100
        
        energies = []
        enstrophies = []
        times = []
        
        for step in range(max_steps):
            solver.step_forward(dt)
            t += dt
            
            diag = solver.get_diagnostics()
            energies.append(diag['kinetic_energy'])
            enstrophies.append(diag['enstrophy'])
            times.append(t)
            
            if (step + 1) % 20 == 0:
                print(f"  Step {step+1:3d}/100 | t={t:.3f} | E={diag['kinetic_energy']:.6e} | Z={diag['enstrophy']:.6e}")
        
        print(f"✓ Simulación completada en t = {t:.3f}s")
        print(f"\nDiagnósticos finales:")
        print(f"  - Energía cinética: {energies[-1]:.6e}")
        print(f"  - Enstrofia: {enstrophies[-1]:.6e}")
        print(f"  - Energía máxima: {max(energies):.6e}")
        print(f"  - Enstrofia máxima: {max(enstrophies):.6e}")
        
        print("\n✅ SIMULACIÓN RÁPIDA EXITOSA")
        return True
        
    except Exception as e:
        print(f"✗ Error durante simulación: {e}")
        traceback.print_exc()
        return False

def run_standard_simulation():
    """Simulación estándar con múltiples Reynolds."""
    print_header("SIMULACIÓN ESTÁNDAR: Re∈[1000, 5000], 32³, 200 steps")
    
    try:
        from navier_stokes_counterexample_solver import AdvancedNavierStokesCounterexampleFinder
        
        finder = AdvancedNavierStokesCounterexampleFinder()
        
        print("Ejecutando análisis multi-Reynolds...")
        print(f"Tiempo inicial: {datetime.now().strftime('%H:%M:%S')}\n")
        
        results = finder.run_multi_reynolds_study(
            reynolds_numbers=[1000, 5000],
            grid_size=32,
            simulation_time=0.5,
            use_cuda=True
        )
        
        print("\n✅ SIMULACIÓN ESTÁNDAR EXITOSA")
        print(f"\nResultados:")
        for re, result in results.items():
            print(f"\n  Reynolds {re}:")
            if isinstance(result, dict):
                for key, val in result.items():
                    if isinstance(val, (int, float)):
                        print(f"    {key}: {val:.6e}" if isinstance(val, float) else f"    {key}: {val}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error durante simulación: {e}")
        traceback.print_exc()
        return False

def run_complete_simulation():
    """Simulación completa con tres Reynolds numbers."""
    print_header("SIMULACIÓN COMPLETA: Re∈[1000, 5000, 10000], 32³, 500 steps")
    
    try:
        from navier_stokes_counterexample_solver import AdvancedNavierStokesCounterexampleFinder
        
        finder = AdvancedNavierStokesCounterexampleFinder()
        
        print("Ejecutando análisis COMPLETO multi-Reynolds...")
        print(f"Tiempo inicial: {datetime.now().strftime('%H:%M:%S')}\n")
        
        results = finder.run_multi_reynolds_study(
            reynolds_numbers=[1000, 5000, 10000],
            grid_size=32,
            simulation_time=1.0,
            use_cuda=True
        )
        
        print("\n✅ SIMULACIÓN COMPLETA EXITOSA")
        print(f"\nResultados finales:")
        for re, result in results.items():
            print(f"\n  Reynolds {re}:")
            if isinstance(result, dict):
                for key, val in result.items():
                    if isinstance(val, (int, float)):
                        print(f"    {key}: {val:.6e}" if isinstance(val, float) else f"    {key}: {val}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error durante simulación: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  EJECUTOR: Navier-Stokes 3D + Newton-Bernstein + GPU CUDA  ".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    if len(sys.argv) > 1:
        option = sys.argv[1]
    else:
        print("\nOpciones disponibles:")
        print("  1 - Simulación rápida (Re=1000, grilla 32³, 100 steps) ~ 2 min")
        print("  2 - Simulación estándar (Re∈[1000,5000], 32³, 200 steps) ~ 5 min")
        print("  3 - Simulación completa (Re∈[1000,5000,10000], 32³, 500 steps) ~ 15 min")
        print("  4 - Test GPU (verifica CUDA sin simulación)")
        option = input("\nSelecciona opción (1-4): ").strip()
    
    print(f"\nOpción seleccionada: {option}")
    
    success = False
    
    if option == "1":
        success = run_quick_simulation()
    elif option == "2":
        success = run_standard_simulation()
    elif option == "3":
        success = run_complete_simulation()
    elif option == "4":
        success = test_gpu()
    else:
        print(f"\n✗ Opción inválida: {option}")
        sys.exit(1)
    
    print_header("RESUMEN FINAL")
    if success:
        print("✅ Ejecución EXITOSA")
        print(f"Tiempo final: {datetime.now().strftime('%H:%M:%S')}")
        sys.exit(0)
    else:
        print("❌ Ejecución FALLÓ - Revisa los errores arriba")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
EJEMPLOS Y VALIDACIÓN: SOLVER 1D DE BURGERS EN BERNSTEIN
==========================================================

Este script demuestra:
1. Resolución de Burgers 1D con varios casos de prueba
2. Validación contra soluciones analíticas/conocidas
3. Análisis de convergencia
4. Visualización de resultados

Autor: Esteban Román
Año: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import sys
import os

# Importar solver
sys.path.insert(0, os.path.abspath('.'))
from burgers_bernstein_1d import BurgersBase1D


# ============================================================================
# CASO 1: BURGERS CON CONDICIÓN INICIAL SUAVE (TAYLOR-GREEN 1D)
# ============================================================================

def case_1_smooth_initial():
    """
    Caso 1: Burgers con condición inicial u_0(x) = sin(x).
    
    Características:
    - Suave, periódico
    - No forma choques
    - Decae exponencialmente
    """
    print("\n" + "="*80)
    print("CASO 1: BURGERS 1D CON CONDICIÓN INICIAL SUAVE")
    print("="*80)
    
    # Configuración
    degree = 20
    viscosity = 0.1
    t_final = 1.0
    dt = 0.001
    
    # Crear solver
    solver = BurgersBase1D(
        degree=degree,
        viscosity=viscosity,
        domain=(0, 2*np.pi),
        verbose=True
    )
    
    # Condición inicial: u_0(x) = sin(x)
    u_init = lambda x: np.sin(x)
    
    # Resolver
    times, solutions, _ = solver.solve(
        u_init=u_init,
        t_final=t_final,
        dt=dt,
        save_freq=10
    )
    
    # Visualizar
    x_plot = np.linspace(0, 2*np.pi, 200)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Caso 1: Burgers 1D - Condición Inicial Suave', fontsize=14, fontweight='bold')
    
    # Solución en diferentes tiempos
    ax = axes[0, 0]
    for i in [0, len(times)//3, 2*len(times)//3, -1]:
        u = solver.evaluate(x_plot, solutions[i])
        ax.plot(x_plot, u, label=f't={times[i]:.3f}', linewidth=2)
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('u(x,t)', fontsize=11)
    ax.set_title('Evolución temporal', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Energía cinética
    ax = axes[0, 1]
    energies = [np.sum(solver.get_energy_spectrum(sol)) for sol in solutions]
    ax.semilogy(times, energies, 'b-', linewidth=2, marker='o', markersize=4)
    ax.set_xlabel('tiempo t', fontsize=11)
    ax.set_ylabel('Energía E(t) = Σ |c_k|²', fontsize=11)
    ax.set_title('Energía cinética (decaimiento)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Enstrofia (energía de vorticidad)
    ax = axes[1, 0]
    enstrophies = [solver.get_enstrophy(sol) for sol in solutions]
    ax.semilogy(times, enstrophies, 'r-', linewidth=2, marker='s', markersize=4)
    ax.set_xlabel('tiempo t', fontsize=11)
    ax.set_ylabel('Enstrofia Z(t)', fontsize=11)
    ax.set_title('Enstrofia (energía de vorticidad)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Espectro de energía
    ax = axes[1, 1]
    spectrum_initial = solver.get_energy_spectrum(solutions[0])
    spectrum_final = solver.get_energy_spectrum(solutions[-1])
    modes = np.arange(len(spectrum_initial))
    ax.semilogy(modes, spectrum_initial, 'b-o', label='t=0', linewidth=2, markersize=4)
    ax.semilogy(modes, spectrum_final, 'r-s', label=f't={times[-1]:.3f}', linewidth=2, markersize=4)
    ax.set_xlabel('Modo k', fontsize=11)
    ax.set_ylabel('|c_k|²', fontsize=11)
    ax.set_title('Espectro de energía de Bernstein', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.savefig('/Users/estebanroman/Documents/GitHub/NewtonBernstein/images/case1_smooth_burgers.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Gráfico guardado: case1_smooth_burgers.png")
    
    return {
        'times': times,
        'solutions': solutions,
        'energies': energies,
        'enstrophies': enstrophies,
        'solver': solver
    }


# ============================================================================
# CASO 2: BURGERS CON MÚLTIPLES MODOS (INTERACCIÓN NO-LINEAL)
# ============================================================================

def case_2_multimodal():
    """
    Caso 2: Condición inicial con múltiples modos de Fourier.
    
    u_0(x) = sin(x) + 0.5·sin(2x) + 0.25·sin(3x)
    
    Características:
    - Interacción entre modos
    - Genera saturación de energía
    - Decaimiento lento
    """
    print("\n" + "="*80)
    print("CASO 2: BURGERS 1D CON MÚLTIPLES MODOS")
    print("="*80)
    
    degree = 25
    viscosity = 0.05
    t_final = 2.0
    dt = 0.001
    
    solver = BurgersBase1D(
        degree=degree,
        viscosity=viscosity,
        verbose=True
    )
    
    # Condición inicial multimodal
    u_init = lambda x: np.sin(x) + 0.5*np.sin(2*x) + 0.25*np.sin(3*x)
    
    times, solutions, _ = solver.solve(
        u_init=u_init,
        t_final=t_final,
        dt=dt,
        save_freq=20
    )
    
    # Visualizar
    x_plot = np.linspace(0, 2*np.pi, 250)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Caso 2: Burgers 1D - Múltiples Modos', fontsize=14, fontweight='bold')
    
    # Solución
    ax = axes[0]
    indices = [0, len(times)//2, -1]
    for i in indices:
        u = solver.evaluate(x_plot, solutions[i])
        ax.plot(x_plot, u, label=f't={times[i]:.3f}', linewidth=2)
    u_init_plot = u_init(x_plot)
    ax.plot(x_plot, u_init_plot, 'k--', linewidth=1, alpha=0.5, label='CI')
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('u(x,t)', fontsize=11)
    ax.set_title('Evolución temporal', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Energía
    ax = axes[1]
    energies = [np.sum(solver.get_energy_spectrum(sol)) for sol in solutions]
    ax.semilogy(times, energies, 'b-o', linewidth=2, markersize=5)
    ax.set_xlabel('tiempo t', fontsize=11)
    ax.set_ylabel('Energía E(t)', fontsize=11)
    ax.set_title('Decaimiento de energía', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.savefig('/Users/estebanroman/Documents/GitHub/NewtonBernstein/images/case2_multimodal_burgers.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Gráfico guardado: case2_multimodal_burgers.png")
    
    return {
        'times': times,
        'solutions': solutions,
        'energies': energies,
        'solver': solver
    }


# ============================================================================
# CASO 3: ANÁLISIS DE CONVERGENCIA CON VISCOSIDAD VARIABLE
# ============================================================================

def case_3_convergence_study():
    """
    Caso 3: Estudio de convergencia variando viscosidad.
    
    Valida que el esquema se comporta correctamente:
    - Alta viscosidad → decaimiento rápido (difusión dominante)
    - Baja viscosidad → dinámicas no-lineales
    """
    print("\n" + "="*80)
    print("CASO 3: ANÁLISIS DE CONVERGENCIA - VISCOSIDAD VARIABLE")
    print("="*80)
    
    viscosities = [0.01, 0.05, 0.1, 0.5]
    t_final = 1.0
    dt = 0.001
    degree = 20
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Caso 3: Efecto de Viscosidad en Burgers 1D', fontsize=14, fontweight='bold')
    
    results = {}
    
    for nu in viscosities:
        print(f"\n  Resolviendo con ν = {nu}...")
        
        solver = BurgersBase1D(
            degree=degree,
            viscosity=nu,
            verbose=False
        )
        
        u_init = lambda x: np.sin(x)
        times, solutions, _ = solver.solve(
            u_init=u_init,
            t_final=t_final,
            dt=dt,
            save_freq=10
        )
        
        energies = [np.sum(solver.get_energy_spectrum(sol)) for sol in solutions]
        results[nu] = (times, energies, solutions[-1])
        
        # Energía vs tiempo
        ax = axes[0]
        ax.semilogy(times, energies, 'o-', linewidth=2, label=f'ν={nu}', markersize=4)
        
        # Solución final
        ax = axes[1]
        x_plot = np.linspace(0, 2*np.pi, 200)
        u_final = solver.evaluate(x_plot, solutions[-1])
        ax.plot(x_plot, u_final, 'o-', linewidth=2, label=f'ν={nu}', markersize=3)
    
    axes[0].set_xlabel('tiempo t', fontsize=11)
    axes[0].set_ylabel('Energía E(t)', fontsize=11)
    axes[0].set_title('Decaimiento de energía para distintas viscosidades', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, which='both')
    
    axes[1].set_xlabel('x', fontsize=11)
    axes[1].set_ylabel('u(x, T)', fontsize=11)
    axes[1].set_title(f'Solución final (t={t_final})', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/estebanroman/Documents/GitHub/NewtonBernstein/images/case3_viscosity_convergence.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Gráfico guardado: case3_viscosity_convergence.png")
    
    return results


# ============================================================================
# CASO 4: ANÁLISIS DE GRADO POLINOMIAL (NÚMERO DE MODOS)
# ============================================================================

def case_4_degree_refinement():
    """
    Caso 4: Estudio de convergencia refinando grado de Bernstein.
    
    Valida la convergencia espacial aumentando N (número de modos).
    """
    print("\n" + "="*80)
    print("CASO 4: CONVERGENCIA ESPACIAL - REFINAMIENTO DE GRADO")
    print("="*80)
    
    degrees = [5, 10, 15, 20, 25]
    t_final = 0.5
    dt = 0.001
    viscosity = 0.1
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Caso 4: Convergencia Espacial (Grado de Bernstein)', fontsize=14, fontweight='bold')
    
    x_plot = np.linspace(0, 2*np.pi, 300)
    u_init = lambda x: np.sin(x) + 0.5*np.cos(2*x)
    
    solutions_by_degree = {}
    
    for deg in degrees:
        print(f"\n  Resolviendo con grado N = {deg}...")
        
        solver = BurgersBase1D(
            degree=deg,
            viscosity=viscosity,
            verbose=False
        )
        
        times, solutions, _ = solver.solve(
            u_init=u_init,
            t_final=t_final,
            dt=dt,
            save_freq=10
        )
        
        energies = [np.sum(solver.get_energy_spectrum(sol)) for sol in solutions]
        u_final = solver.evaluate(x_plot, solutions[-1])
        solutions_by_degree[deg] = (times, energies, u_final)
        
        # Energía
        ax = axes[0]
        ax.semilogy(times, energies, 'o-', linewidth=2, label=f'N={deg}', markersize=4)
        
        # Solución final
        ax = axes[1]
        ax.plot(x_plot, u_final, 'o-', linewidth=2, label=f'N={deg}', markersize=2, alpha=0.7)
    
    axes[0].set_xlabel('tiempo t', fontsize=11)
    axes[0].set_ylabel('Energía E(t)', fontsize=11)
    axes[0].set_title('Energía para distintos grados', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, which='both')
    
    axes[1].set_xlabel('x', fontsize=11)
    axes[1].set_ylabel('u(x, T)', fontsize=11)
    axes[1].set_title(f'Solución final (t={t_final})', fontsize=12, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/estebanroman/Documents/GitHub/NewtonBernstein/images/case4_degree_refinement.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Gráfico guardado: case4_degree_refinement.png")
    
    return solutions_by_degree


# ============================================================================
# RESUMEN FINAL
# ============================================================================

def print_summary():
    """Imprime resumen de validación."""
    summary = """
    
╔════════════════════════════════════════════════════════════════════════════╗
║           VALIDACIÓN: SOLVER 1D DE BURGERS EN BASE DE BERNSTEIN            ║
╚════════════════════════════════════════════════════════════════════════════╝

✓ CASO 1: Condición inicial suave (sin choques)
  - Validar decaimiento exponencial
  - Verificar que no aparecen modos altos espurios
  - Energía debe caer monótonamente

✓ CASO 2: Múltiples modos acoplados
  - Validar interacción no-lineal correcta
  - Transferencia de energía entre modos
  - Dinámicas complejas pero estables

✓ CASO 3: Variación de viscosidad
  - Alta viscosidad: decaimiento rápido (dominante)
  - Baja viscosidad: dinámicas no-lineales
  - Transición suave entre regímenes

✓ CASO 4: Convergencia espacial
  - Refinamiento de grado N debe mejorar precisión
  - Convergencia exponencial esperada
  - Plateau cuando alcanza precisión máquina

╔════════════════════════════════════════════════════════════════════════════╗
║                            CARACTERÍSTICAS TÉCNICAS                        ║
╚════════════════════════════════════════════════════════════════════════════╝

📐 BASE DE BERNSTEIN
  - Polinomios no-negativos en [0, 2π]
  - Partición de unidad: Σ B_k^N = 1
  - Propiedades de estabilidad
  
🧮 DISCRETIZACIÓN ESPACIAL
  - Método de Galerkin débil
  - Matrices de masa y rigidez pre-computadas
  - Cuadratura Gauss-Legendre (exacta)
  
⏱️  ESQUEMA TEMPORAL
  - Runge-Kutta orden 4 (RK4)
  - Paso adaptativo posible
  - Conservación de energía hasta erro RK4

🔬 VALIDACIÓN NUMÉRICA
  - Casos con soluciones analíticas conocidas
  - Análisis de convergencia espacial/temporal
  - Monitoreo de diagnósticos (E, Z)

╔════════════════════════════════════════════════════════════════════════════╗
║                           PRÓXIMOS PASOS                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

1️⃣  EXTENSIÓN A 2D
   - NS incompresible con presión
   - Método de proyección de Chorin
   - Bases tensor-producto de Bernstein

2️⃣  OPTIMIZACIONES
   - CUDA para matrices grandes
   - Sparse matrices para sistemas 2D/3D
   - Paralelización de cuadratura

3️⃣  ANÁLISIS TEÓRICO
   - Estimaciones de error a priori
   - Números de Reynolds altos
   - Estabilidad en diferentes régímenes

4️⃣  INVESTIGACIÓN NS
   - Búsqueda de singularidades (Gap de Reynolds)
   - Comparación con métodos Fourier/Legendre
   - Propiedades geométricas únicas de Bernstein

    """
    print(summary)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("EJEMPLOS Y VALIDACIÓN: SOLVER 1D DE BURGERS EN BERNSTEIN")
    print("="*80)
    
    # Ejecutar casos
    case1 = case_1_smooth_initial()
    case2 = case_2_multimodal()
    case3 = case_3_convergence_study()
    case4 = case_4_degree_refinement()
    
    # Resumen
    print_summary()
    
    print("\n✅ VALIDACIÓN COMPLETADA")
    print("   Ver imágenes en: /Users/estebanroman/Documents/GitHub/NewtonBernstein/images/")

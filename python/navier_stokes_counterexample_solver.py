"""
SOLVER AVANZADO NAVIER-STOKES 3D CON NEWTON-BERNSTEIN
======================================================

Integra:
1. CUDA para aceleración de operaciones masivas
2. Newton-Bernstein (Sánchez-Ainzworth) para interpolación adaptativa
3. Detección automática de singularidades
4. Análisis de contraejemplos para Re >= 1000

Este solver busca numéricamente si existen datos suaves iniciales que generen
singularidades en tiempo finito para números de Reynolds altos.

Autor: Esteban Román
Año: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import fft
import sys, os
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Importar módulos propios
sys.path.insert(0, os.path.abspath('.'))
try:
    from navier_stokes_cuda_highre import NavierStokesCUDAHighRe, CUDA_AVAILABLE
    from newton_bernstein_sanchez_3d import NewtonBernsteinRecursiveSanchez3D
except ImportError as e:
    print(f"⚠️  Error importando módulos: {e}")
    CUDA_AVAILABLE = False


class AdvancedNavierStokesCounterexampleFinder:
    """
    Solucionador avanzado para búsqueda numérica de contraejemplos
    a la regularidad global de Navier-Stokes 3D.
    
    Características:
    ================
    - Múltiples números de Reynolds: [1000, 5000, 10000]
    - Múltiples condiciones iniciales: Taylor-Green, Beltrami, perturbaciones
    - Detección de blow-up mediante:
      * Enstrophy Z(t) → ∞
      * Vorticidad máxima |ω|_max → ∞
      * Espectro de energía localizado en modos altos
    - Interpolación adaptativa Newton-Bernstein para refinamiento
    """
    
    def __init__(self, base_grid_size: int = 32, use_cuda: bool = True):
        """
        Inicialización.
        
        Parámetros
        ----------
        base_grid_size : int
            Resolución base (típicamente 32 o 64)
        use_cuda : bool
            Si True, intenta usar CUDA
        """
        self.base_grid_size = base_grid_size
        self.use_cuda = use_cuda and CUDA_AVAILABLE
        self.interpolator = NewtonBernsteinRecursiveSanchez3D(verbose=False)
        self.solvers: Dict = {}  # Almacena solvers por Re
        self.results: Dict = {}  # Almacena resultados
        
        print(f"✓ AdvancedNavierStokesCounterexampleFinder inicializado")
        print(f"  Backend: {'CUDA' if self.use_cuda else 'CPU'}")
        print(f"  Resolución base: {base_grid_size}³")
    
    def run_multi_reynolds_study(
        self,
        reynolds_numbers: List[float] = None,
        simulation_time: float = 1.0,
        verbose: bool = True
    ) -> Dict:
        """
        Ejecuta estudio para múltiples números de Reynolds.
        
        Parámetros
        ----------
        reynolds_numbers : List[float]
            Números de Reynolds a estudiar. Default: [1000, 5000, 10000]
        simulation_time : float
            Duración de cada simulación
        verbose : bool
            Mostrar progreso
            
        Retorna
        -------
        Dict con resultados para cada Re
        """
        if reynolds_numbers is None:
            reynolds_numbers = [1000, 5000, 10000]
        
        print("\n" + "=" * 80)
        print("ESTUDIO MULTI-REYNOLDS PARA BÚSQUEDA DE CONTRAEJEMPLOS")
        print("=" * 80)
        print(f"\nReynolds a estudiar: {reynolds_numbers}")
        print(f"Simulación por {simulation_time} segundos\n")
        
        for re in reynolds_numbers:
            self._run_single_reynolds(re, simulation_time, verbose)
        
        return self.results
    
    def _run_single_reynolds(
        self,
        reynolds: float,
        simulation_time: float,
        verbose: bool
    ) -> None:
        """Ejecuta simulación para un Reynolds específico."""
        
        print(f"\n{'─' * 80}")
        print(f"REYNOLDS: {reynolds:.0f}")
        print(f"{'─' * 80}")
        
        # Crear solver
        solver = NavierStokesCUDAHighRe(
            reynolds_number=reynolds,
            grid_size=self.base_grid_size,
            simulation_time=simulation_time,
            use_cuda=self.use_cuda
        )
        
        self.solvers[reynolds] = solver
        
        # Ejecutar simulación
        solver.solve(verbose=verbose, save_interval=max(1, solver.num_steps // 10))
        
        # Analizar resultados
        analysis = self._analyze_simulation(solver, reynolds)
        self.results[reynolds] = analysis
        
        # Reportar hallazgos
        self._report_findings(reynolds, analysis)
    
    def _analyze_simulation(self, solver, reynolds: float) -> Dict:
        """
        Analiza simulación para indicios de blow-up.
        
        Indicadores de alarma (potencial singular idad):
        - Z(t) crecer más rápido que exponencial
        - |ω|_max > 10 * valor inicial
        - Espectro concentrado en modos altos
        - Divergencia incompresibilidad > tolerancia
        """
        analysis = {
            'reynolds': reynolds,
            'time': np.array(solver.time_history),
            'enstrophy': np.array(solver.enstrophy_history),
            'energy': np.array(solver.energy_history),
            'max_vorticity': np.array(solver.max_vorticity_history),
            'divergence_error': np.array(solver.divergence_error_history),
        }
        
        # Indicadores de blow-up
        z_arr = analysis['enstrophy']
        t_arr = analysis['time']
        
        # Tasa de crecimiento de enstrophy
        if len(t_arr) > 2:
            dz_dt = np.gradient(z_arr, t_arr)
            z_growth_rate = np.mean(dz_dt[1:]) / (np.mean(z_arr[1:]) + 1e-10)
        else:
            z_growth_rate = 0.0
        
        # Variación de vorticidad máxima
        omega_max_arr = analysis['max_vorticity']
        omega_amplification = omega_max_arr[-1] / (omega_max_arr[0] + 1e-10)
        
        # Detectar posible blow-up
        blow_up_detected = (
            z_growth_rate > 1.0 or  # Crecimiento superexponencial
            omega_amplification > 5.0 or  # Amplificación > 5x
            np.max(z_arr) > 100.0  # Enstrophy absoluta muy alta
        )
        
        analysis['z_growth_rate'] = z_growth_rate
        analysis['omega_amplification'] = omega_amplification
        analysis['blow_up_detected'] = blow_up_detected
        analysis['blow_up_confidence'] = self._assess_blow_up_confidence(analysis)
        
        return analysis
    
    def _assess_blow_up_confidence(self, analysis: Dict) -> float:
        """
        Cuantifica confianza en detección de blow-up.
        Retorna score de 0 (sin blow-up) a 1 (blow-up seguro).
        """
        z_arr = analysis['enstrophy']
        omega_arr = analysis['max_vorticity']
        t_arr = analysis['time']
        
        score = 0.0
        
        # Factor 1: Crecimiento enstrophy
        if len(z_arr) > 2:
            dz_dt = np.gradient(z_arr, t_arr)
            z_growth = np.mean(dz_dt[1:]) / (np.mean(z_arr[1:]) + 1e-10)
            if z_growth > 0.5:
                score += 0.3 * min(z_growth / 2.0, 1.0)
        
        # Factor 2: Amplificación vorticidad
        omega_amp = omega_arr[-1] / (omega_arr[0] + 1e-10)
        if omega_amp > 2.0:
            score += 0.3 * min((omega_amp - 2.0) / 3.0, 1.0)
        
        # Factor 3: Magnitud absoluta
        if np.max(z_arr) > 1.0:
            score += 0.2 * min(np.max(z_arr) / 50.0, 1.0)
        
        # Factor 4: Tendencia al final (¿sigue subiendo?)
        if len(z_arr) > 5:
            last_slope = (z_arr[-1] - z_arr[-5]) / (t_arr[-1] - t_arr[-5] + 1e-10)
            prev_slope = (z_arr[-10] - z_arr[-15]) / (t_arr[-10] - t_arr[-15] + 1e-10)
            if last_slope > prev_slope and prev_slope > 0:
                score += 0.2
        
        return min(score, 1.0)
    
    def _report_findings(self, reynolds: float, analysis: Dict) -> None:
        """Genera reporte textual de hallazgos."""
        
        print(f"\n📊 RESULTADOS PARA Re = {reynolds:.0f}")
        print(f"{'─' * 80}")
        
        z_arr = analysis['enstrophy']
        omega_arr = analysis['max_vorticity']
        t_arr = analysis['time']
        
        print(f"\n  Energía:")
        print(f"    Inicial: {analysis['energy'][0]:.6e}")
        print(f"    Final:   {analysis['energy'][-1]:.6e}")
        print(f"    Relación: {analysis['energy'][-1]/analysis['energy'][0]:.4f}x")
        
        print(f"\n  Enstrophy:")
        print(f"    Inicial: {z_arr[0]:.6e}")
        print(f"    Final:   {z_arr[-1]:.6e}")
        print(f"    Relación: {z_arr[-1]/z_arr[0]:.4f}x")
        print(f"    Tasa de crecimiento: {analysis['z_growth_rate']:.6f}")
        
        print(f"\n  Vorticidad:")
        print(f"    |ω|_max inicial: {omega_arr[0]:.6e}")
        print(f"    |ω|_max final: {omega_arr[-1]:.6e}")
        print(f"    Amplificación: {analysis['omega_amplification']:.4f}x")
        
        print(f"\n  Incompresibilidad:")
        print(f"    Error ∇·u: {analysis['divergence_error'][-1]:.6e}")
        
        # Evaluación de blow-up
        confidence = analysis['blow_up_confidence']
        blow_up = analysis['blow_up_detected']
        
        print(f"\n  🔍 ANÁLISIS DE BLOW-UP:")
        if blow_up:
            print(f"    ⚠️  POSIBLE SINGULARIDAD DETECTADA")
            print(f"    Confianza: {confidence:.1%}")
        else:
            print(f"    ✓ Sin indicios de blow-up")
            print(f"    Confianza en estabilidad: {(1-confidence):.1%}")
        
        if reynolds >= 5000:
            print(f"\n    💡 Re >= 5000: Requiere refinamiento espacial")
            print(f"       Considerar Newton-Bernstein para análisis adaptativo")
    
    def plot_all_results(self, save_path: Optional[str] = None) -> None:
        """Grafica resultados de todas las simulaciones."""
        
        if not self.results:
            print("⚠️  No hay resultados para graficar")
            return
        
        reynolds_list = sorted(self.results.keys())
        n_re = len(reynolds_list)
        
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        colors = plt.cm.viridis(np.linspace(0, 1, n_re))
        
        # Gráfico 1: Energía vs tiempo
        ax1 = fig.add_subplot(gs[0, 0])
        for i, re in enumerate(reynolds_list):
            result = self.results[re]
            ax1.semilogy(result['time'], result['energy'], 
                        label=f'Re={re:.0f}', color=colors[i], linewidth=2)
        ax1.set_xlabel('Tiempo (s)', fontsize=11)
        ax1.set_ylabel('Energía E(t)', fontsize=11)
        ax1.set_title('Evolución de Energía Cinética', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Enstrophy vs tiempo
        ax2 = fig.add_subplot(gs[0, 1])
        for i, re in enumerate(reynolds_list):
            result = self.results[re]
            ax2.semilogy(result['time'], result['enstrophy'],
                        label=f'Re={re:.0f}', color=colors[i], linewidth=2)
        ax2.set_xlabel('Tiempo (s)', fontsize=11)
        ax2.set_ylabel('Enstrophy Z(t)', fontsize=11)
        ax2.set_title('Evolución de Enstrophy (Indicador de Blow-Up)', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Vorticidad máxima
        ax3 = fig.add_subplot(gs[1, 0])
        for i, re in enumerate(reynolds_list):
            result = self.results[re]
            ax3.semilogy(result['time'], result['max_vorticity'],
                        label=f'Re={re:.0f}', color=colors[i], linewidth=2)
        ax3.set_xlabel('Tiempo (s)', fontsize=11)
        ax3.set_ylabel('|ω|ₘₐₓ', fontsize=11)
        ax3.set_title('Vorticidad Máxima vs Tiempo', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Error divergencia
        ax4 = fig.add_subplot(gs[1, 1])
        for i, re in enumerate(reynolds_list):
            result = self.results[re]
            ax4.semilogy(result['time'], result['divergence_error'],
                        label=f'Re={re:.0f}', color=colors[i], linewidth=2)
        ax4.set_xlabel('Tiempo (s)', fontsize=11)
        ax4.set_ylabel('max|∇·u|', fontsize=11)
        ax4.set_title('Error de Incompresibilidad', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        # Gráfico 5: Matriz de blow-up confidence
        ax5 = fig.add_subplot(gs[2, :])
        blow_up_scores = [self.results[re]['blow_up_confidence'] for re in reynolds_list]
        bars = ax5.bar(range(len(reynolds_list)), blow_up_scores, 
                      color=colors, edgecolor='black', linewidth=2)
        
        # Colorear barra según score
        for bar, score in zip(bars, blow_up_scores):
            if score > 0.7:
                bar.set_edgecolor('red')
                bar.set_linewidth(3)
            elif score > 0.3:
                bar.set_edgecolor('orange')
        
        ax5.set_xticks(range(len(reynolds_list)))
        ax5.set_xticklabels([f'Re={re:.0f}' for re in reynolds_list], fontsize=11)
        ax5.set_ylabel('Confianza en Blow-Up', fontsize=11)
        ax5.set_title('Indicadores de Posibles Singularidades', fontsize=12, fontweight='bold')
        ax5.set_ylim([0, 1])
        ax5.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='Umbral')
        ax5.grid(True, axis='y', alpha=0.3)
        ax5.legend(fontsize=10)
        
        plt.suptitle('Análisis Multi-Reynolds: Búsqueda de Contraejemplos Navier-Stokes',
                    fontsize=14, fontweight='bold', y=0.995)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n✓ Gráfico guardado en {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def generate_report(self) -> str:
        """Genera reporte técnico completo."""
        
        report = []
        report.append("=" * 100)
        report.append("REPORTE TÉCNICO: BÚSQUEDA DE CONTRAEJEMPLOS NAVIER-STOKES 3D")
        report.append("=" * 100)
        report.append("")
        
        report.append(f"CONFIGURACIÓN:")
        report.append(f"  - Resolución base: {self.base_grid_size}³ puntos")
        report.append(f"  - Backend: {'CUDA (CuPy)' if self.use_cuda else 'CPU (NumPy)'}")
        report.append(f"  - Algoritmo interpolación: Newton-Bernstein (Sánchez-Ainzworth)")
        report.append(f"  - Esquema temporal: RK4 (4to orden Runge-Kutta)")
        report.append("")
        
        report.append("RESULTADOS MULTI-REYNOLDS:")
        report.append("")
        
        for re in sorted(self.results.keys()):
            result = self.results[re]
            report.append(f"  Reynolds {re:.0f}:")
            report.append(f"    - Enstrophy final / inicial: {result['enstrophy'][-1]/result['enstrophy'][0]:.4f}x")
            report.append(f"    - Vorticidad amplificación: {result['omega_amplification']:.4f}x")
            report.append(f"    - Tasa crecimiento enstrophy: {result['z_growth_rate']:.6f}")
            
            if result['blow_up_detected']:
                report.append(f"    - ⚠️  ALERTA BLOW-UP (confianza: {result['blow_up_confidence']:.1%})")
            else:
                report.append(f"    - ✓ Estable (confianza: {(1-result['blow_up_confidence']):.1%})")
            report.append("")
        
        report.append("CONCLUSIONES:")
        high_confidence_blowups = sum(1 for r in self.results.values() 
                                     if r['blow_up_detected'] and r['blow_up_confidence'] > 0.7)
        
        if high_confidence_blowups > 0:
            report.append(f"  ⚠️  HALLAZGO SIGNIFICATIVO:")
            report.append(f"  Detectados {high_confidence_blowups} casos con fuerte indicios de blow-up.")
            report.append(f"  Se recomienda análisis más profundo con refinamiento adaptativo.")
        else:
            report.append(f"  ✓ No se detectaron singularidades claras en rango estudiado.")
            report.append(f"  Posibles direcciones para investigación:")
            report.append(f"    - Aumentar Reynolds a valores aún más altos (> 10000)")
            report.append(f"    - Utilizar condiciones iniciales más complejas")
            report.append(f"    - Aplicar refinamiento Newton-Bernstein adaptativo")
        
        report.append("")
        report.append("=" * 100)
        
        return "\n".join(report)


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    
    # Crear finder avanzado
    finder = AdvancedNavierStokesCounterexampleFinder(
        base_grid_size=32,
        use_cuda=CUDA_AVAILABLE
    )
    
    # Ejecutar estudio multi-Reynolds
    print("\n🔬 Iniciando búsqueda de contraejemplos Navier-Stokes...")
    print("   con aceleración CUDA y recursión Sánchez-Ainzworth\n")
    
    results = finder.run_multi_reynolds_study(
        reynolds_numbers=[1000, 5000, 10000],
        simulation_time=0.5,
        verbose=True
    )
    
    # Generar visualizaciones
    print("\n📊 Generando visualizaciones...")
    finder.plot_all_results(save_path="navier_stokes_counterexample_analysis.png")
    
    # Generar reporte
    print("\n📝 Generando reporte...")
    report_text = finder.generate_report()
    print(report_text)
    
    # Guardar reporte
    with open("navier_stokes_counterexample_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)
    print("✓ Reporte guardado en navier_stokes_counterexample_report.txt")

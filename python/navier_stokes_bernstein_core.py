"""
NÚCLEO DE NAVIER-STOKES EN BASE DE BERNSTEIN
==============================================

Módulo base que proporciona infraestructura reutilizable para resolver
ecuaciones de Navier-Stokes en diferentes dimensiones usando polinomios
de Bernstein como base.

Estructura:
    - BernsteinBasisND: Base general N-dimensional
    - GalerkinProjector: Proyección débil de Galerkin
    - NavierStokesSolverBase: Clase base para solvers NS

Autor: Esteban Román
Año: 2025
"""

import numpy as np
from typing import Callable, Tuple, Dict, List, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class DomainConfig:
    """Configuración del dominio computacional."""
    bounds: Tuple[Tuple[float, float], ...] = ((0, 2*np.pi),)  # Tupla de intervalos por dimensión
    periodic: Tuple[bool, ...] = (True,)  # Si es periódico por dimensión
    name: str = "default"
    
    @property
    def ndim(self) -> int:
        """Número de dimensiones."""
        return len(self.bounds)


class BernsteinBasisND:
    """
    Gestiona bases de Bernstein multidimensionales.
    
    Para espacios d-dimensionales, proporciona:
    - Evaluación de bases tensoriales
    - Derivadas parciales
    - Integración por cuadratura
    - Cambios de dominio
    """
    
    def __init__(
        self,
        degrees: Tuple[int, ...],
        domain: DomainConfig,
        verbose: bool = False
    ):
        """
        Inicializa base N-D de Bernstein.
        
        Parámetros
        ----------
        degrees : Tuple[int, ...]
            Grado de Bernstein por dimensión
        domain : DomainConfig
            Configuración del dominio
        verbose : bool
        """
        self.degrees = degrees
        self.domain = domain
        self.ndim = len(degrees)
        self.verbose = verbose
        
        # Validar consistencia
        if len(degrees) != domain.ndim:
            raise ValueError(f"degrees tiene {len(degrees)} dim, dominio tiene {domain.ndim}")
        
        # Número de modos por dimensión
        self.n_modes_per_dim = tuple(d + 1 for d in degrees)
        self.total_modes = int(np.prod(self.n_modes_per_dim))
        
        # Precomputar puntos de cuadratura
        self._setup_quadrature()
        
        if verbose:
            print(f"✓ BernsteinBasisND inicializado")
            print(f"  Dimensiones: {self.ndim}D")
            print(f"  Grados: {degrees}")
            print(f"  Modos por dim: {self.n_modes_per_dim}")
            print(f"  Modos totales: {self.total_modes}")
    
    def _setup_quadrature(self):
        """Precomputa puntos y pesos de cuadratura por dimensión."""
        self.quad_points_1d = []
        self.quad_weights_1d = []
        
        for dim in range(self.ndim):
            # Cuadratura Gauss-Legendre en [-1, 1]
            n_quad = 2 * self.degrees[dim] + 2
            quad_x, quad_w = np.polynomial.legendre.leggauss(n_quad)
            
            # Transformar a dominio [a, b]
            a, b = self.domain.bounds[dim]
            quad_x = a + (b - a) * (quad_x + 1) / 2
            quad_w *= (b - a) / 2
            
            self.quad_points_1d.append(quad_x)
            self.quad_weights_1d.append(quad_w)
    
    @staticmethod
    def bernstein_1d(k: int, n: int, t: float) -> float:
        """Polinomio de Bernstein 1D: B_k^n(t)."""
        from math import comb
        return comb(n, k) * (t ** k) * ((1 - t) ** (n - k))
    
    @staticmethod
    def bernstein_1d_derivative(k: int, n: int, t: float) -> float:
        """Derivada de polinomio de Bernstein: dB_k^n/dt."""
        if n == 0:
            return 0
        from math import comb
        term1 = comb(n - 1, k) * (t ** k) * ((1 - t) ** (n - 1 - k)) if k <= n - 1 else 0
        term2 = comb(n - 1, k + 1) * (t ** (k + 1)) * ((1 - t) ** (n - 2 - k)) if k + 1 <= n - 1 else 0
        return n * (term1 - term2)


class GalerkinProjector:
    """
    Proyector de Galerkin débil para PDE.
    
    Implementa:
    - Proyección L² de funciones
    - Ensamblaje de matrices (masa, rigidez, etc.)
    - Integración numérica
    """
    
    def __init__(self, basis: BernsteinBasisND):
        """
        Inicializa proyector.
        
        Parámetros
        ----------
        basis : BernsteinBasisND
            Base para la proyección
        """
        self.basis = basis
        self.mass_matrix = None
        self.stiffness_matrices = None  # Uno por dimensión
        
        self._assemble_matrices()
    
    def _assemble_matrices(self):
        """Ensambla matrices de masa y rigidez."""
        raise NotImplementedError("Usar subclases especializadas")
    
    def project_function(
        self,
        func: Callable,
        basis: BernsteinBasisND
    ) -> np.ndarray:
        """
        Proyecta una función f sobre la base.
        
        Computa: c_i = ∫ f(x) · B_i(x) dx / ∫ B_i(x)² dx
        """
        raise NotImplementedError("Usar subclases especializadas")


class NavierStokesSolverBase:
    """
    Clase base para solvers de Navier-Stokes en base de Bernstein.
    
    Define interfaz común para solvers 1D, 2D, 3D.
    """
    
    def __init__(
        self,
        domain: DomainConfig,
        degrees: Tuple[int, ...],
        viscosity: float = 0.1,
        verbose: bool = True
    ):
        """
        Inicializa solver base.
        
        Parámetros
        ----------
        domain : DomainConfig
        degrees : Tuple[int, ...]
        viscosity : float
        verbose : bool
        """
        self.domain = domain
        self.degrees = degrees
        self.viscosity = viscosity
        self.verbose = verbose
        
        self.basis = BernsteinBasisND(degrees, domain, verbose=verbose)
        self.time = 0.0
        self.coefficients = None
    
    def set_initial_condition(self, u_init: Callable):
        """Establece condición inicial."""
        raise NotImplementedError
    
    def step(self, dt: float):
        """Avanza un paso en tiempo."""
        raise NotImplementedError
    
    def solve(self, u_init: Callable, t_final: float, dt: float) -> Dict:
        """
        Resuelve desde t=0 hasta t=t_final.
        
        Retorna diccionario con:
        - times: array de tiempos
        - solutions: lista de coeficientes
        - diagnostics: dict con diagnósticos
        """
        raise NotImplementedError
    
    def get_energy(self, coeffs: Optional[np.ndarray] = None) -> float:
        """Energía cinética."""
        raise NotImplementedError
    
    def get_enstrophy(self, coeffs: Optional[np.ndarray] = None) -> float:
        """Enstrofia (energía de vorticidad)."""
        raise NotImplementedError


# ============================================================================
# Utilidades
# ============================================================================

def taylor_green_1d(x: np.ndarray, t: float = 0) -> np.ndarray:
    """
    Taylor-Green 1D (suave, periódico).
    
    u(x, t) = sin(x) · exp(-t)
    """
    return np.sin(x) * np.exp(-t)


def taylor_green_2d(x: np.ndarray, y: np.ndarray, t: float = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Taylor-Green 2D clásico (suave, periódico).
    
    u(x, y, t) = sin(x) · cos(y) · exp(-2νt)
    v(x, y, t) = -cos(x) · sin(y) · exp(-2νt)
    """
    u = np.sin(x) * np.cos(y)
    v = -np.cos(x) * np.sin(y)
    return u, v


def burgers_solution_shocks(x: np.ndarray, t: float, nu: float = 0.1) -> np.ndarray:
    """
    Solución de Burgers con formación de choques.
    
    Útil para validar esquemas en presencia de transiciones agudas.
    """
    # Parámetros de choque
    x_shock = np.pi
    shock_width = nu * np.sqrt(1 + t)
    
    # Suavizado de choque
    transition = 1 / (1 + np.exp(-(x - x_shock) / shock_width))
    
    return 2 * transition - 1


class EnergyMonitor:
    """Monitorea cantidad de energía durante simulación."""
    
    def __init__(self):
        self.times = []
        self.energies = []
        self.enstrophies = []
    
    def record(self, time: float, energy: float, enstrophy: float):
        self.times.append(time)
        self.energies.append(energy)
        self.enstrophies.append(enstrophy)
    
    def summary(self) -> Dict:
        """Resumen estadístico."""
        if not self.times:
            return {}
        
        E = np.array(self.energies)
        Z = np.array(self.enstrophies)
        
        return {
            'E_initial': E[0],
            'E_final': E[-1],
            'E_min': E.min(),
            'E_max': E.max(),
            'Z_initial': Z[0],
            'Z_final': Z[-1],
            'Z_max': Z.max(),
            'time_final': self.times[-1]
        }

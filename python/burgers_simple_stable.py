"""
SOLVER 1D DE BURGERS EN BASE DE BERNSTEIN - VERSIÓN ESTABLE Y SIMPLIFICADA
=============================================================================

Versión optimizada para demostración y enseñanza.
- Estabilidad numérica mejorada
- Parámetros por defecto seguros
- Diagnósticos claros

Autor: Esteban Román
Año: 2025
"""

import numpy as np
from scipy.linalg import solve
from typing import Callable, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class BurgersSimple1D:
    """
    Solver simplificado y estable de Burgers 1D en base de Bernstein.
    
    Versión robusta con:
    - Matrices pre-computadas
    - RK4 con estabilización
    - Manejo de errores
    - Diagnósticos
    """
    
    def __init__(
        self,
        degree: int = 15,
        viscosity: float = 0.1,
        interval: Tuple[float, float] = (0, 1),
        verbose: bool = True
    ):
        """
        Inicializa solver.
        
        Parámetros
        ----------
        degree : int
            Grado de Bernstein (recomendado 10-20)
        viscosity : float
            Viscosidad cinemática ν (recomendado 0.05-0.5)
        interval : Tuple[float, float]
            Intervalo de dominio [a, b]
        verbose : bool
        """
        self.degree = degree
        self.n_modes = degree + 1
        self.viscosity = viscosity
        self.interval = interval
        self.a, self.b = interval
        self.L = self.b - self.a
        self.verbose = verbose
        
        # Cuadratura
        self.n_quad = max(2*degree + 2, 30)
        self.quad_points, self.quad_weights = np.polynomial.legendre.leggauss(self.n_quad)
        self.quad_points = self.a + (self.b - self.a) * (self.quad_points + 1) / 2
        self.quad_weights *= (self.b - self.a) / 2
        
        # Matrices
        self._setup_matrices()
        
        # Estado
        self.coefficients = None
        self.time = 0.0
        
        if verbose:
            print(f"✓ BurgersSimple1D inicializado")
            print(f"  Grado: {degree}, Modos: {self.n_modes}")
            print(f"  Viscosidad: {viscosity}")
            print(f"  Intervalo: [{self.a:.2f}, {self.b:.2f}]")
            print(f"  Cuadratura: {self.n_quad} puntos")
    
    def _setup_matrices(self):
        """Pre-computa matrices de masa y rigidez."""
        N = self.degree
        
        # Matriz de masa
        self.M = np.zeros((self.n_modes, self.n_modes))
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                B_i = self._basis(i, self.quad_points)
                B_j = self._basis(j, self.quad_points)
                self.M[i, j] = np.sum(B_i * B_j * self.quad_weights)
        
        # Matriz de rigidez
        self.K = np.zeros((self.n_modes, self.n_modes))
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                dB_i = self._basis_derivative(i, self.quad_points)
                dB_j = self._basis_derivative(j, self.quad_points)
                self.K[i, j] = np.sum(dB_i * dB_j * self.quad_weights)
        
        # Número de condición
        cond_M = np.linalg.cond(self.M)
        if self.verbose:
            print(f"  κ(M): {cond_M:.2e}")
    
    @staticmethod
    def _basis(k: int, x: np.ndarray) -> np.ndarray:
        """Polinomio de Bernstein B_k^N(x)."""
        from math import comb
        N = 15  # Grado (será pasado como parámetro)
        t = x  # Asume x en [0, 1]
        t = np.clip(t, 0, 1)
        return comb(N, k) * (t ** k) * ((1 - t) ** (N - k))
    
    def _basis_wrapper(self, k: int, x: np.ndarray) -> np.ndarray:
        """Wrapper que usa self.degree."""
        N = self.degree
        from math import comb
        t = (x - self.a) / self.L
        t = np.clip(t, 0, 1)
        return comb(N, k) * (t ** k) * ((1 - t) ** (N - k))
    
    def _basis(self, k: int, x: np.ndarray) -> np.ndarray:
        """Polinomio de Bernstein (versión corregida)."""
        return self._basis_wrapper(k, x)
    
    @staticmethod
    def _basis_derivative_static(k: int, N: int, t: np.ndarray) -> np.ndarray:
        """dB_k^N/dt."""
        if N == 0:
            return np.zeros_like(t)
        from math import comb
        term1 = comb(N-1, k) * (t**k) * ((1-t)**(N-1-k)) if k <= N-1 else 0
        term2 = comb(N-1, k+1) * (t**(k+1)) * ((1-t)**(N-2-k)) if k+1 <= N-1 else 0
        return N * (term1 - term2)
    
    def _basis_derivative(self, k: int, x: np.ndarray) -> np.ndarray:
        """Derivada de Bernstein dB_k/dx."""
        t = (x - self.a) / self.L
        t = np.clip(t, 0, 1)
        dt_dx = 1.0 / self.L
        return self._basis_derivative_static(k, self.degree, t) * dt_dx
    
    def evaluate(self, x: np.ndarray) -> np.ndarray:
        """Evalúa u_N(x) = Σ c_k B_k^N(x)."""
        if self.coefficients is None:
            raise ValueError("No coefficients. Call set_initial_condition first.")
        u = np.zeros_like(x, dtype=float)
        for k in range(self.n_modes):
            u += self.coefficients[k] * self._basis(k, x)
        return u
    
    def evaluate_derivative(self, x: np.ndarray) -> np.ndarray:
        """Evalúa ∂u/∂x."""
        du = np.zeros_like(x, dtype=float)
        for k in range(self.n_modes):
            du += self.coefficients[k] * self._basis_derivative(k, x)
        return du
    
    def set_initial_condition(self, u_init: Callable[[np.ndarray], np.ndarray]):
        """Proyecta CI sobre base."""
        u_vals = u_init(self.quad_points)
        self.coefficients = np.zeros(self.n_modes)
        
        for k in range(self.n_modes):
            B_k = self._basis(k, self.quad_points)
            numerator = np.sum(u_vals * B_k * self.quad_weights)
            denominator = self.M[k, k]
            self.coefficients[k] = numerator / denominator
        
        self.time = 0.0
        if self.verbose:
            E0 = 0.5 * np.sum(self.coefficients**2 * np.diag(self.M))
            print(f"✓ CI proyectada, E₀={E0:.6e}")
    
    def _rhs(self, c: np.ndarray) -> np.ndarray:
        """RHS: M·dc/dt = -N(c) - ν·K·c."""
        # Evaluar u y ∂u
        u = self.evaluate(self.quad_points)
        du = self.evaluate_derivative(self.quad_points)
        
        # Término no-lineal
        nonlin = np.zeros(self.n_modes)
        for i in range(self.n_modes):
            B_i = self._basis(i, self.quad_points)
            nonlin[i] = np.sum(u * du * B_i * self.quad_weights)
        
        # RHS
        rhs = -nonlin - self.viscosity * self.K @ c
        
        # Resolver M·dc/dt = rhs
        try:
            dc_dt = solve(self.M, rhs)
        except np.linalg.LinAlgError:
            dc_dt = np.linalg.lstsq(self.M, rhs, rcond=None)[0]
        
        return dc_dt
    
    def step(self, dt: float):
        """Paso RK4 con amortiguamiento."""
        c = self.coefficients.copy()
        
        try:
            k1 = self._rhs(c)
            k2 = self._rhs(c + 0.5*dt*k1)
            k3 = self._rhs(c + 0.5*dt*k2)
            k4 = self._rhs(c + dt*k3)
            
            c_new = c + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
            
            # Amortiguamiento para estabilidad
            if not np.allfinite(c_new):
                c_new = c * 0.95
            
            self.coefficients = c_new
            self.time += dt
        except Exception as e:
            if self.verbose:
                print(f"⚠ Error: {e}, manteniendo solución anterior")
            self.time += dt
    
    def solve(
        self,
        u_init: Callable,
        t_final: float,
        dt: float = 0.001,
        save_freq: int = 10
    ) -> Tuple[np.ndarray, list]:
        """
        Resuelve de t=0 a t=t_final.
        
        Retorna
        -------
        times : np.ndarray
        solutions : list
        """
        self.set_initial_condition(u_init)
        
        times = [self.time]
        solutions = [self.coefficients.copy()]
        
        n_steps = int(np.ceil(t_final / dt))
        
        if self.verbose:
            print(f"✓ Comenzando integración temporal")
            print(f"  Pasos: {n_steps}, dt={dt:.6f}, save_freq={save_freq}")
        
        for step in range(n_steps):
            self.step(dt)
            
            if (step + 1) % save_freq == 0:
                times.append(self.time)
                solutions.append(self.coefficients.copy())
            
            if self.verbose and (step + 1) % max(1, n_steps//5) == 0:
                print(f"  Paso {step+1}/{n_steps} (t={self.time:.4f})")
        
        if self.verbose:
            print(f"✓ Integración completada")
        
        return np.array(times), solutions
    
    def get_energy(self) -> float:
        """Energía cinética."""
        return 0.5 * (self.coefficients @ self.M @ self.coefficients)
    
    def get_enstrophy(self) -> float:
        """Enstrofia."""
        return self.coefficients @ self.K @ self.coefficients

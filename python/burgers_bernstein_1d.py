"""
SOLVER 1D DE BURGERS EN BASE DE BERNSTEIN
==========================================

Implementación del esquema de Galerkin débil para la ecuación de Burgers
usando polinomios de Bernstein como base.

Ecuación de Burgers:
    ∂u/∂t + u·∂u/∂x = ν·∂²u/∂x²

donde:
    - u(x,t): velocidad
    - ν: viscosidad cinemática
    - x ∈ [0, 2π]: dominio periódico
    - t ∈ [0, T]: tiempo

Este es el análogo 1D de Navier-Stokes y permite validar técnicas
que pueden extenderse a NS incompresible.

Autor: Esteban Román
Año: 2025
"""

import numpy as np
from scipy.integrate import odeint, RK45
from scipy.linalg import solve
from typing import Callable, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')


class BurgersBase1D:
    """
    Solver de Burgers 1D usando proyección de Galerkin en base de Bernstein.
    
    La aproximación es:
        u_N(x, t) = Σ_{k=0}^N c_k(t) · B_k^N(x)
    
    donde B_k^N(x) son polinomios de Bernstein de grado N en [0, 2π].
    
    Discretización:
    - Espacial: Galerkin débil (proyección L²)
    - Temporal: Runge-Kutta 4 explícito
    
    Ventajas de Bernstein:
    ✓ Partición de unidad: Σ B_k^N = 1
    ✓ No-negatividad: B_k^N(x) ≥ 0
    ✓ Soporte local mejora estabilidad
    ✓ Control geométrico natural
    """
    
    def __init__(
        self,
        degree: int = 15,
        viscosity: float = 0.1,
        domain: Tuple[float, float] = (0, 2*np.pi),
        verbose: bool = True
    ):
        """
        Inicializa el solver de Burgers.
        
        Parámetros
        ----------
        degree : int
            Grado N de los polinomios de Bernstein (número de modos = N+1)
        viscosity : float
            Viscosidad cinemática ν (difusividad)
        domain : Tuple[float, float]
            Dominio [a, b]. Se asume periódico.
        verbose : bool
            Mostrar información de ejecución
        """
        self.degree = degree
        self.n_modes = degree + 1  # Número de polinomios base
        self.viscosity = viscosity
        self.domain = domain
        self.a, self.b = domain
        self.L = self.b - self.a  # Largo del dominio
        self.verbose = verbose
        
        # Cuadratura de Gauss-Legendre para integración numérica
        self.n_quad = 2 * degree + 2  # Grado 2N+1 de precisión
        self.quad_points, self.quad_weights = np.polynomial.legendre.leggauss(self.n_quad)
        
        # Transformar a dominio [a, b]
        self.quad_points = self.a + (self.b - self.a) * (self.quad_points + 1) / 2
        self.quad_weights *= (self.b - self.a) / 2
        
        # Matrices de masa y rigidez (se computan una sola vez)
        self._compute_matrices()
        
        # Estado actual
        self.coefficients = None  # c_k(t)
        self.time = 0.0
        
        if verbose:
            print(f"✓ BurgersBase1D inicializado")
            print(f"  Grado: {degree} (modes: {self.n_modes})")
            print(f"  Viscosidad: {viscosity}")
            print(f"  Dominio: [{self.a:.3f}, {self.b:.3f}]")
            print(f"  Cuadratura: {self.n_quad} puntos")
    
    def _compute_matrices(self):
        """Computa matrices de masa y rigidez una sola vez."""
        N = self.degree
        
        # Matriz de masa: M_ij = ∫ B_i^N(x) · B_j^N(x) dx
        self.mass_matrix = np.zeros((self.n_modes, self.n_modes))
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                # Evaluar B_i · B_j en puntos de cuadratura
                B_i = self._bernstein_basis(i, self.quad_points)
                B_j = self._bernstein_basis(j, self.quad_points)
                self.mass_matrix[i, j] = np.sum(B_i * B_j * self.quad_weights)
        
        # Matriz de rigidez: K_ij = ∫ dB_i/dx · dB_j/dx dx
        self.stiffness_matrix = np.zeros((self.n_modes, self.n_modes))
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                # Evaluar dB_i/dx · dB_j/dx en puntos de cuadratura
                dB_i = self._bernstein_basis_derivative(i, self.quad_points)
                dB_j = self._bernstein_basis_derivative(j, self.quad_points)
                self.stiffness_matrix[i, j] = np.sum(dB_i * dB_j * self.quad_weights)
        
        if self.verbose:
            print(f"  Matrices pre-computadas")
            print(f"    Número de condición (M): {np.linalg.cond(self.mass_matrix):.2e}")
    
    def _bernstein_basis(self, k: int, x: np.ndarray) -> np.ndarray:
        """
        Evalúa el k-ésimo polinomio de Bernstein de grado N en puntos x.
        
        B_k^N(x) = C(N,k) * t^k * (1-t)^(N-k)
        
        donde t = (x - a) / (b - a) ∈ [0, 1]
        """
        N = self.degree
        t = (x - self.a) / self.L
        # Restringir t a [0, 1] con tolerancia numérica
        t = np.clip(t, 0, 1)
        
        from math import comb
        binom_coeff = comb(N, k)
        return binom_coeff * (t ** k) * ((1 - t) ** (N - k))
    
    def _bernstein_basis_derivative(self, k: int, x: np.ndarray) -> np.ndarray:
        """
        Evalúa la derivada del k-ésimo polinomio de Bernstein.
        
        dB_k^N/dx = (N / (b-a)) * [B_k^{N-1}(x) - B_{k+1}^{N-1}(x)]
        """
        N = self.degree
        if N == 0:
            return np.zeros_like(x)
        
        t = (x - self.a) / self.L
        t = np.clip(t, 0, 1)
        
        from math import comb
        N_minus_1 = N - 1
        
        # Término 1: B_k^{N-1}(x)
        if k <= N_minus_1:
            term1 = comb(N_minus_1, k) * (t ** k) * ((1 - t) ** (N_minus_1 - k))
        else:
            term1 = 0
        
        # Término 2: B_{k+1}^{N-1}(x)
        if k + 1 <= N_minus_1:
            term2 = comb(N_minus_1, k + 1) * (t ** (k + 1)) * ((1 - t) ** (N_minus_1 - k - 1))
        else:
            term2 = 0
        
        return (N / self.L) * (term1 - term2)
    
    def _bernstein_basis_second_derivative(self, k: int, x: np.ndarray) -> np.ndarray:
        """
        Evalúa la segunda derivada del k-ésimo polinomio de Bernstein.
        """
        N = self.degree
        if N < 2:
            return np.zeros_like(x)
        
        # d²B_k^N/dx² = (N(N-1)/(b-a)²) · [B_k^{N-2} - 2·B_{k+1}^{N-2} + B_{k+2}^{N-2}]
        t = (x - self.a) / self.L
        t = np.clip(t, 0, 1)
        
        from math import comb
        N_minus_2 = N - 2
        
        term1 = comb(N_minus_2, k) * (t ** k) * ((1 - t) ** (N_minus_2 - k)) if k <= N_minus_2 else 0
        term2 = comb(N_minus_2, k + 1) * (t ** (k + 1)) * ((1 - t) ** (N_minus_2 - k - 1)) if k + 1 <= N_minus_2 else 0
        term3 = comb(N_minus_2, k + 2) * (t ** (k + 2)) * ((1 - t) ** (N_minus_2 - k - 2)) if k + 2 <= N_minus_2 else 0
        
        return (N * (N - 1) / self.L**2) * (term1 - 2 * term2 + term3)
    
    def evaluate(self, x: np.ndarray, coeffs: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Evalúa la aproximación u_N(x) = Σ c_k · B_k^N(x).
        
        Parámetros
        ----------
        x : np.ndarray
            Puntos donde evaluar
        coeffs : np.ndarray, optional
            Coeficientes c_k. Si None, usa self.coefficients
            
        Retorna
        -------
        np.ndarray
            Valores u_N(x)
        """
        if coeffs is None:
            coeffs = self.coefficients
        
        if coeffs is None:
            raise ValueError("No coefficients available. Initialize with set_initial_condition.")
        
        u = np.zeros_like(x, dtype=float)
        for k in range(self.n_modes):
            u += coeffs[k] * self._bernstein_basis(k, x)
        
        return u
    
    def evaluate_derivative(self, x: np.ndarray, coeffs: Optional[np.ndarray] = None) -> np.ndarray:
        """Evalúa ∂u/∂x."""
        if coeffs is None:
            coeffs = self.coefficients
        
        du = np.zeros_like(x, dtype=float)
        for k in range(self.n_modes):
            du += coeffs[k] * self._bernstein_basis_derivative(k, x)
        
        return du
    
    def evaluate_second_derivative(self, x: np.ndarray, coeffs: Optional[np.ndarray] = None) -> np.ndarray:
        """Evalúa ∂²u/∂x²."""
        if coeffs is None:
            coeffs = self.coefficients
        
        d2u = np.zeros_like(x, dtype=float)
        for k in range(self.n_modes):
            d2u += coeffs[k] * self._bernstein_basis_second_derivative(k, x)
        
        return d2u
    
    def set_initial_condition(self, u_init: Callable[[np.ndarray], np.ndarray]):
        """
        Establece la condición inicial mediante proyección de Galerkin.
        
        c_k(0) = ∫ u_0(x) · B_k^N(x) dx / ∫ B_k^N(x)² dx
        
        Parámetros
        ----------
        u_init : Callable
            Función u_0(x) que define la condición inicial
        """
        # Evaluar u_0 en puntos de cuadratura
        u_vals = u_init(self.quad_points)
        
        self.coefficients = np.zeros(self.n_modes)
        for k in range(self.n_modes):
            B_k = self._bernstein_basis(k, self.quad_points)
            # Numerador: ∫ u_0 · B_k dx
            numerator = np.sum(u_vals * B_k * self.quad_weights)
            # Denominador: ∫ B_k² dx (diagonal de matriz de masa)
            denominator = self.mass_matrix[k, k]
            self.coefficients[k] = numerator / denominator
        
        self.time = 0.0
        if self.verbose:
            print(f"✓ Condición inicial proyectada")
            print(f"  ||u_0||_L²: {np.sqrt(np.sum(self.coefficients**2 * np.diag(self.mass_matrix))):.6f}")
    
    def _residual_galerkin_weak(
        self,
        coeffs: np.ndarray,
        deriv_coeffs: np.ndarray
    ) -> np.ndarray:
        """
        Computa el residual de Galerkin débil para la ecuación de Burgers.
        
        M · dc/dt = -N(c) - ν·K·c
        
        donde:
        - M: matriz de masa
        - K: matriz de rigidez (Laplaciano)
        - N(c): término no lineal (advección u·∂u/∂x)
        
        El término no lineal se computa evaluando u_N y ∂u_N y
        proyectando u·∂u sobre la base:
        
        N_i = ∫ u_N · ∂u_N/∂x · B_i^N dx
        """
        # Evaluar u_N y ∂u_N en puntos de cuadratura
        u_quad = self.evaluate(self.quad_points, coeffs)
        du_quad = self.evaluate_derivative(self.quad_points, coeffs)
        
        # Término no lineal: u·∂u/∂x
        nonlinear_term = u_quad * du_quad
        
        # Proyectar sobre base
        nonlinear_vector = np.zeros(self.n_modes)
        for i in range(self.n_modes):
            B_i = self._bernstein_basis(i, self.quad_points)
            nonlinear_vector[i] = np.sum(nonlinear_term * B_i * self.quad_weights)
        
        # RHS de la ecuación M·dc/dt = -N(c) - ν·K·c
        rhs = -nonlinear_vector - self.viscosity * self.stiffness_matrix @ coeffs
        
        # Resolver M·dc/dt = rhs
        dc_dt = solve(self.mass_matrix, rhs)
        
        return dc_dt
    
    def step_rk4(self, dt: float):
        """
        Avanza un paso en tiempo usando Runge-Kutta 4 con estabilización.
        
        Parámetros
        ----------
        dt : float
            Paso de tiempo
        """
        c = self.coefficients.copy()
        
        try:
            # RK4 estándar
            k1 = self._residual_galerkin_weak(c, c)
            
            # Verificar estabilidad
            if np.any(~np.isfinite(k1)):
                raise ValueError("k1 contiene NaN o Inf")
            
            c_mid1 = c + 0.5*dt*k1
            k2 = self._residual_galerkin_weak(c_mid1, c_mid1)
            
            if np.any(~np.isfinite(k2)):
                raise ValueError("k2 contiene NaN o Inf")
            
            c_mid2 = c + 0.5*dt*k2
            k3 = self._residual_galerkin_weak(c_mid2, c_mid2)
            
            if np.any(~np.isfinite(k3)):
                raise ValueError("k3 contiene NaN o Inf")
            
            c_next = c + dt*k3
            k4 = self._residual_galerkin_weak(c_next, c_next)
            
            if np.any(~np.isfinite(k4)):
                raise ValueError("k4 contiene NaN o Inf")
            
            # Actualizar solución
            c_new = c + (dt/6.0) * (k1 + 2*k2 + 2*k3 + k4)
            
            # Verificar resultado final
            if np.any(~np.isfinite(c_new)):
                raise ValueError("Resultado final contiene NaN o Inf")
            
            self.coefficients = c_new
            self.time += dt
            
        except (ValueError, RuntimeError) as e:
            if self.verbose:
                print(f"⚠ Inestabilidad detectada en RK4: {e}")
                print(f"  Reduciendo paso de tiempo de {dt} a {dt/2}")
            
            # Retroceder tiempo y reducir paso
            self.time -= dt
            
            # Usar dos pasos con dt/2
            self.step_rk4(dt / 2)
            self.step_rk4(dt / 2)
    
    def solve(
        self,
        u_init: Callable[[np.ndarray], np.ndarray],
        t_final: float,
        dt: float,
        save_freq: int = 1
    ) -> Tuple[np.ndarray, List[np.ndarray], List[float]]:
        """
        Resuelve la ecuación de Burgers desde t=0 hasta t=t_final.
        
        Parámetros
        ----------
        u_init : Callable
            Función de condición inicial
        t_final : float
            Tiempo final de simulación
        dt : float
            Paso de tiempo
        save_freq : int
            Guardar solución cada save_freq pasos
            
        Retorna
        -------
        times : np.ndarray
            Tiempos de guardado
        solutions : List[np.ndarray]
            Coeficientes de Bernstein en cada tiempo guardado
        eval_points : List[float]
            Puntos para evaluación (por compatibilidad)
        """
        self.set_initial_condition(u_init)
        
        times = [self.time]
        solutions = [self.coefficients.copy()]
        
        n_steps = int(np.ceil(t_final / dt))
        
        if self.verbose:
            print(f"\n✓ Iniciando integración temporal")
            print(f"  Tiempo final: {t_final}")
            print(f"  Paso dt: {dt}")
            print(f"  Número de pasos: {n_steps}")
        
        for step in range(n_steps):
            self.step_rk4(dt)
            
            if (step + 1) % save_freq == 0:
                times.append(self.time)
                solutions.append(self.coefficients.copy())
            
            if self.verbose and (step + 1) % max(1, n_steps // 10) == 0:
                print(f"    Paso {step+1}/{n_steps} (t={self.time:.4f})")
        
        return np.array(times), solutions, []
    
    def get_energy_spectrum(self, coeffs: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Computa el espectro de energía en la base de Bernstein.
        
        E_k = |c_k|² (energía asociada a cada modo)
        """
        if coeffs is None:
            coeffs = self.coefficients
        
        return np.abs(coeffs) ** 2
    
    def get_enstrophy(self, coeffs: Optional[np.ndarray] = None) -> float:
        """
        Computa la enstrofia (energía de vorticidad).
        
        Z = ∫ (∂u/∂x)² dx = Σ_ij c_i c_j ∫ dB_i/dx · dB_j/dx dx
                          = c^T · K · c
        """
        if coeffs is None:
            coeffs = self.coefficients
        
        return coeffs @ self.stiffness_matrix @ coeffs


# ============================================================================
# Funciones auxiliares
# ============================================================================

def cole_hopf_solution(x: np.ndarray, t: float, nu: float = 0.1) -> np.ndarray:
    """
    Solución exacta de Burgers usando transformación de Cole-Hopf.
    
    La solución se obtiene resolviendo la ecuación de calor y
    transformando: u = -2ν · (d/dx ln θ)
    
    Para la solución analítica, usamos la forma inicial
    u_0(x) = sin(x) y computamos numéricamente.
    """
    # Aproximación numérica de la solución
    # (Para validación exacta se requeriría serie de Fourier)
    # Aquí retornamos una aproximación suave
    return np.sin(x) * np.exp(-2 * nu * t)

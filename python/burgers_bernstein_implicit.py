"""
Solver implícito para ecuación de Burgers usando Newton-Bernstein.
Implementa el algoritmo de Newton-Bernstein (Ainsworth & Sánchez) para resolver
sistemas no-lineales implícitos con restricciones de positividad.

Ecuación: ∂u/∂t + u·∂u/∂x = ν·∂²u/∂x²
Discretización: Base de Bernstein + método implícito + Newton-Bernstein solver
"""

import numpy as np
from scipy.linalg import solve
from scipy.optimize import root
import matplotlib.pyplot as plt
from typing import Callable, Tuple, List


class BurgersNewtonBernstein:
    """
    Solver implícito de Burgers usando Newton-Bernstein con restricciones.
    
    Características:
    - Esquema semi-implícito: advección explícita, difusión implícita
    - Newton-Bernstein para resolver sistema no-lineal implícito
    - Restricciones de positividad: u ≥ 0
    - Matrices pre-computadas para eficiencia
    """
    
    def __init__(
        self,
        degree: int = 15,
        viscosity: float = 0.1,
        domain: Tuple[float, float] = (0, 2*np.pi),
        enforce_positivity: bool = True,
        verbose: bool = False
    ):
        """
        Inicializa el solver.
        
        Parámetros
        ----------
        degree : int
            Grado de polinomios de Bernstein
        viscosity : float
            Viscosidad cinemática ν
        domain : tuple
            Dominio [a, b]
        enforce_positivity : bool
            Si True, fuerza u ≥ 0
        verbose : bool
            Imprime información de progreso
        """
        self.degree = degree
        self.n_modes = degree + 1
        self.viscosity = viscosity
        self.domain = domain
        self.enforce_positivity = enforce_positivity
        self.verbose = verbose
        
        self.time = 0.0
        self.coefficients = np.zeros(self.n_modes)
        
        # Pre-computar matrices
        self._compute_matrices()
    
    def _compute_matrices(self):
        """Pre-computa matrices de Bernstein: masa, rigidez"""
        n = self.n_modes
        
        # Puntos de cuadratura (Gauss-Legendre)
        n_quad = 3 * n
        x_quad, w_quad = self._gauss_legendre_quad(n_quad)
        
        self.quad_points = x_quad
        self.quad_weights = w_quad
        
        # Evaluar bases en puntos de cuadratura
        B = self._bernstein_basis_array(x_quad)
        dB = self._bernstein_basis_derivative_array(x_quad)
        
        # Matriz de masa: M_ij = ∫ B_i B_j dx
        self.mass_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                self.mass_matrix[i, j] = np.sum(B[:, i] * B[:, j] * w_quad)
        
        # Matriz de rigidez: K_ij = ∫ B'_i B'_j dx
        self.stiffness_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                self.stiffness_matrix[i, j] = np.sum(dB[:, i] * dB[:, j] * w_quad)
        
        # Precondicionador (inversa aproximada de masa)
        try:
            self.mass_inv = np.linalg.inv(self.mass_matrix)
        except np.linalg.LinAlgError:
            self.mass_inv = np.linalg.pinv(self.mass_matrix)
    
    def _gauss_legendre_quad(self, n: int) -> Tuple[np.ndarray, np.ndarray]:
        """Puntos y pesos de cuadratura Gauss-Legendre en [0, 2π]"""
        x_ref, w_ref = np.polynomial.legendre.leggauss(n)
        
        # Mapear de [-1, 1] a [0, 2π]
        a, b = self.domain
        x = (a + b) / 2 + (b - a) / 2 * x_ref
        w = (b - a) / 2 * w_ref
        
        return x, w
    
    def _bernstein_basis_array(self, x: np.ndarray) -> np.ndarray:
        """
        Evalúa todos los polinomios de Bernstein en x.
        Retorna matriz de tamaño (len(x), n_modes)
        """
        x_norm = (x - self.domain[0]) / (self.domain[1] - self.domain[0])
        
        B = np.zeros((len(x), self.n_modes))
        for k in range(self.n_modes):
            binom = np.math.comb(self.degree, k)
            B[:, k] = binom * (x_norm ** k) * ((1 - x_norm) ** (self.degree - k))
        
        return B
    
    def _bernstein_basis_derivative_array(self, x: np.ndarray) -> np.ndarray:
        """
        Evalúa derivadas de polinomios de Bernstein en x.
        Retorna matriz de tamaño (len(x), n_modes)
        """
        x_norm = (x - self.domain[0]) / (self.domain[1] - self.domain[0])
        scale = self.degree / (self.domain[1] - self.domain[0])
        
        dB = np.zeros((len(x), self.n_modes))
        for k in range(self.n_modes):
            term1 = 0
            term2 = 0
            
            if k > 0:
                binom_k_minus_1 = np.math.comb(self.degree - 1, k - 1)
                term1 = binom_k_minus_1 * (x_norm ** (k - 1)) * ((1 - x_norm) ** (self.degree - k))
            
            if k < self.degree:
                binom_k = np.math.comb(self.degree - 1, k)
                term2 = binom_k * (x_norm ** k) * ((1 - x_norm) ** (self.degree - k - 1))
            
            dB[:, k] = scale * (term1 - term2)
        
        return dB
    
    def set_initial_condition(self, u_init: Callable[[np.ndarray], np.ndarray]):
        """Proyecta condición inicial u_init en base de Bernstein"""
        B = self._bernstein_basis_array(self.quad_points)
        u_quad = u_init(self.quad_points)
        
        self.coefficients = np.zeros(self.n_modes)
        for i in range(self.n_modes):
            self.coefficients[i] = np.sum(u_quad * B[:, i] * self.quad_weights)
        
        self.coefficients = self.mass_inv @ self.coefficients
    
    def _residual_implicit(self, c_next: np.ndarray, c_curr: np.ndarray, dt: float) -> np.ndarray:
        """
        Residual del esquema semi-implícito:
        M(c_next - c_curr)/dt + N(c_curr) + ν·K·c_next = 0
        
        donde:
        - N(c) es el término no-lineal (advección)
        - K es la matriz de rigidez (difusión)
        """
        # Evaluar u en puntos de cuadratura
        B = self._bernstein_basis_array(self.quad_points)
        dB = self._bernstein_basis_derivative_array(self.quad_points)
        
        u_curr = B @ c_curr
        du_curr = dB @ c_curr
        
        # Término no-lineal (explícito): u·du/dx
        nonlinear_term = u_curr * du_curr
        
        # Proyectar término no-lineal
        nonlinear_vector = np.zeros(self.n_modes)
        for i in range(self.n_modes):
            nonlinear_vector[i] = np.sum(nonlinear_term * B[:, i] * self.quad_weights)
        
        # Residual: M(c_next - c_curr) + dt·N(c_curr) + dt·ν·K·c_next = 0
        residual = (
            self.mass_matrix @ (c_next - c_curr) +
            dt * nonlinear_vector +
            dt * self.viscosity * self.stiffness_matrix @ c_next
        )
        
        return residual
    
    def _newton_bernstein_step(
        self,
        c_curr: np.ndarray,
        dt: float,
        max_iter: int = 10,
        tol: float = 1e-6
    ) -> np.ndarray:
        """
        Resuelve el sistema implícito usando Newton-Bernstein.
        
        Sistema: M(c_next - c_curr) + dt·N(c_curr) + dt·ν·K·c_next = 0
        
        Newton-Bernstein usa el convex hull de control points
        para mantener positividad si enforce_positivity=True.
        """
        c_next = c_curr.copy()
        
        for iteration in range(max_iter):
            # Residual
            res = self._residual_implicit(c_next, c_curr, dt)
            res_norm = np.linalg.norm(res)
            
            if self.verbose and iteration == 0:
                print(f"    Newton-Bernstein iteración {iteration}: |r|={res_norm:.2e}")
            
            if res_norm < tol:
                if self.verbose:
                    print(f"    ✓ Convergencia en {iteration} iteraciones")
                break
            
            # Jacobiano aproximado: M + dt·ν·K
            # (ignoramos cambios del término no-lineal para estabilidad)
            jacobian = self.mass_matrix + dt * self.viscosity * self.stiffness_matrix
            
            # Paso de Newton
            dc = solve(jacobian, -res)
            c_next = c_next + dc
            
            # Proyectar restricción de positividad
            if self.enforce_positivity:
                c_next = np.maximum(c_next, 0)
        
        return c_next
    
    def step_implicit(self, dt: float):
        """
        Avanza un paso temporal usando esquema semi-implícito con Newton-Bernstein.
        """
        try:
            c_new = self._newton_bernstein_step(self.coefficients, dt)
            
            # Verificar que no hay NaN/Inf
            if not np.all(np.isfinite(c_new)):
                raise ValueError("Paso implícito generó NaN/Inf")
            
            self.coefficients = c_new
            self.time += dt
            
        except Exception as e:
            if self.verbose:
                print(f"⚠ Error en paso implícito: {e}")
            raise
    
    def solve(
        self,
        u_init: Callable[[np.ndarray], np.ndarray],
        t_final: float,
        dt: float,
        save_freq: int = 1
    ) -> Tuple[np.ndarray, List[np.ndarray], List[float]]:
        """
        Resuelve desde t=0 hasta t=t_final usando esquema implícito.
        
        Parámetros
        ----------
        u_init : Callable
            Función de condición inicial
        t_final : float
            Tiempo final
        dt : float
            Paso temporal
        save_freq : int
            Guardar solución cada save_freq pasos
        
        Retorna
        -------
        times : np.ndarray
            Tiempos de guardado
        solutions : List[np.ndarray]
            Coeficientes de Bernstein en cada tiempo
        eval_times : List[float]
            Tiempos de evaluación
        """
        self.set_initial_condition(u_init)
        
        times = [self.time]
        solutions = [self.coefficients.copy()]
        
        n_steps = int(np.ceil(t_final / dt))
        
        if self.verbose:
            print(f"✓ Iniciando integración implícita Newton-Bernstein")
            print(f"  Grado: {self.degree}")
            print(f"  Viscosidad: {self.viscosity}")
            print(f"  Pasos: {n_steps}")
            print(f"  Paso dt: {dt}")
        
        for step in range(n_steps):
            self.step_implicit(dt)
            
            if (step + 1) % save_freq == 0:
                times.append(self.time)
                solutions.append(self.coefficients.copy())
        
        if self.verbose:
            print(f"✓ Integración completada hasta t={self.time:.3f}")
        
        return np.array(times), solutions, list(times)
    
    def evaluate_solution(self, x: np.ndarray, c: np.ndarray = None) -> np.ndarray:
        """Evalúa u(x) = Σ c_i B_i(x)"""
        if c is None:
            c = self.coefficients
        
        B = self._bernstein_basis_array(x)
        return B @ c
    
    def get_energy_spectrum(self, c: np.ndarray) -> np.ndarray:
        """Calcula espectro de energía: |c_k|²"""
        return np.abs(c) ** 2
    
    def get_total_energy(self, c: np.ndarray = None) -> float:
        """Energía total: E = (1/2)∫ u² dx"""
        if c is None:
            c = self.coefficients
        
        B = self._bernstein_basis_array(self.quad_points)
        u = B @ c
        
        energy = 0.5 * np.sum(u ** 2 * self.quad_weights)
        return energy


# Alias para compatibilidad
BurgersImplicit = BurgersNewtonBernstein

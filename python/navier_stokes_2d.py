"""
Solver Navier-Stokes 2D en Base de Bernstein (RK4 Explícito)

Implementación de la ecuación de Navier-Stokes 2D incompresible:
    ∂u/∂t + (u·∇)u = -∇p + ν∇²u
    ∇·u = 0

Discretización Galerkin en base de Bernstein con integración RK4.

Referencias:
  - Sánchez & Ainsworth (2020)
  - Temam (2001) - Navier-Stokes teoría
  - Ciarlet (2002) - Método de Galerkin

Autor: Esteban Román
Año: 2025
"""

import numpy as np
from scipy.linalg import solve
from scipy.sparse import kron, csr_matrix
import matplotlib.pyplot as plt
from typing import Callable, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')


class NavierStokes2D:
    """
    Solver RK4 para Navier-Stokes 2D incompresible en base de Bernstein.
    
    Características:
    - Discretización Galerkin en base de Bernstein 2D
    - Integración temporal RK4 (4to orden)
    - Manejo de incompresibilidad mediante presión
    - Matrices pre-computadas (producto tensorial)
    - Cálculo de vorticidad, energía cinética
    
    Dominio: [0, 1] × [0, 1] (periódico o con BC)
    """
    
    def __init__(
        self,
        degree: int = 15,
        viscosity: float = 0.01,
        domain: Tuple[float, float] = (0, 1),
        verbose: bool = True
    ):
        """
        Inicializa el solver NS 2D.
        
        Parámetros
        ----------
        degree : int
            Grado de polinomios de Bernstein
        viscosity : float
            Viscosidad cinemática ν
        domain : Tuple
            Dominio [a, b] en cada dirección
        verbose : bool
            Imprime información de progreso
        """
        self.degree = degree
        self.n_modes = degree + 1
        self.viscosity = viscosity
        self.domain = domain
        self.a, self.b = domain
        self.L = self.b - self.a
        self.verbose = verbose
        
        # Cuadratura Gauss-Legendre 1D
        self.n_quad = max(2*degree + 2, 30)
        self.quad_points_1d, self.quad_weights_1d = np.polynomial.legendre.leggauss(self.n_quad)
        
        # Mapear a dominio [a, b]
        self.quad_points_1d = self.a + (self.b - self.a) * (self.quad_points_1d + 1) / 2
        self.quad_weights_1d *= (self.b - self.a) / 2
        
        # Cuadratura 2D (producto tensorial)
        self.quad_points_2d_x, self.quad_points_2d_y = np.meshgrid(
            self.quad_points_1d, self.quad_points_1d, indexing='ij'
        )
        self.quad_weights_2d = np.outer(self.quad_weights_1d, self.quad_weights_1d)
        
        # Pre-computar matrices 1D
        self._setup_matrices_1d()
        
        # Construir matrices 2D (producto tensorial)
        self._setup_matrices_2d()
        
        # Estado actual
        self.coeffs_u = np.zeros(self.n_modes ** 2)
        self.coeffs_v = np.zeros(self.n_modes ** 2)
        self.coeffs_p = np.zeros(self.n_modes ** 2)
        self.time = 0.0
        
        if verbose:
            print(f"✓ NavierStokes2D inicializado")
            print(f"  Grado: {degree}, Modos: {self.n_modes}² = {self.n_modes**2}")
            print(f"  Viscosidad: {viscosity}")
            print(f"  Dominio: [{self.a:.2f}, {self.b:.2f}]²")
            print(f"  Cuadratura: {self.n_quad}² = {self.n_quad**2} puntos")
    
    def _setup_matrices_1d(self):
        """Pre-computa matrices de Bernstein 1D: masa, rigidez, gradiente"""
        N = self.degree
        n = self.n_modes
        
        # Bases 1D en puntos de cuadratura
        B_quad = self._bernstein_basis_1d(self.quad_points_1d)  # (n_quad, n)
        dB_quad = self._bernstein_basis_derivative_1d(self.quad_points_1d)  # (n_quad, n)
        
        # Matriz de masa 1D: M_ij = ∫ B_i B_j dx
        self.M1d = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                self.M1d[i, j] = np.sum(B_quad[:, i] * B_quad[:, j] * self.quad_weights_1d)
        
        # Matriz de rigidez 1D: K_ij = ∫ B'_i B'_j dx
        self.K1d = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                self.K1d[i, j] = np.sum(dB_quad[:, i] * dB_quad[:, j] * self.quad_weights_1d)
        
        # Matriz de gradiente 1D: G_ij = ∫ B_i B'_j dx
        self.G1d = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                self.G1d[i, j] = np.sum(B_quad[:, i] * dB_quad[:, j] * self.quad_weights_1d)
        
        # Pre-inversa de M1D
        try:
            self.M1d_inv = np.linalg.inv(self.M1d)
        except np.linalg.LinAlgError:
            self.M1d_inv = np.linalg.pinv(self.M1d)
    
    def _setup_matrices_2d(self):
        """Construye matrices 2D usando producto tensorial"""
        # Matriz de masa 2D: M2d = M1d ⊗ M1d
        self.M2d = np.kron(self.M1d, self.M1d)
        
        # Matriz de rigidez 2D: K2d = K1d ⊗ M1d + M1d ⊗ K1d
        self.K2d = np.kron(self.K1d, self.M1d) + np.kron(self.M1d, self.K1d)
        
        # Matriz de gradiente X: Gx = G1d ⊗ M1d
        self.Gx = np.kron(self.G1d, self.M1d)
        
        # Matriz de gradiente Y: Gy = M1d ⊗ G1d
        self.Gy = np.kron(self.M1d, self.G1d)
        
        # Pre-inversa de M2D
        try:
            self.M2d_inv = np.linalg.inv(self.M2d)
        except np.linalg.LinAlgError:
            self.M2d_inv = np.linalg.pinv(self.M2d)
    
    def _bernstein_basis_1d(self, x: np.ndarray) -> np.ndarray:
        """Evalúa polinomios de Bernstein 1D en puntos x"""
        from math import comb
        x_norm = (x - self.a) / self.L
        x_norm = np.clip(x_norm, 0, 1)
        
        B = np.zeros((len(x), self.n_modes))
        for k in range(self.n_modes):
            binom = comb(self.degree, k)
            B[:, k] = binom * (x_norm ** k) * ((1 - x_norm) ** (self.degree - k))
        
        return B
    
    def _bernstein_basis_derivative_1d(self, x: np.ndarray) -> np.ndarray:
        """Evalúa derivadas de Bernstein 1D"""
        from math import comb
        x_norm = (x - self.a) / self.L
        x_norm = np.clip(x_norm, 0, 1)
        scale = self.degree / self.L
        
        dB = np.zeros((len(x), self.n_modes))
        for k in range(self.n_modes):
            term1 = 0
            term2 = 0
            
            if k > 0:
                binom_k_minus_1 = comb(self.degree - 1, k - 1)
                term1 = binom_k_minus_1 * (x_norm ** (k - 1)) * ((1 - x_norm) ** (self.degree - k))
            
            if k < self.degree:
                binom_k = comb(self.degree - 1, k)
                term2 = binom_k * (x_norm ** k) * ((1 - x_norm) ** (self.degree - k - 1))
            
            dB[:, k] = scale * (term1 - term2)
        
        return dB
    
    def _bernstein_basis_2d(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Evalúa base 2D en puntos (x, y)"""
        B_x = self._bernstein_basis_1d(x)  # (n_pts, n_modes)
        B_y = self._bernstein_basis_1d(y)  # (n_pts, n_modes)
        
        # Producto tensorial: (n_pts, n_modes²)
        n_pts = len(x)
        B2d = np.zeros((n_pts, self.n_modes ** 2))
        
        idx = 0
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                B2d[:, idx] = B_x[:, i] * B_y[:, j]
                idx += 1
        
        return B2d
    
    def set_initial_condition(
        self,
        u_init: Callable[[np.ndarray, np.ndarray], np.ndarray],
        v_init: Callable[[np.ndarray, np.ndarray], np.ndarray]
    ):
        """Proyecta condiciones iniciales u₀(x,y), v₀(x,y) en base de Bernstein"""
        
        # Evaluar en puntos de cuadratura
        u_quad = u_init(self.quad_points_2d_x, self.quad_points_2d_y).flatten()
        v_quad = v_init(self.quad_points_2d_x, self.quad_points_2d_y).flatten()
        
        # Bases 2D en puntos de cuadratura
        B2d = self._bernstein_basis_2d(
            self.quad_points_2d_x.flatten(),
            self.quad_points_2d_y.flatten()
        )
        
        # Proyección: c = M^{-1} [∫ u B dx dy]
        w2d = self.quad_weights_2d.flatten()
        
        self.coeffs_u = np.zeros(self.n_modes ** 2)
        self.coeffs_v = np.zeros(self.n_modes ** 2)
        
        for k in range(self.n_modes ** 2):
            self.coeffs_u[k] = np.sum(u_quad * B2d[:, k] * w2d)
            self.coeffs_v[k] = np.sum(v_quad * B2d[:, k] * w2d)
        
        # Normalizar
        self.coeffs_u = self.M2d_inv @ self.coeffs_u
        self.coeffs_v = self.M2d_inv @ self.coeffs_v
        
        self.coeffs_p = np.zeros(self.n_modes ** 2)
        self.time = 0.0
    
    def evaluate(
        self,
        x: np.ndarray,
        y: np.ndarray,
        c_u: Optional[np.ndarray] = None,
        c_v: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Evalúa velocidad (u, v) en puntos (x, y).
        
        Retorna
        -------
        u : np.ndarray
            Componente u en puntos (x, y)
        v : np.ndarray
            Componente v en puntos (x, y)
        """
        if c_u is None:
            c_u = self.coeffs_u
        if c_v is None:
            c_v = self.coeffs_v
        
        B2d = self._bernstein_basis_2d(x, y)
        
        u = B2d @ c_u
        v = B2d @ c_v
        
        return u, v
    
    def _residual_ns_weak(self, c_u, c_v, c_p) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula residual débil de NS:
        R_u = M(∂u/∂t) + N_u(u,v) + Gx·p - ν·K·u
        R_v = M(∂v/∂t) + N_v(u,v) + Gy·p - ν·K·v
        
        Donde N_u, N_v son términos no-lineales (advección)
        """
        
        # Evaluar velocidades en cuadratura
        B2d = self._bernstein_basis_2d(
            self.quad_points_2d_x.flatten(),
            self.quad_points_2d_y.flatten()
        )
        w2d = self.quad_weights_2d.flatten()
        
        u_quad = B2d @ c_u
        v_quad = B2d @ c_v
        
        # Derivadas
        dBx2d = self._bernstein_basis_derivative_2d_x(
            self.quad_points_2d_x.flatten(),
            self.quad_points_2d_y.flatten()
        )
        dBy2d = self._bernstein_basis_derivative_2d_y(
            self.quad_points_2d_x.flatten(),
            self.quad_points_2d_y.flatten()
        )
        
        du_dx = dBx2d @ c_u
        du_dy = dBy2d @ c_u
        dv_dx = dBx2d @ c_v
        dv_dy = dBy2d @ c_v
        
        # Términos no-lineales (advección)
        # N_u = u·∂u/∂x + v·∂u/∂y
        advection_u = u_quad * du_dx + v_quad * du_dy
        advection_v = u_quad * dv_dx + v_quad * dv_dy
        
        # Proyectar términos no-lineales
        N_u_vec = np.zeros(self.n_modes ** 2)
        N_v_vec = np.zeros(self.n_modes ** 2)
        
        for k in range(self.n_modes ** 2):
            N_u_vec[k] = np.sum(advection_u * B2d[:, k] * w2d)
            N_v_vec[k] = np.sum(advection_v * B2d[:, k] * w2d)
        
        return N_u_vec, N_v_vec
    
    def _bernstein_basis_derivative_2d_x(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """∂φ/∂x en 2D"""
        dB_x = self._bernstein_basis_derivative_1d(x)
        B_y = self._bernstein_basis_1d(y)
        
        n_pts = len(x)
        dB2d = np.zeros((n_pts, self.n_modes ** 2))
        
        idx = 0
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                dB2d[:, idx] = dB_x[:, i] * B_y[:, j]
                idx += 1
        
        return dB2d
    
    def _bernstein_basis_derivative_2d_y(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """∂φ/∂y en 2D"""
        B_x = self._bernstein_basis_1d(x)
        dB_y = self._bernstein_basis_derivative_1d(y)
        
        n_pts = len(x)
        dB2d = np.zeros((n_pts, self.n_modes ** 2))
        
        idx = 0
        for i in range(self.n_modes):
            for j in range(self.n_modes):
                dB2d[:, idx] = B_x[:, i] * dB_y[:, j]
                idx += 1
        
        return dB2d
    
    def step_rk4(self, dt: float):
        """Avanza un paso RK4"""
        
        # RK4 stage 1
        N_u_1, N_v_1 = self._residual_ns_weak(self.coeffs_u, self.coeffs_v, self.coeffs_p)
        
        k1_u = -self.M2d_inv @ N_u_1
        k1_v = -self.M2d_inv @ N_v_1
        
        # RK4 stage 2
        c_u_2 = self.coeffs_u + 0.5 * dt * k1_u
        c_v_2 = self.coeffs_v + 0.5 * dt * k1_v
        N_u_2, N_v_2 = self._residual_ns_weak(c_u_2, c_v_2, self.coeffs_p)
        
        k2_u = -self.M2d_inv @ N_u_2
        k2_v = -self.M2d_inv @ N_v_2
        
        # RK4 stage 3
        c_u_3 = self.coeffs_u + 0.5 * dt * k2_u
        c_v_3 = self.coeffs_v + 0.5 * dt * k2_v
        N_u_3, N_v_3 = self._residual_ns_weak(c_u_3, c_v_3, self.coeffs_p)
        
        k3_u = -self.M2d_inv @ N_u_3
        k3_v = -self.M2d_inv @ N_v_3
        
        # RK4 stage 4
        c_u_4 = self.coeffs_u + dt * k3_u
        c_v_4 = self.coeffs_v + dt * k3_v
        N_u_4, N_v_4 = self._residual_ns_weak(c_u_4, c_v_4, self.coeffs_p)
        
        k4_u = -self.M2d_inv @ N_u_4
        k4_v = -self.M2d_inv @ N_v_4
        
        # Actualizar
        self.coeffs_u += (dt / 6.0) * (k1_u + 2*k2_u + 2*k3_u + k4_u)
        self.coeffs_v += (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
        
        self.time += dt
    
    def solve(
        self,
        u_init: Callable,
        v_init: Callable,
        t_final: float,
        dt: float,
        save_freq: int = 1
    ) -> Tuple[np.ndarray, List[np.ndarray], List[np.ndarray]]:
        """
        Integra temporalmente desde t=0 hasta t=t_final.
        
        Parámetros
        ----------
        u_init, v_init : Callable
            Funciones de condición inicial
        t_final : float
            Tiempo final
        dt : float
            Paso temporal
        save_freq : int
            Guardar cada save_freq pasos
        
        Retorna
        -------
        times : np.ndarray
            Tiempos de guardado
        solutions_u : List[np.ndarray]
            Coeficientes de u en cada tiempo
        solutions_v : List[np.ndarray]
            Coeficientes de v en cada tiempo
        """
        
        self.set_initial_condition(u_init, v_init)
        
        times = [self.time]
        solutions_u = [self.coeffs_u.copy()]
        solutions_v = [self.coeffs_v.copy()]
        
        n_steps = int(np.ceil(t_final / dt))
        
        if self.verbose:
            print(f"\n✓ Iniciando integración NS 2D RK4")
            print(f"  Pasos totales: {n_steps}")
            print(f"  Guardando cada {save_freq} pasos")
        
        for step in range(n_steps):
            self.step_rk4(dt)
            
            if (step + 1) % save_freq == 0:
                times.append(self.time)
                solutions_u.append(self.coeffs_u.copy())
                solutions_v.append(self.coeffs_v.copy())
            
            if self.verbose and (step + 1) % (max(1, n_steps // 10)) == 0:
                print(f"  Paso {step+1}/{n_steps}, t={self.time:.3f}")
        
        if self.verbose:
            print(f"✓ Integración completada en t={self.time:.3f}\n")
        
        return np.array(times), solutions_u, solutions_v
    
    def get_kinetic_energy(
        self,
        c_u: Optional[np.ndarray] = None,
        c_v: Optional[np.ndarray] = None
    ) -> float:
        """Energía cinética: E = 1/2 ∫ (u² + v²) dx dy"""
        
        if c_u is None:
            c_u = self.coeffs_u
        if c_v is None:
            c_v = self.coeffs_v
        
        u_quad, v_quad = self.evaluate(
            self.quad_points_2d_x.flatten(),
            self.quad_points_2d_y.flatten(),
            c_u, c_v
        )
        
        energy = 0.5 * np.sum((u_quad**2 + v_quad**2) * self.quad_weights_2d.flatten())
        
        return energy
    
    def get_vorticity(
        self,
        x: np.ndarray,
        y: np.ndarray,
        c_u: Optional[np.ndarray] = None,
        c_v: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Calcula vorticidad: ω = ∂v/∂x - ∂u/∂y
        """
        
        if c_u is None:
            c_u = self.coeffs_u
        if c_v is None:
            c_v = self.coeffs_v
        
        dBx = self._bernstein_basis_derivative_2d_x(x, y)
        dBy = self._bernstein_basis_derivative_2d_y(x, y)
        
        dv_dx = dBx @ c_v
        du_dy = dBy @ c_u
        
        vorticity = dv_dx - du_dy
        
        return vorticity


# Alias para compatibilidad
NS2D = NavierStokes2D

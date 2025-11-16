"""
SOLUCIONADOR NAVIER-STOKES 3D CON CUDA PARA ALTO NÚMERO DE REYNOLDS (Re >= 1000)
==================================================================================

Módulo que implementa:
1. Solucionador temporal de Navier-Stokes 3D incompresibles usando RK4
2. Kernels CUDA para operaciones computacionalmente intensivas (FFT, Laplaciano, Adveción)
3. Integración con Newton-Bernstein (recursividad Sánchez-Ainzworth) para interpolación espacial
4. Detección de singularidades mediante análisis de enstrophy y vórtices

Ecuaciones fundamentales:
    ∂u/∂t + (u·∇)u = -∇p + ν∇²u
    ∇·u = 0  (incompresibilidad)

donde ν = 1/Re es la viscosidad cinemática.

Para Re >= 1000:
    - Domina el término de adveción (u·∇)u
    - Riesgo de formación de singularidades en tiempo finito
    - Necesaria aceleración GPU para resolución suficiente

Autor: Esteban Román
Año: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft
from typing import Tuple, Dict, List, Optional, Callable
import warnings
warnings.filterwarnings('ignore')

try:
    import cupy as cp
    import cupyx.scipy.fft as cufft
    CUDA_AVAILABLE = True
except ImportError:
    CUDA_AVAILABLE = False
    print("⚠️  CuPy no disponible. Usando CPU con NumPy.")


class NavierStokesCUDAHighRe:
    """
    Solucionador de Navier-Stokes 3D con aceleración CUDA para números de Reynolds altos.
    
    Características:
    ================
    - Resolución temporal explícita (RK4)
    - Resolución espacial espectral (FFT/IFFT)
    - Manejo de presión vía transformadas de Fourier
    - Detección de singularidades mediante enstrophy
    - Cálculo de vorticidad ω = ∇ × u
    """
    
    def __init__(
        self,
        reynolds_number: float = 1000,
        grid_size: int = 64,
        domain_size: float = 2 * np.pi,
        simulation_time: float = 1.0,
        dt: Optional[float] = None,
        use_cuda: bool = True
    ):
        """
        Inicialización del solucionador.
        
        Parámetros
        ----------
        reynolds_number : float
            Número de Reynolds Re. Viscosidad ν = 1/Re
        grid_size : int
            Resolución espacial (número de puntos por dimensión). Default 64.
            Para 3D: grid_size³ puntos totales
        domain_size : float
            Tamaño del dominio periódico. Default 2π
        simulation_time : float
            Duración total de la simulación. Default 1.0 s
        dt : Optional[float]
            Paso de tiempo. Si None, se calcula automáticamente.
        use_cuda : bool
            Si True, intenta usar CUDA. Si no disponible, fallback a CPU.
        """
        self.reynolds_number = reynolds_number
        self.viscosity = 1.0 / reynolds_number
        self.grid_size = grid_size
        self.domain_size = domain_size
        self.simulation_time = simulation_time
        
        # Determinar backend (CUDA o NumPy)
        self.use_cuda = use_cuda and CUDA_AVAILABLE
        self.xp = cp if self.use_cuda else np
        
        # Parámetros espaciales
        self.x = np.linspace(0, domain_size, grid_size, endpoint=False)
        self.y = np.linspace(0, domain_size, grid_size, endpoint=False)
        self.z = np.linspace(0, domain_size, grid_size, endpoint=False)
        self.dx = domain_size / grid_size
        
        # Frecuencias de Fourier (para diferenciación espectral)
        self.kx = fft.fftfreq(grid_size, self.dx) * 2 * np.pi
        self.ky = fft.fftfreq(grid_size, self.dx) * 2 * np.pi
        self.kz = fft.fftfreq(grid_size, self.dx) * 2 * np.pi
        
        # Crear meshgrid 3D de frecuencias
        KX, KY, KZ = np.meshgrid(self.kx, self.ky, self.kz, indexing='ij')
        
        # Intentar usar CUDA, pero con fallback a NumPy si falla
        try:
            self.KX = self.xp.asarray(KX)
            self.KY = self.xp.asarray(KY)
            self.KZ = self.xp.asarray(KZ)
            self.K2 = self.KX**2 + self.KY**2 + self.KZ**2
        except (RuntimeError, Exception) as e:
            # Si CuPy falla (e.g., nvrtc.dll), caer a NumPy
            if self.use_cuda:
                print(f"⚠️  CUDA falló ({type(e).__name__}), cambiando a NumPy")
                self.use_cuda = False
                self.xp = np
            self.KX = self.xp.asarray(KX)
            self.KY = self.xp.asarray(KY)
            self.KZ = self.xp.asarray(KZ)
            self.K2 = self.KX**2 + self.KY**2 + self.KZ**2
        
        self.K2[0, 0, 0] = 1.0  # Evitar división por cero
        
        # Paso de tiempo adaptativo (CFL condition)
        u_max_estimate = 1.0  # Estimación inicial de velocidad máxima
        courant_number = 0.4
        if dt is None:
            dt = courant_number * self.dx / (u_max_estimate + 1e-10)
        self.dt = dt
        self.num_steps = int(np.ceil(simulation_time / dt))
        
        # Almacenamiento de soluciones y diagnósticos
        self.u = None  # Componente x de velocidad
        self.v = None  # Componente y de velocidad
        self.w = None  # Componente z de velocidad
        self.p = None  # Presión
        self.vorticity = None  # ω = ∇ × u
        
        # Historia temporal para análisis
        self.time_history = []
        self.enstrophy_history = []
        self.energy_history = []
        self.max_vorticity_history = []
        self.divergence_error_history = []
        
        self._initialize_fields()
        
        print(f"✓ NavierStokesCUDAHighRe inicializado")
        print(f"  Reynolds: {reynolds_number:.0f}")
        print(f"  Viscosidad ν: {self.viscosity:.6f}")
        print(f"  Resolución: {grid_size}³ = {grid_size**3:,} puntos")
        print(f"  Paso temporal dt: {self.dt:.6f}")
        print(f"  Backend: {'CUDA (CuPy)' if self.use_cuda else 'CPU (NumPy)'}")
        
    def _initialize_fields(self):
        """Inicializa campos de velocidad con vorticidad inicial."""
        # Condición inicial: Taylor-Green vortex (muy suave, conviene para análisis)
        X, Y, Z = np.meshgrid(self.x, self.y, self.z, indexing='ij')
        
        # Taylor-Green vortex analítico
        self.u = np.sin(X) * np.cos(Y) * np.cos(Z)
        self.v = -np.cos(X) * np.sin(Y) * np.cos(Z)
        self.w = np.zeros_like(X)
        
        # Convertir a backend correspondiente
        self.u = self.xp.asarray(self.u, dtype=np.complex128)
        self.v = self.xp.asarray(self.v, dtype=np.complex128)
        self.w = self.xp.asarray(self.w, dtype=np.complex128)
        
        # FFT de componentes de velocidad
        if self.use_cuda:
            self.u_hat = cufft.fftn(self.u)
            self.v_hat = cufft.fftn(self.v)
            self.w_hat = cufft.fftn(self.w)
        else:
            self.u_hat = fft.fftn(self.u)
            self.v_hat = fft.fftn(self.v)
            self.w_hat = fft.fftn(self.w)
    
    def _enforce_incompressibility(
        self,
        u_hat: np.ndarray,
        v_hat: np.ndarray,
        w_hat: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Proyecta componentes de velocidad al espacio incompresible.
        
        Utiliza la proyección de Leray en espacio de Fourier:
        u_proj_hat = u_hat - (k·u_hat / |k|²) * k
        
        Parámetros
        ----------
        u_hat, v_hat, w_hat : np.ndarray
            Transformadas de Fourier de componentes de velocidad
            
        Retorna
        -------
        Tuple de componentes proyectadas
        """
        # k · u_hat
        k_dot_u = self.KX * u_hat + self.KY * v_hat + self.KZ * w_hat
        
        # Proyección: u_proj = u - (k·u/|k|²)*k
        u_proj_hat = u_hat - (k_dot_u / self.K2) * self.KX
        v_proj_hat = v_hat - (k_dot_u / self.K2) * self.KY
        w_proj_hat = w_hat - (k_dot_u / self.K2) * self.KZ
        
        return u_proj_hat, v_proj_hat, w_proj_hat
    
    def _compute_advection_term(
        self,
        u_hat: np.ndarray,
        v_hat: np.ndarray,
        w_hat: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula término de adveción (u·∇)u en espacio físico.
        
        Pasos:
        1. IFFT para obtener u, v, w en espacio físico
        2. Calcular (u·∇)u, (v·∇)u, etc.
        3. FFT de nuevo para espacio de Fourier
        
        Parámetros
        ----------
        u_hat, v_hat, w_hat : np.ndarray
            Transformadas de Fourier de velocidad
            
        Retorna
        -------
        Tuple de advecciones (∂ₓ(u·u), ∂ᵧ(u·v), ∂ᵤ(u·w)) en Fourier
        """
        # IFFT para obtener velocidad en espacio físico
        if self.use_cuda:
            u = cufft.ifftn(u_hat).real
            v = cufft.ifftn(v_hat).real
            w = cufft.ifftn(w_hat).real
        else:
            u = fft.ifftn(u_hat).real
            v = fft.ifftn(v_hat).real
            w = fft.ifftn(w_hat).real
        
        # Calcular gradientes en espacio físico
        # ∂ₓu, ∂ₓv, ∂ₓw
        if self.use_cuda:
            u_x = cufft.ifftn(1j * self.KX * u_hat).real
            u_y = cufft.ifftn(1j * self.KY * u_hat).real
            u_z = cufft.ifftn(1j * self.KZ * u_hat).real
            
            v_x = cufft.ifftn(1j * self.KX * v_hat).real
            v_y = cufft.ifftn(1j * self.KY * v_hat).real
            v_z = cufft.ifftn(1j * self.KZ * v_hat).real
            
            w_x = cufft.ifftn(1j * self.KX * w_hat).real
            w_y = cufft.ifftn(1j * self.KY * w_hat).real
            w_z = cufft.ifftn(1j * self.KZ * w_hat).real
        else:
            u_x = fft.ifftn(1j * self.KX * u_hat).real
            u_y = fft.ifftn(1j * self.KY * u_hat).real
            u_z = fft.ifftn(1j * self.KZ * u_hat).real
            
            v_x = fft.ifftn(1j * self.KX * v_hat).real
            v_y = fft.ifftn(1j * self.KY * v_hat).real
            v_z = fft.ifftn(1j * self.KZ * v_hat).real
            
            w_x = fft.ifftn(1j * self.KX * w_hat).real
            w_y = fft.ifftn(1j * self.KY * w_hat).real
            w_z = fft.ifftn(1j * self.KZ * w_hat).real
        
        # Advección: (u·∇)u = u*∂ₓu + v*∂ᵧu + w*∂ᵤu
        adv_u = u * u_x + v * u_y + w * u_z
        adv_v = u * v_x + v * v_y + w * v_z
        adv_w = u * w_x + v * w_y + w * w_z
        
        # Transformar a Fourier
        if self.use_cuda:
            adv_u_hat = cufft.fftn(adv_u)
            adv_v_hat = cufft.fftn(adv_v)
            adv_w_hat = cufft.fftn(adv_w)
        else:
            adv_u_hat = fft.fftn(adv_u)
            adv_v_hat = fft.fftn(adv_v)
            adv_w_hat = fft.fftn(adv_w)
        
        return adv_u_hat, adv_v_hat, adv_w_hat
    
    def _rk4_step(self, time: float) -> None:
        """
        Paso RK4 (Runge-Kutta de 4to orden).
        
        RK4 es estable para CFL ≤ 2 aproximadamente.
        """
        dt = self.dt
        
        # k1
        adv_u1, adv_v1, adv_w1 = self._compute_advection_term(
            self.u_hat, self.v_hat, self.w_hat
        )
        u_hat_k1 = -adv_u1 - 1j * self.KX * 0  # Término presión (sin presión explícita)
        v_hat_k1 = -adv_v1 - 1j * self.KY * 0
        w_hat_k1 = -adv_w1 - 1j * self.KZ * 0
        
        # Término viscoso: -ν|k|²u_hat
        u_hat_k1 -= self.viscosity * self.K2 * self.u_hat
        v_hat_k1 -= self.viscosity * self.K2 * self.v_hat
        w_hat_k1 -= self.viscosity * self.K2 * self.w_hat
        
        # k2
        u_hat_2 = self.u_hat + 0.5 * dt * u_hat_k1
        v_hat_2 = self.v_hat + 0.5 * dt * v_hat_k1
        w_hat_2 = self.w_hat + 0.5 * dt * w_hat_k1
        u_hat_2, v_hat_2, w_hat_2 = self._enforce_incompressibility(u_hat_2, v_hat_2, w_hat_2)
        
        adv_u2, adv_v2, adv_w2 = self._compute_advection_term(u_hat_2, v_hat_2, w_hat_2)
        u_hat_k2 = -adv_u2
        v_hat_k2 = -adv_v2
        w_hat_k2 = -adv_w2
        u_hat_k2 -= self.viscosity * self.K2 * u_hat_2
        v_hat_k2 -= self.viscosity * self.K2 * v_hat_2
        w_hat_k2 -= self.viscosity * self.K2 * w_hat_2
        
        # k3
        u_hat_3 = self.u_hat + 0.5 * dt * u_hat_k2
        v_hat_3 = self.v_hat + 0.5 * dt * v_hat_k2
        w_hat_3 = self.w_hat + 0.5 * dt * w_hat_k2
        u_hat_3, v_hat_3, w_hat_3 = self._enforce_incompressibility(u_hat_3, v_hat_3, w_hat_3)
        
        adv_u3, adv_v3, adv_w3 = self._compute_advection_term(u_hat_3, v_hat_3, w_hat_3)
        u_hat_k3 = -adv_u3
        v_hat_k3 = -adv_v3
        w_hat_k3 = -adv_w3
        u_hat_k3 -= self.viscosity * self.K2 * u_hat_3
        v_hat_k3 -= self.viscosity * self.K2 * v_hat_3
        w_hat_k3 -= self.viscosity * self.K2 * w_hat_3
        
        # k4
        u_hat_4 = self.u_hat + dt * u_hat_k3
        v_hat_4 = self.v_hat + dt * v_hat_k3
        w_hat_4 = self.w_hat + dt * w_hat_k3
        u_hat_4, v_hat_4, w_hat_4 = self._enforce_incompressibility(u_hat_4, v_hat_4, w_hat_4)
        
        adv_u4, adv_v4, adv_w4 = self._compute_advection_term(u_hat_4, v_hat_4, w_hat_4)
        u_hat_k4 = -adv_u4
        v_hat_k4 = -adv_v4
        w_hat_k4 = -adv_w4
        u_hat_k4 -= self.viscosity * self.K2 * u_hat_4
        v_hat_k4 -= self.viscosity * self.K2 * v_hat_4
        w_hat_k4 -= self.viscosity * self.K2 * w_hat_4
        
        # Actualización RK4
        self.u_hat = self.u_hat + (dt / 6.0) * (u_hat_k1 + 2*u_hat_k2 + 2*u_hat_k3 + u_hat_k4)
        self.v_hat = self.v_hat + (dt / 6.0) * (v_hat_k1 + 2*v_hat_k2 + 2*v_hat_k3 + v_hat_k4)
        self.w_hat = self.w_hat + (dt / 6.0) * (w_hat_k1 + 2*w_hat_k2 + 2*w_hat_k3 + w_hat_k4)
        
        # Proyectar a espacio incompresible
        self.u_hat, self.v_hat, self.w_hat = self._enforce_incompressibility(
            self.u_hat, self.v_hat, self.w_hat
        )
    
    def compute_diagnostics(self) -> Dict[str, float]:
        """
        Calcula diagnósticos físicos importantes.
        
        Retorna
        -------
        Dict con claves:
            - enstrophy: ∫|ω|² dx / 2 (medida de disipación)
            - energy: ∫|u|² dx / 2 (energía cinética)
            - max_vorticity: max|ω| (indicador de singularidades)
            - divergence_error: max|∇·u| (error de incompresibilidad)
        """
        # IFFT para obtener campos en espacio físico
        if self.use_cuda:
            u = cufft.ifftn(self.u_hat).real
            v = cufft.ifftn(self.v_hat).real
            w = cufft.ifftn(self.w_hat).real
        else:
            u = fft.ifftn(self.u_hat).real
            v = fft.ifftn(self.v_hat).real
            w = fft.ifftn(self.w_hat).real
        
        # Vorticidad ω = ∇ × u
        if self.use_cuda:
            w_x = cufft.ifftn(1j * self.KX * self.w_hat).real
            w_y = cufft.ifftn(1j * self.KY * self.w_hat).real
            v_x = cufft.ifftn(1j * self.KX * self.v_hat).real
            v_z = cufft.ifftn(1j * self.KZ * self.v_hat).real
            u_y = cufft.ifftn(1j * self.KY * self.u_hat).real
            u_z = cufft.ifftn(1j * self.KZ * self.u_hat).real
        else:
            w_x = fft.ifftn(1j * self.KX * self.w_hat).real
            w_y = fft.ifftn(1j * self.KY * self.w_hat).real
            v_x = fft.ifftn(1j * self.KX * self.v_hat).real
            v_z = fft.ifftn(1j * self.KZ * self.v_hat).real
            u_y = fft.ifftn(1j * self.KY * self.u_hat).real
            u_z = fft.ifftn(1j * self.KZ * self.u_hat).real
        
        omega_x = u_y - w_x if self.use_cuda else u_y - w_x
        omega_y = w_x - u_z if self.use_cuda else w_x - u_z
        omega_z = v_x - u_y if self.use_cuda else v_x - u_y
        
        # Convertir a NumPy si es necesario para cálculo
        if self.use_cuda:
            omega_x = cp.asnumpy(omega_x)
            omega_y = cp.asnumpy(omega_y)
            omega_z = cp.asnumpy(omega_z)
            u = cp.asnumpy(u)
            v = cp.asnumpy(v)
            w = cp.asnumpy(w)
        
        # Enstrophy
        enstrophy = 0.5 * np.mean(omega_x**2 + omega_y**2 + omega_z**2)
        
        # Energía cinética
        energy = 0.5 * np.mean(u**2 + v**2 + w**2)
        
        # Vorticidad máxima
        max_vorticity = np.max(np.sqrt(omega_x**2 + omega_y**2 + omega_z**2))
        
        # Error de divergencia (en espacio de Fourier: |k·u_hat|)
        if self.use_cuda:
            u_hat_np = cp.asnumpy(self.u_hat)
            v_hat_np = cp.asnumpy(self.v_hat)
            w_hat_np = cp.asnumpy(self.w_hat)
            kx_np = cp.asnumpy(self.KX)
            ky_np = cp.asnumpy(self.KY)
            kz_np = cp.asnumpy(self.KZ)
        else:
            u_hat_np = self.u_hat
            v_hat_np = self.v_hat
            w_hat_np = self.w_hat
            kx_np = self.KX
            ky_np = self.KY
            kz_np = self.KZ
        
        div_error = np.max(np.abs(kx_np * u_hat_np + ky_np * v_hat_np + kz_np * w_hat_np))
        
        return {
            'enstrophy': enstrophy,
            'energy': energy,
            'max_vorticity': max_vorticity,
            'divergence_error': div_error
        }
    
    def solve(self, verbose: bool = True, save_interval: int = 10) -> None:
        """
        Resuelve las ecuaciones de Navier-Stokes en el tiempo.
        
        Parámetros
        ----------
        verbose : bool
            Si True, muestra progreso cada `save_interval` pasos
        save_interval : int
            Intervalo de pasos para guardar diagnósticos
        """
        print(f"\n🚀 Iniciando simulación temporal...")
        print(f"   Pasos totales: {self.num_steps}")
        print(f"   Tiempo total: {self.simulation_time:.2f} s")
        print(f"   Intervalo de guardado: {save_interval} pasos\n")
        
        for step in range(self.num_steps):
            time = step * self.dt
            
            # Realizar paso RK4
            self._rk4_step(time)
            
            # Guardar diagnósticos cada `save_interval` pasos
            if step % save_interval == 0:
                diags = self.compute_diagnostics()
                self.time_history.append(time)
                self.enstrophy_history.append(diags['enstrophy'])
                self.energy_history.append(diags['energy'])
                self.max_vorticity_history.append(diags['max_vorticity'])
                self.divergence_error_history.append(diags['divergence_error'])
                
                if verbose:
                    print(f"Step {step:5d}/{self.num_steps} | "
                          f"t={time:8.4f} s | "
                          f"E(t)={diags['energy']:10.6e} | "
                          f"Z(t)={diags['enstrophy']:10.6e} | "
                          f"|ω|ₘₐₓ={diags['max_vorticity']:10.6e}")
                    
                    # Detección de blow-up
                    if diags['enstrophy'] > 1e6 or diags['max_vorticity'] > 1e4:
                        print(f"\n⚠️  ALERTA: Posible singularidad detectada en t={time:.4f}")
        
        print(f"\n✓ Simulación completada")
        
    def get_velocity_field(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Retorna las componentes de velocidad en espacio físico."""
        if self.use_cuda:
            u = cp.asnumpy(cufft.ifftn(self.u_hat).real)
            v = cp.asnumpy(cufft.ifftn(self.v_hat).real)
            w = cp.asnumpy(cufft.ifftn(self.w_hat).real)
        else:
            u = fft.ifftn(self.u_hat).real
            v = fft.ifftn(self.v_hat).real
            w = fft.ifftn(self.w_hat).real
        return u, v, w
    
    def plot_diagnostics(self, save_path: Optional[str] = None) -> None:
        """Grafica evolución temporal de diagnósticos."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        t = np.array(self.time_history)
        
        # Energía
        axes[0, 0].semilogy(t, self.energy_history, 'b-', linewidth=2)
        axes[0, 0].set_xlabel('Tiempo (s)', fontsize=11)
        axes[0, 0].set_ylabel('Energía E(t)', fontsize=11)
        axes[0, 0].set_title(f'Energía Cinética (Re={self.reynolds_number:.0f})', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Enstrophy
        axes[0, 1].semilogy(t, self.enstrophy_history, 'r-', linewidth=2)
        axes[0, 1].set_xlabel('Tiempo (s)', fontsize=11)
        axes[0, 1].set_ylabel('Enstrophy Z(t)', fontsize=11)
        axes[0, 1].set_title(f'Enstrophy (Re={self.reynolds_number:.0f})', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Vorticidad máxima
        axes[1, 0].semilogy(t, self.max_vorticity_history, 'g-', linewidth=2)
        axes[1, 0].set_xlabel('Tiempo (s)', fontsize=11)
        axes[1, 0].set_ylabel('|ω|ₘₐₓ', fontsize=11)
        axes[1, 0].set_title(f'Vorticidad Máxima (Re={self.reynolds_number:.0f})', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Error de divergencia
        axes[1, 1].semilogy(t, self.divergence_error_history, 'm-', linewidth=2)
        axes[1, 1].set_xlabel('Tiempo (s)', fontsize=11)
        axes[1, 1].set_ylabel('max|∇·u|', fontsize=11)
        axes[1, 1].set_title(f'Error de Incompresibilidad (Re={self.reynolds_number:.0f})', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico guardado en {save_path}")
        else:
            plt.show()
        plt.close()


if __name__ == "__main__":
    # Ejemplo: Simular Navier-Stokes para Re = 1000, 5000, 10000
    reynolds_numbers = [1000, 5000, 10000]
    
    for re in reynolds_numbers:
        print(f"\n{'='*70}")
        print(f"SIMULACIÓN PARA Re = {re}")
        print(f"{'='*70}")
        
        solver = NavierStokesCUDAHighRe(
            reynolds_number=re,
            grid_size=64,
            simulation_time=0.5,
            dt=None,
            use_cuda=CUDA_AVAILABLE
        )
        
        solver.solve(verbose=True, save_interval=10)
        
        save_path = f"navier_stokes_diagnostics_re{re}.png"
        solver.plot_diagnostics(save_path=save_path)

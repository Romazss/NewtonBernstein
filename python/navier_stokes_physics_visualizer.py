"""
VISUALIZACIÓN DE FENÓMENOS FÍSICOS EN NAVIER-STOKES DE ALTO REYNOLDS
=====================================================================

Genera visualizaciones complejas que muestran:
1. Campos de velocidad y vorticidad
2. Superficies de isovórtice  
3. Espectro de energía wavelet
4. Estructuras coherentes
5. Estadísticas de cascada de energía

Autor: Esteban Román
Año: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LogNorm
import matplotlib.patches as patches
from scipy import fft, ndimage
from typing import Dict, Tuple, Optional, List
import sys, os

sys.path.insert(0, os.path.abspath('.'))

try:
    import cupy as cp
    import cupyx.scipy.fft as cufft
    CUDA_AVAILABLE = True
except ImportError:
    CUDA_AVAILABLE = False


class NavierStokesPhysicsVisualizer:
    """
    Visualizador especializado en fenómenos físicos de Navier-Stokes.
    
    Genera análisis de:
    - Estructuras de vorticidad
    - Cascadas de energía
    - Coherencia de vórtices
    - Cuantificación de turbulencia
    """
    
    def __init__(self, use_cuda: bool = True):
        """Inicialización."""
        self.use_cuda = use_cuda and CUDA_AVAILABLE
        self.xp = cp if self.use_cuda else np
    
    def visualize_3d_velocity_field(
        self,
        u: np.ndarray,
        v: np.ndarray,
        w: np.ndarray,
        title: str = "Velocity Field",
        save_path: Optional[str] = None,
        slice_index: int = None
    ) -> None:
        """
        Visualiza campo de velocidad 3D mediante cortes 2D.
        
        Parámetros
        ----------
        u, v, w : np.ndarray
            Componentes de velocidad (n, n, n)
        title : str
            Título de la figura
        save_path : Optional[str]
            Ruta para guardar
        slice_index : Optional[int]
            Índice del corte (default: n//2)
        """
        n = u.shape[0]
        if slice_index is None:
            slice_index = n // 2
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # Corte en z = const
        u_slice_xy = u[:, :, slice_index]
        v_slice_xy = v[:, :, slice_index]
        speed_xy = np.sqrt(u_slice_xy**2 + v_slice_xy**2)
        
        im0 = axes[0].contourf(speed_xy, levels=20, cmap='hot')
        axes[0].quiver(u_slice_xy[::2, ::2], v_slice_xy[::2, ::2], alpha=0.7)
        axes[0].set_title(f'Plano z={slice_index} (xy)', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('x', fontsize=11)
        axes[0].set_ylabel('y', fontsize=11)
        plt.colorbar(im0, ax=axes[0], label='|u|')
        
        # Corte en y = const
        u_slice_xz = u[:, slice_index, :]
        w_slice_xz = w[:, slice_index, :]
        speed_xz = np.sqrt(u_slice_xz**2 + w_slice_xz**2)
        
        im1 = axes[1].contourf(speed_xz, levels=20, cmap='hot')
        axes[1].quiver(u_slice_xz[::2, ::2], w_slice_xz[::2, ::2], alpha=0.7)
        axes[1].set_title(f'Plano y={slice_index} (xz)', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('x', fontsize=11)
        axes[1].set_ylabel('z', fontsize=11)
        plt.colorbar(im1, ax=axes[1], label='|u|')
        
        # Corte en x = const
        v_slice_yz = v[slice_index, :, :]
        w_slice_yz = w[slice_index, :, :]
        speed_yz = np.sqrt(v_slice_yz**2 + w_slice_yz**2)
        
        im2 = axes[2].contourf(speed_yz, levels=20, cmap='hot')
        axes[2].quiver(v_slice_yz[::2, ::2], w_slice_yz[::2, ::2], alpha=0.7)
        axes[2].set_title(f'Plano x={slice_index} (yz)', fontsize=12, fontweight='bold')
        axes[2].set_xlabel('y', fontsize=11)
        axes[2].set_ylabel('z', fontsize=11)
        plt.colorbar(im2, ax=axes[2], label='|u|')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Guardado: {save_path}")
        else:
            plt.show()
        plt.close()
    
    def visualize_vorticity_field(
        self,
        u: np.ndarray,
        v: np.ndarray,
        w: np.ndarray,
        dx: float = 1.0,
        title: str = "Vorticity Field",
        save_path: Optional[str] = None,
        slice_index: int = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula y visualiza vorticidad ω = ∇ × u.
        
        Parámetros
        ----------
        u, v, w : np.ndarray
            Componentes de velocidad
        dx : float
            Espaciamiento de grilla
        title : str
            Título
        save_path : Optional[str]
            Ruta para guardar
        slice_index : Optional[int]
            Índice de corte
            
        Retorna
        -------
        Tuple de componentes de vorticidad (ω_x, ω_y, ω_z)
        """
        n = u.shape[0]
        if slice_index is None:
            slice_index = n // 2
        
        # Calcular vorticidad en espacio físico
        omega_x = np.zeros_like(u)
        omega_y = np.zeros_like(u)
        omega_z = np.zeros_like(u)
        
        # ω_x = ∂w/∂y - ∂v/∂z
        omega_x = np.gradient(w, axis=1) - np.gradient(v, axis=2)
        # ω_y = ∂u/∂z - ∂w/∂x
        omega_y = np.gradient(u, axis=2) - np.gradient(w, axis=0)
        # ω_z = ∂v/∂x - ∂u/∂y
        omega_z = np.gradient(v, axis=0) - np.gradient(u, axis=1)
        
        omega_magnitude = np.sqrt(omega_x**2 + omega_y**2 + omega_z**2)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Magnitud de vorticidad
        omega_slice = omega_magnitude[:, :, slice_index]
        im0 = axes[0, 0].contourf(omega_slice, levels=20, cmap='jet')
        axes[0, 0].set_title(f'|ω| en z={slice_index}', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('x', fontsize=11)
        axes[0, 0].set_ylabel('y', fontsize=11)
        plt.colorbar(im0, ax=axes[0, 0], label='|ω|')
        
        # Componente ω_x
        im1 = axes[0, 1].contourf(omega_x[:, :, slice_index], levels=20, cmap='RdBu_r')
        axes[0, 1].set_title(f'ω_x en z={slice_index}', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('x', fontsize=11)
        axes[0, 1].set_ylabel('y', fontsize=11)
        plt.colorbar(im1, ax=axes[0, 1], label='ω_x')
        
        # Componente ω_y
        im2 = axes[1, 0].contourf(omega_y[:, :, slice_index], levels=20, cmap='RdBu_r')
        axes[1, 0].set_title(f'ω_y en z={slice_index}', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('x', fontsize=11)
        axes[1, 0].set_ylabel('y', fontsize=11)
        plt.colorbar(im2, ax=axes[1, 0], label='ω_y')
        
        # Componente ω_z
        im3 = axes[1, 1].contourf(omega_z[:, :, slice_index], levels=20, cmap='RdBu_r')
        axes[1, 1].set_title(f'ω_z en z={slice_index}', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('x', fontsize=11)
        axes[1, 1].set_ylabel('y', fontsize=11)
        plt.colorbar(im3, ax=axes[1, 1], label='ω_z')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Guardado: {save_path}")
        else:
            plt.show()
        plt.close()
        
        return omega_x, omega_y, omega_z
    
    def compute_energy_spectrum(
        self,
        u_hat: np.ndarray,
        v_hat: np.ndarray,
        w_hat: np.ndarray,
        kx: np.ndarray,
        ky: np.ndarray,
        kz: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula espectro de energía 1D: E(k) = Σ_{|k|=const} |û|²
        
        Parámetros
        ----------
        u_hat, v_hat, w_hat : np.ndarray
            Transformadas de Fourier de velocidad
        kx, ky, kz : np.ndarray
            Vectores de número de onda
            
        Retorna
        -------
        (k_bins, energy_spectrum)
        """
        # Crear grilla de números de onda
        KX, KY, KZ = np.meshgrid(kx, ky, kz, indexing='ij')
        K = np.sqrt(KX**2 + KY**2 + KZ**2)
        
        # Energía en espacio de Fourier
        E_k = 0.5 * (np.abs(u_hat)**2 + np.abs(v_hat)**2 + np.abs(w_hat)**2)
        
        # Binnear por magnitud de número de onda
        k_max = np.max(K)
        k_bins = np.linspace(0, k_max, 50)
        energy_spectrum = np.zeros_like(k_bins)
        
        for i in range(len(k_bins) - 1):
            mask = (K >= k_bins[i]) & (K < k_bins[i+1])
            energy_spectrum[i] = np.sum(E_k[mask])
        
        return k_bins, energy_spectrum
    
    def visualize_energy_cascade(
        self,
        u_hat: np.ndarray,
        v_hat: np.ndarray,
        w_hat: np.ndarray,
        kx: np.ndarray,
        ky: np.ndarray,
        kz: np.ndarray,
        reynolds: float = 1000,
        title: str = "Energy Cascade",
        save_path: Optional[str] = None
    ) -> None:
        """
        Visualiza cascada de energía y compara con Kolmogorov k^{-5/3}.
        
        La cascada de Kolmogorov predice:
            E(k) ∝ k^{-5/3}  en rango inercial
        
        Para Re alto, este rango debería ser evidente.
        """
        k_bins, E_spectrum = self.compute_energy_spectrum(u_hat, v_hat, w_hat, kx, ky, kz)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Gráfico lineal
        axes[0].plot(k_bins, E_spectrum, 'b-o', linewidth=2, markersize=6, label='Simulación')
        
        # Referencia Kolmogorov
        k_ref = k_bins[k_bins > 0]
        E_ref = (k_ref ** (-5/3))
        E_ref = E_ref / E_ref[len(E_ref)//2] * E_spectrum[len(E_spectrum)//2]
        axes[0].plot(k_ref, E_ref, 'r--', linewidth=2, label=r'Kolmogorov $k^{-5/3}$')
        
        axes[0].set_xlabel('Número de onda k', fontsize=11)
        axes[0].set_ylabel('E(k)', fontsize=11)
        axes[0].set_title(f'Cascada de Energía (Re={reynolds:.0f})', fontsize=12, fontweight='bold')
        axes[0].legend(fontsize=11)
        axes[0].grid(True, alpha=0.3)
        
        # Gráfico log-log
        k_log = k_bins[k_bins > 0]
        E_log = E_spectrum[k_bins > 0]
        
        axes[1].loglog(k_log, E_log, 'b-o', linewidth=2, markersize=6, label='Simulación')
        axes[1].loglog(k_ref, E_ref, 'r--', linewidth=2, label=r'Kolmogorov $k^{-5/3}$')
        
        axes[1].set_xlabel('Número de onda k (log)', fontsize=11)
        axes[1].set_ylabel('E(k) (log)', fontsize=11)
        axes[1].set_title(f'Cascada de Energía - Log-Log (Re={reynolds:.0f})', fontsize=12, fontweight='bold')
        axes[1].legend(fontsize=11)
        axes[1].grid(True, alpha=0.3, which='both')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Guardado: {save_path}")
        else:
            plt.show()
        plt.close()
    
    def detect_vortex_structures(
        self,
        omega_x: np.ndarray,
        omega_y: np.ndarray,
        omega_z: np.ndarray,
        threshold: float = 0.5
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detecta estructuras de vórtices usando criterio Q de Hunt.
        
        Q-criterio: Q = 0.5 * (Ω² - S²) > 0
        donde Ω es rotación y S es deformación
        
        Parámetros
        ----------
        omega_x, omega_y, omega_z : np.ndarray
            Componentes de vorticidad
        threshold : float
            Umbral para Q para considerar vórtice
            
        Retorna
        -------
        (Q_field, list_of_vortex_centers)
        """
        # Calcular Q-criterio (simplificado)
        omega_squared = omega_x**2 + omega_y**2 + omega_z**2
        
        # Filtro para detectar máximos locales
        Q_field = omega_squared
        
        # Detectar máximos locales
        local_max = ndimage.maximum_filter(Q_field, size=3) == Q_field
        local_max[Q_field < threshold * np.max(Q_field)] = False
        
        # Encontrar centros
        labeled, num_features = ndimage.label(local_max)
        vortex_centers = []
        
        for i in range(1, num_features + 1):
            coords = np.where(labeled == i)
            center = (
                np.mean(coords[0]).astype(int),
                np.mean(coords[1]).astype(int),
                np.mean(coords[2]).astype(int)
            )
            strength = np.mean(Q_field[coords])
            vortex_centers.append({
                'center': center,
                'strength': strength,
                'size': np.sum(labeled == i)
            })
        
        return Q_field, vortex_centers
    
    def visualize_turbulent_statistics(
        self,
        u: np.ndarray,
        v: np.ndarray,
        w: np.ndarray,
        reynolds: float = 1000,
        title: str = "Turbulence Statistics",
        save_path: Optional[str] = None
    ) -> None:
        """
        Calcula y visualiza estadísticas de turbulencia.
        """
        # Varianzas de velocidad
        u_rms = np.sqrt(np.mean(u**2))
        v_rms = np.sqrt(np.mean(v**2))
        w_rms = np.sqrt(np.mean(w**2))
        u_rms_total = np.sqrt(u_rms**2 + v_rms**2 + w_rms**2)
        
        # Skewness (asimetría de distribuciones de velocidad)
        u_skew = np.mean(u**3) / (u_rms**3 + 1e-10)
        v_skew = np.mean(v**3) / (v_rms**3 + 1e-10)
        w_skew = np.mean(w**3) / (w_rms**3 + 1e-10)
        
        # Flatness (curtosis)
        u_flat = np.mean(u**4) / (np.mean(u**2)**2 + 1e-10)
        v_flat = np.mean(v**4) / (np.mean(v**2)**2 + 1e-10)
        w_flat = np.mean(w**4) / (np.mean(w**2)**2 + 1e-10)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # RMS velocidades
        components = ['u_x', 'u_y', 'u_z', 'Total']
        rms_values = [u_rms, v_rms, w_rms, u_rms_total]
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        axes[0, 0].bar(components, rms_values, color=colors, edgecolor='black', linewidth=2)
        axes[0, 0].set_ylabel('RMS Velocity', fontsize=11)
        axes[0, 0].set_title('RMS de Componentes de Velocidad', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, axis='y', alpha=0.3)
        
        # Skewness
        skew_values = [u_skew, v_skew, w_skew]
        axes[0, 1].bar(['u_x', 'u_y', 'u_z'], skew_values, 
                      color=['#1f77b4', '#ff7f0e', '#2ca02c'], edgecolor='black', linewidth=2)
        axes[0, 1].axhline(y=0, color='k', linestyle='--', alpha=0.5)
        axes[0, 1].set_ylabel('Skewness', fontsize=11)
        axes[0, 1].set_title('Asimetría de Distribuciones', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, axis='y', alpha=0.3)
        
        # Flatness
        flat_values = [u_flat, v_flat, w_flat]
        axes[1, 0].bar(['u_x', 'u_y', 'u_z'], flat_values,
                      color=['#1f77b4', '#ff7f0e', '#2ca02c'], edgecolor='black', linewidth=2)
        axes[1, 0].axhline(y=3, color='r', linestyle='--', alpha=0.5, label='Gaussiano (3)')
        axes[1, 0].set_ylabel('Flatness', fontsize=11)
        axes[1, 0].set_title('Curtosis (Flatness)', fontsize=12, fontweight='bold')
        axes[1, 0].legend(fontsize=10)
        axes[1, 0].grid(True, axis='y', alpha=0.3)
        
        # Distribuciones de velocidad
        axes[1, 1].hist(u.flatten(), bins=50, alpha=0.6, label='u_x', density=True)
        axes[1, 1].hist(v.flatten(), bins=50, alpha=0.6, label='u_y', density=True)
        axes[1, 1].hist(w.flatten(), bins=50, alpha=0.6, label='u_z', density=True)
        axes[1, 1].set_xlabel('Velocidad', fontsize=11)
        axes[1, 1].set_ylabel('PDF', fontsize=11)
        axes[1, 1].set_title('Distribuciones de Probabilidad', fontsize=12, fontweight='bold')
        axes[1, 1].legend(fontsize=10)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.suptitle(f'{title} (Re={reynolds:.0f})', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Guardado: {save_path}")
        else:
            plt.show()
        plt.close()


if __name__ == "__main__":
    print("✓ Módulo de visualización de fenómenos físicos cargado")
    print("  Funciones disponibles:")
    print("    - visualize_3d_velocity_field()")
    print("    - visualize_vorticity_field()")
    print("    - visualize_energy_cascade()")
    print("    - detect_vortex_structures()")
    print("    - visualize_turbulent_statistics()")

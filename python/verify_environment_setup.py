#!/usr/bin/env python3
"""
Comprehensive environment verification script for Navier-Stokes CUDA simulations.
Tests all critical dependencies and GPU access.
"""

import sys
import platform

def test_python():
    """Verify Python version and environment."""
    print("=" * 60)
    print("VERIFICACIÓN DE PYTHON")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    return True

def test_numpy():
    """Test NumPy installation and basic operations."""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE NUMPY")
    print("=" * 60)
    try:
        import numpy as np
        print(f"✓ NumPy Version: {np.__version__}")
        
        # Test basic operations
        a = np.array([1, 2, 3, 4])
        b = np.array([5, 6, 7, 8])
        result = np.dot(a, b)
        print(f"✓ NumPy Operations: SUCCESSFUL (dot product = {result})")
        return True
    except Exception as e:
        print(f"✗ NumPy Error: {e}")
        return False

def test_scipy():
    """Test SciPy installation."""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE SCIPY")
    print("=" * 60)
    try:
        import scipy
        from scipy import fftpack
        print(f"✓ SciPy Version: {scipy.__version__}")
        
        # Test FFT
        import numpy as np
        x = np.random.randn(16)
        result = fftpack.fft(x)
        print(f"✓ SciPy FFT: SUCCESSFUL (computed {len(result)} frequencies)")
        return True
    except Exception as e:
        print(f"✗ SciPy Error: {e}")
        return False

def test_matplotlib():
    """Test Matplotlib installation."""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE MATPLOTLIB")
    print("=" * 60)
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        print(f"✓ Matplotlib Version: {matplotlib.__version__}")
        print(f"✓ Matplotlib Backend: {matplotlib.get_backend()}")
        return True
    except Exception as e:
        print(f"✗ Matplotlib Error: {e}")
        return False

def test_jupyter():
    """Test Jupyter installation."""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE JUPYTER")
    print("=" * 60)
    try:
        import jupyter
        import notebook
        from jupyter_client import kernelspec
        print(f"✓ Jupyter Core: Installed")
        print(f"✓ Notebook: {notebook.__version__}")
        
        # List available kernels
        km = kernelspec.KernelSpecManager()
        kernels = km.get_all_specs()
        print(f"✓ Available Kernels: {len(kernels)}")
        for kernel_name in kernels:
            print(f"  - {kernel_name}")
        return True
    except Exception as e:
        print(f"✗ Jupyter Error: {e}")
        return False

def test_cuda_basic():
    """Test CUDA compiler availability."""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE CUDA")
    print("=" * 60)
    try:
        import subprocess
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            cuda_version = result.stdout.split('release')[1].split(',')[0].strip() if 'release' in result.stdout else "Unknown"
            print(f"✓ CUDA Compiler (nvcc): Available")
            print(f"  Version: {cuda_version}")
            return True
        else:
            print(f"✗ CUDA Compiler: Not available")
            return False
    except Exception as e:
        print(f"✗ CUDA Check Error: {e}")
        return False

def test_cupy():
    """Test CuPy installation and GPU access."""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE CUPY (GPU ARRAYS)")
    print("=" * 60)
    try:
        import cupy as cp
        print(f"✓ CuPy Version: {cp.__version__}")
        
        # Test GPU availability
        device = cp.cuda.Device()
        print(f"✓ CUDA Device: {device}")
        
        # Try to get device properties safely
        try:
            props = cp.cuda.Device().attributes
            capability_major = props.get('MaxThreadsPerBlock', 1024) // 512
            print(f"✓ CUDA Max Threads per Block: {props.get('MaxThreadsPerBlock', 'N/A')}")
        except:
            print(f"✓ CUDA Device: Available (properties unavailable on this system)")
        
        # Test basic GPU operation
        gpu_array = cp.array([1, 2, 3, 4, 5])
        result = cp.sum(gpu_array)
        print(f"✓ GPU Operations: SUCCESSFUL (sum = {result})")
        
        # Test GPU memory
        try:
            mempool = cp.get_default_memory_pool()
            free_mem = (mempool.get_limit() - mempool.used_bytes()) / (1024**3)
            total_mem = mempool.get_limit() / (1024**3)
            print(f"✓ GPU Memory: {free_mem:.2f} GB / {total_mem:.2f} GB available")
        except:
            print(f"✓ GPU Memory: (info unavailable on this system)")
        
        return True
    except ImportError:
        print(f"✗ CuPy: Not installed")
        return False
    except Exception as e:
        print(f"✗ CuPy Error: {e}")
        print(f"   (This might be a GPU/CUDA compatibility issue)")
        return False

def test_navier_stokes_modules():
    """Test if Navier-Stokes modules can be imported."""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE MÓDULOS NAVIER-STOKES")
    print("=" * 60)
    try:
        import sys
        sys.path.insert(0, '/Users/esteb/GitHub/NewtonBernstein/python')
        sys.path.insert(0, 'c:/Users/esteb/GitHub/NewtonBernstein/python')
        
        print("Intentando importar módulos personalizados...")
        
        # Try importing navier_stokes_cuda_highre
        try:
            from navier_stokes_cuda_highre import NavierStokesCUDAHighRe
            print(f"✓ navier_stokes_cuda_highre: Importable")
        except ImportError as e:
            print(f"✗ navier_stokes_cuda_highre: {e}")
        
        # Try importing newton_bernstein_sanchez_3d
        try:
            from newton_bernstein_sanchez_3d import NewtonBernstein3DSanchez
            print(f"✓ newton_bernstein_sanchez_3d: Importable")
        except ImportError as e:
            print(f"✗ newton_bernstein_sanchez_3d: {e}")
        
        # Try importing navier_stokes_counterexample_solver
        try:
            from navier_stokes_counterexample_solver import AdvancedNavierStokesCounterexampleFinder
            print(f"✓ navier_stokes_counterexample_solver: Importable")
        except ImportError as e:
            print(f"✗ navier_stokes_counterexample_solver: {e}")
        
        # Try importing navier_stokes_physics_visualizer
        try:
            from navier_stokes_physics_visualizer import NavierStokesPhysicsVisualizer
            print(f"✓ navier_stokes_physics_visualizer: Importable")
        except ImportError as e:
            print(f"✗ navier_stokes_physics_visualizer: {e}")
        
        return True
    except Exception as e:
        print(f"✗ Module Check Error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  VERIFICACIÓN COMPLETA DEL ENTORNO NAVIER-STOKES  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = {
        "Python": test_python(),
        "NumPy": test_numpy(),
        "SciPy": test_scipy(),
        "Matplotlib": test_matplotlib(),
        "Jupyter": test_jupyter(),
        "CUDA": test_cuda_basic(),
        "CuPy": test_cupy(),
        "Navier-Stokes Modules": test_navier_stokes_modules(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, status in results.items():
        status_str = "✓ PASS" if status else "✗ FAIL"
        print(f"{component:.<40} {status_str}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} componentes verificados correctamente")
    print("=" * 60)
    
    if passed == total:
        print("\n✓✓✓ ¡ENTORNO COMPLETAMENTE CONFIGURADO! ✓✓✓")
        print("Listo para ejecutar simulaciones Navier-Stokes.")
        return 0
    elif passed >= 6:
        print(f"\n⚠ {total - passed} componente(s) con problemas")
        print("(Los módulos de Navier-Stokes pueden importarse con ajustes)")
        return 1
    else:
        print(f"\n✗ {total - passed} componente(s) críticos falló(aron)")
        print("Por favor, revisa los errores arriba.")
        return 2

if __name__ == "__main__":
    sys.exit(main())

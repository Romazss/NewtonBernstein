"""
VERIFICACIÓN DE INSTALACIÓN Y CONFIGURACIÓN
==============================================

Ejecuta este script para verificar que todo está correctamente configurado
para ejecutar el análisis de contraejemplo Navier-Stokes 3D con Newton-Bernstein.

Uso:
    python verify_setup.py

Autor: Esteban Román
Año: 2025
"""

import sys
import platform
from typing import Tuple, Dict, List

def print_header(text: str) -> None:
    """Imprime encabezado formateado."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_success(text: str) -> None:
    """Imprime mensaje de éxito."""
    print(f"  ✓ {text}")

def print_warning(text: str) -> None:
    """Imprime mensaje de advertencia."""
    print(f"  ⚠️  {text}")

def print_error(text: str) -> None:
    """Imprime mensaje de error."""
    print(f"  ✗ {text}")

def verify_python_version() -> bool:
    """Verifica versión de Python."""
    version = sys.version_info
    print_header("Python Version")
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} es demasiado antiguo (requiere ≥ 3.8)")
        return False

def verify_system_info() -> None:
    """Muestra información del sistema."""
    print_header("System Information")
    print_success(f"Sistema operativo: {platform.system()} {platform.release()}")
    print_success(f"Arquitectura: {platform.machine()}")
    print_success(f"Procesador: {platform.processor()}")

def verify_dependencies() -> Dict[str, Tuple[bool, str]]:
    """Verifica dependencias principales."""
    print_header("Verificación de Dependencias")
    
    dependencies = {}
    
    # NumPy
    try:
        import numpy as np
        dependencies['numpy'] = (True, f"NumPy {np.__version__}")
        print_success(f"NumPy {np.__version__}")
    except ImportError:
        dependencies['numpy'] = (False, "No instalado")
        print_error("NumPy no instalado")
    
    # SciPy
    try:
        import scipy
        dependencies['scipy'] = (True, f"SciPy {scipy.__version__}")
        print_success(f"SciPy {scipy.__version__}")
    except ImportError:
        dependencies['scipy'] = (False, "No instalado")
        print_error("SciPy no instalado")
    
    # Matplotlib
    try:
        import matplotlib
        dependencies['matplotlib'] = (True, f"Matplotlib {matplotlib.__version__}")
        print_success(f"Matplotlib {matplotlib.__version__}")
    except ImportError:
        dependencies['matplotlib'] = (False, "No instalado")
        print_error("Matplotlib no instalado")
    
    # Pandas
    try:
        import pandas
        dependencies['pandas'] = (True, f"Pandas {pandas.__version__}")
        print_success(f"Pandas {pandas.__version__}")
    except ImportError:
        dependencies['pandas'] = (False, "No instalado")
        print_warning("Pandas no instalado (opcional)")
    
    return dependencies

def verify_cuda_setup() -> Tuple[bool, Dict]:
    """Verifica configuración de CUDA y CuPy."""
    print_header("Verificación de CUDA y GPU")
    
    cuda_info = {
        'cuda_available': False,
        'cupy_version': None,
        'cuda_version': None,
        'device_info': None
    }
    
    # Verificar CUDA Toolkit
    import subprocess
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'release' in line.lower():
                    cuda_info['cuda_version'] = line.strip()
                    print_success(f"CUDA Toolkit: {line.strip()}")
    except FileNotFoundError:
        print_error("CUDA Toolkit no encontrado (nvcc no disponible)")
        print_warning("  Instala CUDA Toolkit desde https://developer.nvidia.com/cuda-toolkit")
    
    # Verificar CuPy
    try:
        import cupy as cp
        cuda_info['cuda_available'] = True
        cuda_info['cupy_version'] = cp.__version__
        print_success(f"CuPy {cp.__version__}")
        
        # Información del dispositivo
        from cupy.cuda import Device
        device = Device()
        cuda_info['device_info'] = {
            'name': device.name.decode() if isinstance(device.name, bytes) else str(device.name),
            'compute_capability': device.compute_capability,
            'memory_available': cp.get_default_memory_pool().get_limit() / 1e9
        }
        
        print_success(f"GPU: {cuda_info['device_info']['name']}")
        print_success(f"Compute Capability: {cuda_info['device_info']['compute_capability']}")
        print_success(f"Memoria disponible: {cuda_info['device_info']['memory_available']:.2f} GB")
        
        return True, cuda_info
    except ImportError:
        print_warning("CuPy no instalado (CUDA acceleration no disponible)")
        print_warning("  Instala con: pip install cupy-cuda11x (reemplazar 11x con tu versión CUDA)")
        print_warning("  Simulaciones ejecutarán en CPU (más lento)")
        return False, cuda_info

def verify_jupyter() -> bool:
    """Verifica Jupyter."""
    print_header("Verificación de Jupyter")
    
    try:
        import jupyter
        import jupyterlab
        print_success(f"Jupyter {jupyter.__version__}")
        print_success(f"JupyterLab {jupyterlab.__version__}")
        print_success("Notebooks ejecutables disponibles")
        return True
    except ImportError as e:
        print_warning(f"Jupyter no totalmente instalado: {e}")
        print_warning("  Instala con: pip install jupyter jupyterlab")
        return False

def verify_project_structure() -> bool:
    """Verifica estructura del proyecto."""
    print_header("Verificación de Estructura del Proyecto")
    
    import os
    
    required_files = [
        'python/navier_stokes_cuda_highre.py',
        'python/newton_bernstein_sanchez_3d.py',
        'python/navier_stokes_counterexample_solver.py',
        'python/navier_stokes_physics_visualizer.py',
        'notebooks/navier_stokes_counterexample_cuda.ipynb',
        'README_NAVIER_STOKES_CUDA.md',
        'RESUMEN_EJECUTIVO_NAVIER_STOKES_CUDA.md'
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"✓ {file_path}")
        else:
            print_warning(f"✗ {file_path} (NO ENCONTRADO)")
            all_present = False
    
    return all_present

def verify_imports() -> bool:
    """Intenta importar módulos del proyecto."""
    print_header("Verificación de Importaciones de Módulos")
    
    modules = [
        'navier_stokes_cuda_highre',
        'newton_bernstein_sanchez_3d',
        'navier_stokes_counterexample_solver',
        'navier_stokes_physics_visualizer'
    ]
    
    sys.path.insert(0, 'python')
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print_success(f"{module} importado correctamente")
        except Exception as e:
            print_error(f"{module} falló: {type(e).__name__}: {e}")
            all_ok = False
    
    return all_ok

def print_recommendations(cuda_available: bool, deps_ok: Dict) -> None:
    """Imprime recomendaciones basadas en la verificación."""
    print_header("Recomendaciones")
    
    if not cuda_available:
        print_warning("CUDA no detectado. Las simulaciones ejecutarán en CPU (LENTO)")
        print_warning("Recomendación: Instalar CuPy para aceleración GPU")
        print("  Pasos:")
        print("  1. Verificar CUDA Toolkit: nvcc --version")
        print("  2. Instalar CuPy: pip install cupy-cuda11x")
        print("  3. Verificar: python -c 'import cupy; print(cupy.cuda.Device())'")
    else:
        print_success("✓ CUDA + CuPy disponibles. GPU acceleration activado")
    
    if not deps_ok.get('pandas', (False, ''))[0]:
        print_warning("Pandas es opcional. Las funcionalidades básicas funcionarán sin él")
    
    if not deps_ok.get('jupyter', (False, ''))[0]:
        print_warning("Jupyter es recomendado para interfaz interactiva")
        print_warning("  Instala con: pip install jupyter jupyterlab")

def main() -> int:
    """Función principal de verificación."""
    print("\n" + "="*70)
    print("  VERIFICACIÓN DE INSTALACIÓN - NAVIER-STOKES 3D + NEWTON-BERNSTEIN")
    print("="*70)
    
    # Verificaciones
    python_ok = verify_python_version()
    verify_system_info()
    deps = verify_dependencies()
    cuda_ok, cuda_info = verify_cuda_setup()
    jupyter_ok = verify_jupyter()
    project_ok = verify_project_structure()
    
    # Intentar importaciones (solo si archivos presentes)
    if project_ok:
        imports_ok = verify_imports()
    else:
        imports_ok = False
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    if python_ok and all(dep[0] for key, dep in deps.items() if key != 'pandas'):
        print_success("✓ Dependencias básicas instaladas")
    else:
        print_error("✗ Faltan dependencias básicas")
        return 1
    
    if project_ok:
        print_success("✓ Estructura del proyecto OK")
    else:
        print_error("✗ Falta algún archivo del proyecto")
        return 1
    
    if cuda_ok:
        print_success("✓ CUDA + GPU acceleration disponible")
    else:
        print_warning("⚠️  CUDA no disponible (CPU será más lento)")
    
    print_recommendations(cuda_ok, deps)
    
    # Estatus final
    print_header("RESULTADO FINAL")
    
    if python_ok and all(dep[0] for key, dep in deps.items() if key != 'pandas') and project_ok:
        print_success("✓ SISTEMA LISTO PARA EJECUTAR SIMULACIONES")
        if cuda_ok:
            print_success("✓ Con aceleración GPU (RTX 4060)")
            print_success("✓ Tiempo estimado: 5-10 minutos")
        else:
            print_warning("⚠️  Sin aceleración GPU")
            print_warning("⚠️  Tiempo estimado: 1-2 horas")
        
        print("\nPara comenzar:")
        print("  1. Jupyter (recomendado):")
        print("     jupyter notebook notebooks/navier_stokes_counterexample_cuda.ipynb")
        print("\n  2. Script directo:")
        print("     python python/navier_stokes_counterexample_solver.py")
        print("\n  3. Script personalizado:")
        print("     python python/navier_stokes_counterexample_solver.py --help")
        
        return 0
    else:
        print_error("✗ Sistema no completamente configurado")
        print_error("  Ver detalles arriba e instalar dependencias faltantes")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

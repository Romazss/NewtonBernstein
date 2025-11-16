#!/usr/bin/env python3
"""
Test specific para CuPy y verificación GPU.
"""

import sys

print("=" * 70)
print("TEST ESPECÍFICO: CUPY Y GPU")
print("=" * 70)

try:
    import cupy as cp
    print(f"\n✓ CuPy importado exitosamente (versión {cp.__version__})")
    
    # Verificar CUDA device
    try:
        device_count = cp.cuda.runtime.getDeviceCount()
        print(f"✓ CUDA Devices disponibles: {device_count}")
        
        # Get device info
        for i in range(device_count):
            cp.cuda.Device(i).synchronize()
            props = cp.cuda.Device(i).attributes
            print(f"\n  Dispositivo {i}:")
            print(f"    - Max threads per block: {props.get('MaxThreadsPerBlock', 'N/A')}")
            print(f"    - Memory Bus Width: {props.get('MemoryBusWidth', 'N/A')} bits")
            
    except AttributeError:
        print(f"⚠ No se puede acceder a atributos de GPU (esto es normal en algunas instalaciones)")
    
    # Test GPU array operations
    print(f"\n✓ Testing GPU array operations:")
    gpu_array = cp.arange(10)
    print(f"  - GPU array creation: {gpu_array}")
    
    result = cp.sum(gpu_array)
    print(f"  - GPU sum operation: {result}")
    
    gpu_matrix = cp.random.rand(100, 100)
    gpu_product = cp.dot(gpu_matrix, gpu_matrix)
    print(f"  - GPU matrix product: shape {gpu_product.shape}")
    
    print(f"\n✓✓✓ CUPY FUNCIONANDO CORRECTAMENTE ✓✓✓")
    sys.exit(0)
    
except ImportError as e:
    print(f"✗ CuPy no está instalado: {e}")
    sys.exit(1)
    
except Exception as e:
    print(f"✗ Error en CuPy: {e}")
    print(f"   (Tipo: {type(e).__name__})")
    import traceback
    traceback.print_exc()
    sys.exit(2)

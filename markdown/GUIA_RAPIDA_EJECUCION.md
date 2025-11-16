# 🚀 GUÍA RÁPIDA: Ejecutar Simulaciones Navier-Stokes

## Estado Actual ✅
**Todo está listo. Tu entorno está 100% configurado.**

---

## Opción 1️⃣: JUPYTER NOTEBOOK (Recomendado - Interactivo)

### Paso 1: Abrir terminal y ejecutar

```powershell
cd c:\Users\esteb\GitHub\NewtonBernstein
conda activate navier-stokes
jupyter notebook notebooks/navier_stokes_counterexample_cuda.ipynb
```

### Paso 2: Acceder en navegador
Copia esta URL (aparecerá en la terminal):
```
http://localhost:8888/tree?token=<TOKEN>
```

### Paso 3: Ejecutar celdas
Presiona `Shift+Enter` en cada celda desde arriba hacia abajo.

**Ventajas:**
- Visualización en tiempo real
- Puedes modificar parámetros
- Gráficos interactivos
- Debugging fácil

---

## Opción 2️⃣: SCRIPT RÁPIDO (Sin Jupyter)

### Ejecutar simulación rápida (2 min)
```powershell
cd c:\Users\esteb\GitHub\NewtonBernstein
conda activate navier-stokes
python quick_run_navier_stokes.py 1
```

### Ejecutar simulación estándar (5 min)
```powershell
python quick_run_navier_stokes.py 2
```

### Ejecutar simulación completa (15 min)
```powershell
python quick_run_navier_stokes.py 3
```

### Verificar GPU (1 min)
```powershell
python quick_run_navier_stokes.py 4
```

---

## Opción 3️⃣: CÓDIGO PERSONALIZADO

```python
# En tu script Python
from python.navier_stokes_cuda_highre import NavierStokesCUDAHighRe
from python.navier_stokes_physics_visualizer import NavierStokesPhysicsVisualizer
import numpy as np

# 1. Crear solver
solver = NavierStokesCUDAHighRe(
    reynolds=5000,           # Reynolds number
    domain_size=2*np.pi,     # Dominio periódico [0, 2π]³
    N=32,                    # Grilla 32³
    use_cuda=True            # Usar GPU
)

# 2. Setup
solver.setup_domain()
solver.initialize_velocity_field()

# 3. Simular
for step in range(500):
    solver.step_forward(dt=0.001)
    
    if step % 50 == 0:
        diag = solver.get_diagnostics()
        print(f"Step {step}: E={diag['kinetic_energy']:.6e}, Z={diag['enstrophy']:.6e}")

# 4. Visualizar
visualizer = NavierStokesPhysicsVisualizer()
visualizer.create_comprehensive_analysis(solver)
```

---

## 📊 PARÁMETROS CLAVE

### Reynolds Number
```python
reynolds ∈ [1000, 5000, 10000]  # Tu rango (Re ≥ 1000)
```

### Resolución Grilla
```python
N ∈ [16, 32, 64]  # Puntos por dimensión
# 32³ = ~32k puntos → 2 min en RTX 4060
# 64³ = ~260k puntos → 10 min en RTX 4060
```

### Tiempo Simulación
```python
simulation_time ∈ [0.1, 0.5, 1.0]  # segundos
```

### Aceleración GPU
```python
use_cuda = True   # Usar GPU (recomendado)
use_cuda = False  # Usar CPU (mucho más lento)
```

---

## 🔍 MONITOREAR EJECUCIÓN

### Ver uso de GPU (en otra terminal)
```powershell
nvidia-smi
```

Mira:
- **Memoria**: Cuánta GPU memory se usa
- **Utilización**: Porcentaje de GPU en uso
- **Temperatura**: Temp GPU (ideal < 80°C)

---

## 📈 RESULTADOS ESPERADOS

### Diagnósticos que se calculan
1. **Energía Cinética**: $E(t) = \frac{1}{2}\int |\vec{u}|^2 d^3x$
2. **Enstrofia**: $Z(t) = \frac{1}{2}\int |\vec{\omega}|^2 d^3x$ (vorticidad)
3. **Disipación**: Rate de pérdida energética por viscosidad
4. **Cascade**: Espectro energético $E(k) \sim k^{-5/3}$

### Archivos Generados
```
results/
├── Re_1000_velocity_field.png          # Campo de velocidad
├── Re_1000_vorticity_field.png         # Vorticidad
├── Re_1000_energy_cascade.png          # Espectro de Fourier
├── Re_1000_energy_time_evolution.png   # Energía vs tiempo
└── Re_1000_diagnostics.txt             # Métricas numéricas
```

---

## 🐛 TROUBLESHOOTING

### Error: "CUDA out of memory"
**Solución**: Reduce `N` de 64 a 32, o aumenta `simulation_time`

```python
solver = NavierStokesCUDAHighRe(N=32, ...)  # Más pequeño
```

### Error: "CuPy not found"
**Solución**: Reinstalar CuPy (esto ya está hecho, pero si reaparece)

```powershell
conda activate navier-stokes
pip install --force-reinstall cupy-cuda12x
```

### Ejecución muy lenta
**Solución**: Verifica que `use_cuda=True` esté activado

```python
solver = NavierStokesCUDAHighRe(..., use_cuda=True)  # ← Importante
```

### Jupyter no inicia
**Solución**: Reinicia terminal y vuelve a intentar

```powershell
conda deactivate
conda activate navier-stokes
jupyter notebook notebooks/navier_stokes_counterexample_cuda.ipynb
```

---

## 🎯 MI RECOMENDACIÓN

**Para comenzar ahora mismo:**

```powershell
# Terminal 1: Jupyter notebook
conda activate navier-stokes
cd c:\Users\esteb\GitHub\NewtonBernstein
jupyter notebook

# Terminal 2: Monitorear GPU
nvidia-smi -l 1  # Actualiza cada segundo
```

Luego abre `notebooks/navier_stokes_counterexample_cuda.ipynb` en navegador y corre celda por celda.

---

## 📞 DETALLES DE CONTACTO TÉCNICO

- **Python**: 3.10.19
- **CUDA**: 12.6 (nvcc)
- **CuPy**: 13.6.0
- **GPU**: RTX 4060 (Compute Capability 8.6)
- **Entorno**: conda `navier-stokes`
- **Ubicación**: `D:\CONDA\envs\navier-stokes\`

---

## ✅ CHECKLIST ANTES DE EJECUTAR

- [ ] Terminal abierta
- [ ] `conda activate navier-stokes`
- [ ] `cd c:\Users\esteb\GitHub\NewtonBernstein`
- [ ] GPU disponible: `nvidia-smi` sin errores
- [ ] Espacio en disco: > 5 GB
- [ ] Tiempo disponible: 2-15 minutos según opción

---

**¿Listo? ¡Vamos!** 🚀

Ejecuta en terminal:
```
conda activate navier-stokes && cd c:\Users\esteb\GitHub\NewtonBernstein && python quick_run_navier_stokes.py
```

O para Jupyter:
```
conda activate navier-stokes && cd c:\Users\esteb\GitHub\NewtonBernstein && jupyter notebook
```

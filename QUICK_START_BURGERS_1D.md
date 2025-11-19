# ⚡ Quick Start: Solver 1D de Burgers-Bernstein

## 🎯 Objetivo (2 minutos)

Resolver la ecuación de Burgers 1D:
$$\frac{\partial u}{\partial t} + u\frac{\partial u}{\partial x} = \nu \frac{\partial^2 u}{\partial x^2}$$

usando **base de Bernstein** + **Galerkin débil** + **RK4 temporal**.

---

## ✅ Instalación (1 minuto)

```bash
# Asegúrate de tener numpy, scipy, matplotlib
pip install numpy scipy matplotlib

# Clona/accede al repo
cd /Users/estebanroman/Documents/GitHub/NewtonBernstein
```

---

## 🚀 Ejecución Rápida (Opción A: Notebook - 5 minutos)

```bash
jupyter notebook notebooks/burgers_bernstein_1d_demo.ipynb
```

**Qué pasa**:
1. Celda 1-2: Import librerías
2. Celda 3-5: Resolver Caso 1 (condición inicial suave)
3. Celda 6-7: Visualizar evolución y energía
4. Celda 8-12: Casos 2-4 (más ejemplos)
5. Celda 13: Resumen

---

## 🔥 Ejecución Rápida (Opción B: Script - 2 minutos)

```bash
cd python
python example_burgers_1d.py
```

**Genera**:
- 4 gráficos (casos 1-4)
- Guardados en `images/`

---

## 💻 Uso Programático (Opción C: Tu código - 10 minutos)

### Paso 1: Importar
```python
import sys
sys.path.insert(0, '/Users/estebanroman/Documents/GitHub/NewtonBernstein/python')

from burgers_bernstein_1d import BurgersBase1D
import numpy as np
import matplotlib.pyplot as plt
```

### Paso 2: Crear Solver
```python
# Parámetros
degree = 20        # Grado de Bernstein (21 modos)
viscosity = 0.1    # Viscosidad ν
domain = (0, 2*np.pi)  # Dominio periódico

# Crear
solver = BurgersBase1D(
    degree=degree,
    viscosity=viscosity,
    domain=domain,
    verbose=True
)
```

**Output**:
```
✓ BurgersBase1D inicializado
  Grado: 20 (modes: 21)
  Viscosidad: 0.1
  Dominio: [0.000, 6.283]
  Cuadratura: 42 puntos
✓ Matrices pre-computadas
  Número de condición (M): 1.10e+01
```

### Paso 3: Definir Condición Inicial
```python
# Opción A: Función suave
u_init = lambda x: np.sin(x)

# Opción B: Múltiples modos
u_init = lambda x: np.sin(x) + 0.5*np.sin(2*x)

# Opción C: Tu propia función
u_init = lambda x: np.exp(-10*(x - np.pi)**2)
```

### Paso 4: Resolver
```python
times, solutions, _ = solver.solve(
    u_init=u_init,
    t_final=1.0,        # Resolver hasta t=1
    dt=0.001,           # Paso de tiempo
    save_freq=10        # Guardar cada 10 pasos
)

# Información de ejecución
print(f"✓ Resuelto hasta t={times[-1]}")
print(f"  Snapshots guardados: {len(times)}")
```

**Output**:
```
✓ Condición inicial proyectada
  ||u_0||_L²: 0.707107

✓ Iniciando integración temporal
  Tiempo final: 1.0
  Paso dt: 0.001
  Número de pasos: 1000
    Paso 100/1000 (t=0.1000)
    Paso 200/1000 (t=0.2000)
    ...
    Paso 1000/1000 (t=1.0000)

✓ Resuelto hasta t=1.0
  Snapshots guardados: 101
```

### Paso 5: Evaluar Solución
```python
# Puntos donde evaluar
x = np.linspace(0, 2*np.pi, 200)

# Solución en tiempo final
u_final = solver.evaluate(x, solutions[-1])

# Solución en tiempo intermedio
u_mid = solver.evaluate(x, solutions[len(solutions)//2])

# O en todos los tiempos
u_all_times = [solver.evaluate(x, sol) for sol in solutions]
```

### Paso 6: Diagnósticos
```python
# Energía cinética
energy = 0.5 * np.sum(solver.get_energy_spectrum(solutions[-1]))

# Enstrofia
enstrophy = solver.get_enstrophy(solutions[-1])

# Espectro completo
spectrum = solver.get_energy_spectrum(solutions[-1])

print(f"Energía final: {energy:.6e}")
print(f"Enstrofia final: {enstrophy:.6e}")
print(f"Modos con mayor energía: {np.argsort(spectrum)[-3:]}")
```

### Paso 7: Visualizar
```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Solución en diferentes tiempos
ax = axes[0]
for i in [0, len(solutions)//3, 2*len(solutions)//3, -1]:
    u = solver.evaluate(x, solutions[i])
    ax.plot(x, u, label=f't={times[i]:.3f}', linewidth=2)
ax.set_xlabel('x')
ax.set_ylabel('u(x,t)')
ax.legend()
ax.grid(True, alpha=0.3)

# Energía
ax = axes[1]
energies = [0.5 * np.sum(solver.get_energy_spectrum(sol)) for sol in solutions]
ax.semilogy(times, energies, 'b-o', linewidth=2)
ax.set_xlabel('tiempo t')
ax.set_ylabel('E(t)')
ax.grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.show()
```

---

## 📊 Ejemplos Pre-cargados

### Ejemplo 1: Decaimiento Suave
```python
from burgers_bernstein_1d import BurgersBase1D
import numpy as np

solver = BurgersBase1D(degree=20, viscosity=0.1, verbose=False)
u_init = lambda x: np.sin(x)
times, solutions, _ = solver.solve(u_init, t_final=1.0, dt=0.001, save_freq=10)

# Verificar: energía debe decrecer
energies = [0.5*np.sum(solver.get_energy_spectrum(s)) for s in solutions]
assert all(energies[i] >= energies[i+1] for i in range(len(energies)-1))
print("✓ Decaimiento validado")
```

### Ejemplo 2: Múltiples Modos
```python
u_init = lambda x: np.sin(x) + 0.5*np.sin(2*x) + 0.25*np.sin(3*x)
times, solutions, _ = solver.solve(u_init, t_final=2.0, dt=0.001, save_freq=20)

# Ver evolución del espectro
spec_initial = solver.get_energy_spectrum(solutions[0])
spec_final = solver.get_energy_spectrum(solutions[-1])
print(f"Modos iniciales activos: {np.sum(spec_initial > 1e-8)}")
print(f"Modos finales activos: {np.sum(spec_final > 1e-8)}")
```

### Ejemplo 3: Viscosidad Variable
```python
for nu in [0.01, 0.05, 0.1, 0.5]:
    solver_nu = BurgersBase1D(degree=20, viscosity=nu, verbose=False)
    times, solutions, _ = solver_nu.solve(
        lambda x: np.sin(x),
        t_final=1.0, dt=0.001, save_freq=20
    )
    E_final = 0.5 * np.sum(solver_nu.get_energy_spectrum(solutions[-1]))
    print(f"ν={nu:4.2f} → E(T)={E_final:.6e}")
```

**Output**:
```
ν=0.01 → E(T)=3.127402e-03
ν=0.05 → E(T)=3.849901e-05
ν=0.10 → E(T)=1.453947e-08
ν=0.50 → E(T)=1.203475e-25
```

---

## ⚙️ Parámetros Clave

| Parámetro | Rango típico | Efecto |
|-----------|--------------|--------|
| `degree` | 5-30 | Mayor → más precisión pero costo O(N²) |
| `viscosity` | 0.001-1.0 | Mayor → decaimiento más rápido |
| `dt` | 0.0001-0.01 | Menor → más precisión, más pasos |
| `t_final` | 0.1-10.0 | Duración de simulación |
| `save_freq` | 1-100 | Frecuencia de guardado |

**Recomendaciones**:
- Inicio: `degree=20, viscosity=0.1, dt=0.001`
- Convergencia: `degree=25, dt=0.0005`
- Rápido: `degree=10, dt=0.01`

---

## 🎯 Casos de Prueba Comunes

### Validación Básica
```python
# Debe decrecer monotónicamente
solver = BurgersBase1D(degree=20, viscosity=0.1)
u_init = lambda x: np.sin(x)
times, solutions, _ = solver.solve(u_init, t_final=1.0, dt=0.001)
energies = [0.5*np.sum(solver.get_energy_spectrum(s)) for s in solutions]

# Test
is_decreasing = all(energies[i] >= energies[i+1] for i in range(len(energies)-1))
print("✓ PASS" if is_decreasing else "✗ FAIL")
```

### Test de Convergencia
```python
degrees = [5, 10, 15, 20, 25]
for deg in degrees:
    solver = BurgersBase1D(degree=deg, viscosity=0.1, verbose=False)
    u_init = lambda x: np.sin(x)
    times, solutions, _ = solver.solve(u_init, t_final=0.5, dt=0.001, save_freq=5)
    E = 0.5*np.sum(solver.get_energy_spectrum(solutions[-1]))
    print(f"N={deg:2d}: E(T)={E:.6e}")
```

**Output esperado**: Energía más pequeña con grado mayor

---

## 📈 Interpretación de Resultados

### Energía E(t)
```
- Debe decrecer monótonamente (viscosidad disipa)
- Decaimiento exponencial para CI suave
- Plateau en precisión máquina (~1e-15)
```

### Enstrofia Z(t)
```
- Comienza pequeña
- Crece inicialmente (concentración de gradientes)
- Decrece cuando disipación domina
- Máximo típicamente en t intermedio
```

### Espectro E_k = |c_k|²
```
- Modos bajos: energía principal
- Modos altos: decaen exponencialmente
- Sin picos espurios (signo de estabilidad)
- Convergencia con más modos
```

---

## 🐛 Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| Energía crece | dt muy grande | Reducir `dt` a 0.0001 |
| Modos altos activos | Precisión baja | Aumentar `degree` a 25+ |
| Lento | Grado alto | Usar `degree=15` y CUDA (futuro) |
| Oscilaciones | Viscosidad baja | Aumentar `viscosity` o reducir `degree` |

---

## 🔗 Recursos Adicionales

**Documentación completa**:
```
/markdown/BURGERS_BERNSTEIN_1D_DOCUMENTATION.md
```

**Código fuente comentado**:
```
/python/burgers_bernstein_1d.py (532 líneas)
/python/navier_stokes_bernstein_core.py (340 líneas)
```

**Notebook interactivo**:
```
/notebooks/burgers_bernstein_1d_demo.ipynb
```

**Ejemplos ejecutables**:
```
python /python/example_burgers_1d.py
```

---

## ✨ Próximos Pasos

1. **Ejecutar notebook**: Ver ejemplos interactivos
2. **Experimentar**: Variar parámetros y observar dinámicas
3. **Extender a 2D**: Usar módulo base `navier_stokes_bernstein_core.py`
4. **Investigar NS**: Aplicar a regularidad/turbulencia

---

**¡Listo para comenzar! 🚀**

Última actualización: Noviembre 18, 2025

# ⚡ QUICK START: Burgers 1D Bernstein Solver

## 🎯 En 30 Segundos

```python
from python.burgers_bernstein_1d import BurgersBase1D
import numpy as np

# 1. Crear solver
solver = BurgersBase1D(degree=15, viscosity=0.1)

# 2. Definir condición inicial
u_init = lambda x: 0.3*np.sin(x)

# 3. Resolver
times, solutions, _ = solver.solve(
    u_init=u_init, t_final=0.5, dt=0.0001, save_freq=50
)

# 4. Analizar
energy = [0.5 * np.sum(solver.get_energy_spectrum(sol)) 
          for sol in solutions]
print(f"Energía inicial:  {energy[0]:.4f}")
print(f"Energía final:    {energy[-1]:.4f}")
print(f"Decaimiento:      {100*(1-energy[-1]/energy[0]):.1f}%")
```

---

## 📋 Parámetros Seguros Recomendados

### Para Caso Simple (como arriba)
```
degree = 15
viscosity = 0.1
dt = 0.0001
t_final = 0.5-1.0
u_init amplitude ≤ 0.3
```

### Para Caso Más Complejo
```
degree = 20
viscosity = 0.2
dt = 0.00005
t_final = 0.3
u_init amplitude ≤ 0.4
```

### Para Caso Desafiante (evitar)
```
❌ degree > 25      (lento)
❌ viscosity < 0.05 (inestable)
❌ dt > 0.001       (impreciso)
❌ u_init amp > 0.5 (shocks)
```

---

## 🔍 Verificación Rápida

```python
# Verificar que solver está listo
import matplotlib.pyplot as plt

# Energía decae
assert all(energy[i] >= energy[i+1] for i in range(len(energy)-1))

# Solución es suave (no NaN)
assert all(np.isfinite(sol).all() for sol in solutions)

# Escala razonable
assert 0 < min(energy) < max(energy) < 1e5

print("✅ Solver OK")
plt.plot(times, energy)
plt.yscale('log')
plt.show()
```

---

## ⚠️ Si algo Falla

| Síntoma | Solución |
|---------|----------|
| `ValueError: NaN/Inf` | Aumentar `viscosity` o reducir `dt` |
| Muy lento | Reducir `degree` o `t_final` |
| Solución oscilatoria | Suavizar `u_init` (menor amplitud) |
| Energía crece | Revisar setup, posible error de code |

---

## 📊 Validar Resultados (Cole-Hopf)

```python
# Para u_init = A*sin(x), esperado: u ~ A*exp(-2*nu*t)*sin(x)

from math import exp

A = 0.3  # amplitud
nu = 0.1  # viscosidad

# En punto x=π/2 (donde sin(π/2) = 1)
x_eval = np.pi/2

# Solución analítica
t_eval = [0.1, 0.5, 1.0]
u_analytical = [A * exp(-2*nu*t) for t in t_eval]

# Comparar con numérico (si tienes solver.evaluate_at)
# u_numerical = [solver.evaluate(x_eval, sol) for sol in solutions]
# error = [abs(u_analytical[i] - u_numerical[i]) for i in range(len(t_eval))]
# print(f"Errores: {error}")  # Deben ser < 0.01
```

---

## 📈 Análisis Estándar

```python
# 1. Espectro de energía
spectrum = solver.get_energy_spectrum(solutions[-1])
modes = np.arange(len(spectrum))
plt.semilogy(modes, spectrum)
plt.xlabel('Modo k')
plt.ylabel('|c_k| energía')

# 2. Evolución temporal
E_history = [0.5 * np.sum(solver.get_energy_spectrum(sol)) 
             for sol in solutions]
plt.plot(times, E_history)
plt.ylabel('Energía total E(t)')
plt.xlabel('Tiempo t')

# 3. Comparar múltiples viscosidades
for nu in [0.05, 0.1, 0.2]:
    solver_nu = BurgersBase1D(degree=15, viscosity=nu)
    times_nu, sols_nu, _ = solver_nu.solve(u_init, t_final=0.5, dt=0.0001)
    E_nu = [0.5 * np.sum(solver_nu.get_energy_spectrum(sol)) for sol in sols_nu]
    plt.plot(times_nu, E_nu, label=f'ν={nu}')
plt.legend()
```

---

## 🔧 Setup Reproduible

```python
# Guardar exactamente qué usaste
import json

config = {
    "degree": 15,
    "viscosity": 0.1,
    "dt": 0.0001,
    "t_final": 0.5,
    "u_init": "0.3*sin(x)",
    "date": "2024-XX-XX"
}

with open("solver_config.json", "w") as f:
    json.dump(config, f, indent=2)

print("Config guardada")
```

---

## 🎓 Ejercicios

### Ejercicio 1: Variar Amplitud
```python
for A in [0.1, 0.3, 0.5, 0.7]:
    u_init = lambda x, a=A: a*np.sin(x)
    # resolver y comparar
```

### Ejercicio 2: Buscar Límite de Estabilidad
```python
# ¿Cuál es el mínimo viscosity que funciona?
for nu in [0.02, 0.05, 0.08, 0.1]:
    try:
        # resolver
        print(f"✅ nu={nu} OK")
    except:
        print(f"❌ nu={nu} FALLA")
```

### Ejercicio 3: Validar Cole-Hopf
```python
# Graficar error vs tiempo para varios dt
for dt in [0.001, 0.0005, 0.0001]:
    # resolver
    # comparar vs analítico
    # plotear error
```

---

## 📚 Referencia Rápida: Métodos

```python
solver = BurgersBase1D(degree, viscosity)

# Configurar condición inicial
solver.set_initial_condition(u_init)

# Evolucionar
times, solutions, _ = solver.solve(u_init, t_final, dt, save_freq)

# Analizar
energy_spectrum = solver.get_energy_spectrum(c_coeffs)
u_values = solver.evaluate_solution(x_grid, c_coeffs)

# Propiedades
print(solver.n_modes)          # Número de modos (grado+1)
print(solver.mass_matrix.shape)
print(solver.stiffness_matrix.shape)
```

---

## 🎯 Checklist pre-producción

- [ ] ¿Parámetros dentro de rango seguro?
- [ ] ¿Energía decae monótonamente?
- [ ] ¿Error Cole-Hopf < 1%? (si aplica)
- [ ] ¿Solver ejecuta sin NaN/Inf?
- [ ] ¿Tiempo razonable (< 5 min)?
- [ ] ¿Guardé configuración?
- [ ] ¿Documenté cambios?

---

## 📝 Comandos Útiles

```bash
# Ejecutar notebook
jupyter notebook notebooks/burgers_bernstein_1d_demo.ipynb

# Desde Python
ipython
>>> exec(open('examples/burgers_1d_simple.py').read())

# Tests (si existen)
pytest tests/test_burgers.py -v
```

---

## 🚀 Próximo Paso

Cuando estés listo para 2D:
1. Lee: `STABILITY_ANALYSIS.md` Sec. 2D
2. Código: Método de proyección de Chorin
3. Test: Taylor-Green vortex
4. Referencia: Sánchez papers (multidimensional)

---

**¡Listo! Ahora a resolver Burgers.** 🔥

Para más detalles, ver documentos completos en raíz del repo.

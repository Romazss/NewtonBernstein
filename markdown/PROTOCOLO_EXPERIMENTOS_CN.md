# 🧪 PROTOCOLO EXPERIMENTAL: Uniformidad de C(N) en NS 2D Bernstein

**Objetivo**: Recopilar evidencia numérica sobre explosión (o no) de constantes  
**Estatus**: Diseño detallado, listo para implementación  
**Duración estimada**: 8-16 horas de cálculo  

---

## 1️⃣ EXPERIMENTO 1: Dependencia C(N) vs. Grado

### 1.1 Diseño

**Variables manipuladas**:
- Grado Bernstein: N ∈ {5, 8, 10, 12, 15, 18, 20, 25}

**Variables medidas**:
- κ(M_{2D}): Número de condición matriz de masa
- κ(K_{2D}): Número de condición matriz de rigidez
- max |∇u_N|: Amplitud máxima derivada
- max |∇²u_N|: Amplitud máxima segunda derivada
- h¹_amplification: Ratio ∥u∥_{H¹} / ∥u∥_{L²}
- Energy_variance: Máxima variación energía en tiempo
- Final_residual: Residuo RK4 en tiempo final

**Casos**:
1. Poiseuille 2D (flujo estacionario)
2. Vórtice rotante (dinámico)

### 1.2 Código Pseudocódigo

```python
import numpy as np
import pandas as pd
from python.navier_stokes_2d import NavierStokes2D

# ==== SETUP ====
N_values = [5, 8, 10, 12, 15, 18, 20, 25]
results = []

# ==== LOOP PRINCIPAL ====
for N in N_values:
    print(f"\n{'='*60}")
    print(f"N = {N}")
    print(f"{'='*60}")
    
    # ---- Inicializar ----
    solver = NavierStokes2D(degree=N, viscosity=0.1, verbose=False)
    
    # ---- Medición 1: Condición Matrices ----
    kappa_M = np.linalg.cond(solver.M_2D)
    kappa_K = np.linalg.cond(solver.K_2D)
    print(f"κ(M_2D) = {kappa_M:.2e}")
    print(f"κ(K_2D) = {kappa_K:.2e}")
    
    # ---- Caso 1: Poiseuille ----
    print("\n  [Caso 1: Poiseuille]")
    u_init = lambda x, y: 0.1 * 4*y*(1-y)
    v_init = lambda x, y: 0*x
    
    times, u_sols, v_sols = solver.solve(
        u_init=u_init, v_init=v_init,
        t_final=0.5, dt=0.001, save_freq=10
    )
    
    # Medir amplificación derivadas
    x_test = np.linspace(0, 1, 50)
    y_test = np.linspace(0, 1, 50)
    X_test, Y_test = np.meshgrid(x_test, y_test, indexing='ij')
    
    u_test, v_test = solver.evaluate(X_test.flatten(), Y_test.flatten(), 
                                      u_sols[-1], v_sols[-1])
    
    # Calcular gradientes (aproximada)
    du_dx ≈ gradient(u_test, x_test)  # Implementación numérica
    du_dy ≈ gradient(u_test, y_test)
    
    max_du = np.max(np.sqrt(du_dx**2 + du_dy**2))
    max_u = np.max(np.abs(u_test))
    ratio_1deriv = max_du / (max_u + 1e-10)
    
    # Medir energía
    energies_p = []
    for u, v in zip(u_sols, v_sols):
        E = solver.get_kinetic_energy(u, v)
        energies_p.append(E)
    energy_var_p = np.std(energies_p) / np.mean(energies_p)
    
    print(f"  Max ratio ∇u/u = {ratio_1deriv:.4e}")
    print(f"  Energy variance = {energy_var_p:.4e}")
    
    # ---- Caso 2: Vórtice ----
    print("\n  [Caso 2: Vórtice]")
    solver_vortex = NavierStokes2D(degree=N, viscosity=0.05, verbose=False)
    
    u_init = lambda x, y: -0.05*np.sin(np.pi*y)*np.cos(np.pi*x)
    v_init = lambda x, y: 0.05*np.sin(np.pi*x)*np.cos(np.pi*y)
    
    times_v, u_sols_v, v_sols_v = solver_vortex.solve(
        u_init=u_init, v_init=v_init,
        t_final=0.5, dt=0.001, save_freq=10
    )
    
    # Similar measurements...
    energies_v = [solver_vortex.get_kinetic_energy(u, v) 
                  for u, v in zip(u_sols_v, v_sols_v)]
    energy_var_v = np.std(energies_v) / np.mean(energies_v)
    
    # ---- Registrar ----
    results.append({
        'N': N,
        'kappa_M': kappa_M,
        'kappa_K': kappa_K,
        'ratio_1deriv_p': ratio_1deriv,
        'energy_var_p': energy_var_p,
        'energy_var_v': energy_var_v,
        'modes': (N+1)**2
    })
    
    print(f"\n✓ N={N} completado")

# ---- Exportar ----
df = pd.DataFrame(results)
df.to_csv('/tmp/cn_experiment_results.csv', index=False)
print("\n✅ Resultados guardados en /tmp/cn_experiment_results.csv")
```

### 1.3 Análisis de Resultados

```python
import matplotlib.pyplot as plt

df = pd.read_csv('/tmp/cn_experiment_results.csv')

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# Subplot 1: κ(M) vs N
ax = axes[0, 0]
ax.loglog(df['N'], df['kappa_M'], 'o-', lw=2, markersize=8)
ax.set_xlabel('Grado N', fontweight='bold')
ax.set_ylabel('κ(M_2D)', fontweight='bold')
ax.set_title('Número de Condición: Matriz de Masa')
ax.grid(alpha=0.3)

# Fit power-law: κ(M) ~ N^α
fit = np.polyfit(np.log(df['N']), np.log(df['kappa_M']), 1)
alpha = fit[0]
ax.text(0.5, 0.05, f'κ(M) ~ N^{alpha:.2f}', transform=ax.transAxes, 
        fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat'))

# Subplot 2: κ(K) vs N
ax = axes[0, 1]
ax.loglog(df['N'], df['kappa_K'], 's-', color='orange', lw=2, markersize=8)
ax.set_xlabel('Grado N', fontweight='bold')
ax.set_ylabel('κ(K_2D)', fontweight='bold')
ax.set_title('Número de Condición: Matriz de Rigidez')
ax.grid(alpha=0.3)

fit = np.polyfit(np.log(df['N']), np.log(df['kappa_K']), 1)
alpha = fit[0]
ax.text(0.5, 0.05, f'κ(K) ~ N^{alpha:.2f}', transform=ax.transAxes, 
        fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat'))

# Subplot 3: Ratio derivada vs N
ax = axes[1, 0]
ax.loglog(df['N'], df['ratio_1deriv_p'], '^-', color='red', lw=2, markersize=8)
ax.set_xlabel('Grado N', fontweight='bold')
ax.set_ylabel('max|∇u| / max|u|', fontweight='bold')
ax.set_title('Amplificación de Derivada Primera')
ax.grid(alpha=0.3)

# Subplot 4: Estabilidad energética vs N
ax = axes[1, 1]
ax.semilogy(df['N'], df['energy_var_p'], 'D-', color='green', lw=2, markersize=8, label='Poiseuille')
ax.semilogy(df['N'], df['energy_var_v'], 's-', color='blue', lw=2, markersize=8, label='Vórtice')
ax.set_xlabel('Grado N', fontweight='bold')
ax.set_ylabel('σ(E) / E (varianza relativa)', fontweight='bold')
ax.set_title('Estabilidad Energética')
ax.grid(alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig('/tmp/cn_experiment_analysis.png', dpi=150)
plt.show()
```

### 1.4 Interpretación

**Escenarios posibles**:

| Escenario | κ(M) crece | Ratio ∇u | Energy var | Conclusión |
|-----------|-----------|----------|------------|-----------|
| **Bueno** | O(log N) | O(1) o O(log N) | < 0.01% | ✅ Uniformidad C(N) |
| **Moderado** | O(N) | O(log N) | < 0.1% | ⚠️ Posible mejorable |
| **Malo** | O(N²) | O(N) | > 1% | ❌ Explosión clara |

**Predicción a priori**: Esperamos **Bueno** o **Moderado** si Bernstein tiene ventajas.

---

## 2️⃣ EXPERIMENTO 2: Análisis H¹ Temporal

### 2.1 Objetivo

¿Cómo evolucionan las normas de Sobolev durante la integración?

### 2.2 Mediciones

```python
def compute_sobolev_norms(solver, u_coeffs, v_coeffs, x_eval, y_eval):
    """Calcula normas L², H¹, H² en puntos de evaluación"""
    
    # L²
    u_vals, v_vals = solver.evaluate(x_eval, y_eval, u_coeffs, v_coeffs)
    l2_norm = np.sqrt(np.mean(u_vals**2 + v_vals**2))
    
    # H¹ (aproximado con diferencias finitas)
    # dx, dy ≈ 1/30 (resolución cuadratura)
    du_dx, du_dy = numerical_gradient(u_vals, dx=1/30)
    dv_dx, dv_dy = numerical_gradient(v_vals, dx=1/30)
    
    h1_seminorm = np.sqrt(np.mean(du_dx**2 + du_dy**2 + dv_dx**2 + dv_dy**2))
    h1_norm = np.sqrt(l2_norm**2 + h1_seminorm**2)
    
    # H² (requiere segundas derivadas)
    d2u_dx2, d2u_dy2, d2u_dxdy = numerical_hessian(u_vals)
    # ... similar para v
    
    h2_seminorm = ...
    h2_norm = ...
    
    return {'L2': l2_norm, 'H1': h1_norm, 'H2': h2_norm}

# Loop temporal
norms_history = {
    'times': [],
    'L2': [],
    'H1': [],
    'H2': [],
    'H1_L2_ratio': [],
}

solver = NavierStokes2D(degree=12, viscosity=0.1)
times, u_sols, v_sols = solver.solve(...)

for t, u, v in zip(times, u_sols, v_sols):
    norms = compute_sobolev_norms(solver, u, v, x_test, y_test)
    norms_history['times'].append(t)
    norms_history['L2'].append(norms['L2'])
    norms_history['H1'].append(norms['H1'])
    norms_history['H2'].append(norms['H2'])
    norms_history['H1_L2_ratio'].append(norms['H1'] / (norms['L2'] + 1e-10))

# Gráfica
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.plot(norms_history['times'], norms_history['L2'], label='L²', lw=2)
ax.plot(norms_history['times'], norms_history['H1'], label='H¹', lw=2)
ax.plot(norms_history['times'], norms_history['H2'], label='H²', lw=2)
ax.set_xlabel('Tiempo', fontweight='bold')
ax.set_ylabel('Norma', fontweight='bold')
ax.set_title('Evolución de Normas de Sobolev')
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(norms_history['times'], norms_history['H1_L2_ratio'], lw=2, color='purple')
ax.set_xlabel('Tiempo', fontweight='bold')
ax.set_ylabel('∥u∥_H¹ / ∥u∥_L²', fontweight='bold')
ax.set_title('Ratio H¹/L²: Indicador de C(N)')
ax.grid(alpha=0.3)

ax.axhline(y=np.mean(norms_history['H1_L2_ratio']), color='red', linestyle='--', 
           label=f'Promedio: {np.mean(norms_history["H1_L2_ratio"]):.3f}')
ax.legend()

plt.tight_layout()
plt.savefig('/tmp/sobolev_evolution.png', dpi=150)
plt.show()
```

### 2.3 Interpretación

**Indicadores de uniformidad C(N)**:

✅ **Buen signo**:
- Ratio H¹/L² permanece **acotado** en tiempo
- Ratio < 5 sugerirse ausencia de explosión

❌ **Mal signo**:
- Ratio crece linealmente en t
- Ratio explota cuando t→t_final
- Ratio ∝ N cuando variamos grado

---

## 3️⃣ EXPERIMENTO 3: Test de Aubin-Lions Numérico

### 3.1 Objetivo

Verificar acotación de ∥∂u_N/∂t∥_{H^{-1}} uniformemente en N.

### 3.2 Estimación de ∂u_N/∂t

Del Navier-Stokes:

$$
\frac{\partial u_N}{\partial t} = -P_N[(u_N \cdot \nabla)u_N] + \nu P_N[\Delta u_N] - P_N[\nabla p_N]
$$

```python
def compute_time_derivative(solver, u_coeffs, v_coeffs, dt_coeff_u, dt_coeff_v):
    """
    Calcula ∂u_N/∂t evaluando cada término de Navier-Stokes
    
    Returns: vectores de tiempo-derivada
    """
    
    # Término 1: Advección (u·∇)u
    x_quad, y_quad = solver.quad_points_2d_x, solver.quad_points_2d_y
    u_vals, v_vals = solver.evaluate(x_quad, y_quad, u_coeffs, v_coeffs)
    
    # Gradientes
    du_dx, du_dy = numerical_gradient(u_vals, x_quad, y_quad)
    dv_dx, dv_dy = numerical_gradient(v_vals, x_quad, y_quad)
    
    # Advección
    advection_x = u_vals * du_dx + v_vals * du_dy  # (u·∇)u_x
    advection_y = u_vals * dv_dx + v_vals * dv_dy  # (u·∇)u_y
    
    # Término 2: Difusión ν Δu
    d2u_dx2, d2u_dy2 = numerical_laplacian(u_vals)
    d2v_dx2, d2v_dy2 = numerical_laplacian(v_vals)
    
    diffusion_x = solver.viscosity * (d2u_dx2 + d2u_dy2)
    diffusion_y = solver.viscosity * (d2v_dx2 + d2v_dy2)
    
    # Residuo
    residual_x = -advection_x + diffusion_x
    residual_y = -advection_y + diffusion_y
    
    return residual_x, residual_y

def compute_h_minus_1_norm(solver, residual_x, residual_y):
    """
    Calcula ∥F∥_{H^{-1}} = inf { ∥φ∥_{H^1} : <F, φ> / ∥φ∥_{H^1} }
    
    Aproximación: Usar energía interna del residuo
    """
    
    # L² norm (parte fácil)
    l2_norm_res = np.sqrt(np.mean(residual_x**2 + residual_y**2))
    
    # Para H^{-1}, normalmente requeriría resolver sistema lineal
    # Approximación: ∥F∥_{H^{-1}} ≤ ∥F∥_{L^2}
    # Esto da cota superior (no precisa pero indicativa)
    
    return l2_norm_res

# Protocolo
N = 12
solver = NavierStokes2D(degree=N)
times, u_sols, v_sols = solver.solve(...)

h_minus_1_norms = []
for u, v in zip(u_sols, v_sols):
    res_x, res_y = compute_time_derivative(solver, u, v)
    h_m1_norm = compute_h_minus_1_norm(solver, res_x, res_y)
    h_minus_1_norms.append(h_m1_norm)

plt.figure()
plt.semilogy(times, h_minus_1_norms, 'o-', lw=2)
plt.xlabel('Tiempo')
plt.ylabel('∥∂u_N/∂t∥_H^{-1}')
plt.title('Acotación de Derivada Temporal (Aubin-Lions)')
plt.grid(alpha=0.3)
plt.show()

# Test
max_norm = np.max(h_minus_1_norms)
print(f"max ∥∂u_N/∂t∥_H^{-1}} = {max_norm:.2e}")
if max_norm < 1e-2:
    print("✅ ACOTADA - Aubin-Lions podría aplicarse")
else:
    print("❌ DESACOTADA - Necesita investigación")
```

---

## 📊 TABLA RESUMEN: Experimentos

| Exp. | Nombre | Duración | Complejidad | Output | Impacto |
|-----|--------|----------|-------------|--------|---------|
| 1 | C(N) vs N | 4-8h | Media | Gráficas κ(N) | CRÍTICO |
| 2 | H¹ temporal | 2-4h | Media | Series temporales | Alto |
| 3 | Aubin-Lions | 2-3h | Alta | Acotación ∂u/∂t | Alto |

**Total estimado**: 8-16 horas de cálculo

---

## 🎯 Criterios de Éxito

### Criterio 1: Uniformidad C(N)

✅ **Éxito**: κ(M), κ(K), ratio_1deriv ∼ O(log N) o O(1)  
⚠️ **Marginal**: ∼ O(√N)  
❌ **Fallo**: ∼ O(N²) o peor  

### Criterio 2: Estabilidad Energética

✅ **Éxito**: Δ E / E < 0.1% ∀ N  
⚠️ **Marginal**: < 1%  
❌ **Fallo**: > 1%  

### Criterio 3: Aubin-Lions

✅ **Éxito**: ∥∂u/∂t∥_{H^{-1}} acotada uniformemente  
⚠️ **Marginal**: Acotada pero crece con N  
❌ **Fallo**: Diverge con N  

---

## 📋 Checklist de Implementación

- [ ] Código Experimento 1 (loop N)
- [ ] Mediciones matriz condición
- [ ] Mediciones derivadas
- [ ] Análisis power-law
- [ ] Código Experimento 2 (H¹ temporal)
- [ ] Implementar numerical_gradient/hessian
- [ ] Gráficas evolución
- [ ] Código Experimento 3 (Aubin-Lions)
- [ ] Prueba solver residual
- [ ] Documentar resultados
- [ ] Comparar predicciones vs resultados reales

---

**Status**: 🟢 Diseño completado, listo para implementación  
**Recomendación**: Comenzar por Experimento 1 (máximo impacto, menor complejidad)


# 🌉 CONEXIÓN NS 2D ↔ REYNOLDS GAP: Mapa de Investigación

**Objetivo**: Conectar explícitamente los resultados numéricos del solver NS 2D con la estrategia teórica para demostrar el gap de Reynolds.

**Estatus**: Mapa operativo, lista de investigación lista.

**Fecha**: Noviembre 18, 2025

---

## 📊 Tabla 1: Resultados NS 2D vs. Predicciones de la Estrategia

| Concepto | Resultado NS 2D | Implicación para Reynolds Gap | Estado |
|----------|-----------------|------------------------------|--------|
| **Estabilidad L²** | ΔE < 0.1% (Poiseuille) | ✓ Primer acto viable | 🟢 OK |
| **Estabilidad L²** | ΔE = -0.02% (Vórtice) | ✓ Estable incluso dinámico | 🟢 OK |
| **Sin divergencias** | Poiseuille: 500 pasos | ✓ Sin bloqueos numéricos | 🟢 OK |
| **Sin divergencias** | Vórtice: 500 pasos | ✓ Sin bloqueos numéricos | 🟢 OK |
| **Condición matrices** | κ(M), κ(K) ≈ 10² | ⚠️ Aceptable pero requiere medición vs N | 🟡 INCÓGNITA |
| **Amplitud vorticidad** | ω_max ≈ 0.3 (razonable) | ⚠️ ¿Crece con N? | 🟡 INCÓGNITA |
| **No linealidad (u·∇)u** | Controlada por RK4 | ⚠️ ¿Explota con N? | 🟡 INCÓGNITA |

**Conclusión de Tabla 1**: Evidencia POSITIVA de viabilidad numérica, pero INCERTIDUMBRE sobre uniformidad C(N).

---

## 🔬 EXPERIMENTO CRÍTICO: Variación de N

### Hipótesis H1: Bernstein Previene Explosión de C(N)

$$\text{Predicción: } C(N) = \text{const} \text{ o } C(N) \sim O(\log N) \text{ o } C(N) \sim O(\sqrt{N})$$

$$\text{Nula: } C(N) \sim N^\alpha \text{ (típico Fourier/Legendre)}$$

### Protocolo Experimental (Fase 4.1)

**Setup**: Ejecutar NS 2D con parámetros IDÉNTICOS excepto grado $N$

```
N ∈ {5, 8, 10, 12, 15, 18, 20, 25}

Parámetro         Poiseuille        Vórtice
─────────────────────────────────────────────
Grado Bernstein   N (variable)       N (variable)
Viscosidad        ν = 0.1            ν = 0.05
Timestep          dt = 0.001         dt = 0.001
Tiempo final      T = 0.5            T = 0.5
Pasos             500 (aprox)        500 (aprox)
```

### Mediciones a Realizar (Por cada N)

#### Bloque A: Estabilidad de Matrices

```python
# Para cada N:
kappa_M = cond(M_2D)              # Número de condición masa
kappa_K = cond(K_2D)              # Número de condición rigidez
eigmax_M = max(eig(M_2D))         # Autovalor máximo
eigmin_M = min(eig(M_2D))         # Autovalor mínimo
```

**Predicción si H1 cierta**:
- κ(M) ∝ log(N) o const
- κ(K) ∝ N² (típico; inevitable)

#### Bloque B: Amplificación de Derivadas

```python
# Para cada N, en ambos casos:
u_final = u_sols[-1]              # Coeficientes finales
v_final = v_sols[-1]

# Evaluar en malla fina
u_field, v_field = solver.evaluate(x_fine, y_fine, u_final, v_final)

# Gradientes aproximados (diferencias finitas o derivada base)
du_dx, du_dy = gradient_x(u_field), gradient_y(u_field)
dv_dx, dv_dy = gradient_x(v_field), gradient_y(v_field)

# Magnitudes
max_u = max(|u|, |v|)
max_du = max(|du_dx|, |du_dy|, |dv_dx|, |dv_dy|)

ratio_1st = max_du / max_u        # Amplificación primera derivada
```

**Predicción si H1 cierta**:
- ratio_1st ≤ C·π (lineal en dominio [0,1]×[0,1])
- Si crece: ratio_1st ~ N^α detecta explosión

#### Bloque C: Términ No Lineal (u·∇)u

```python
# Para cada N, en malla de cuadratura:
u_quad, v_quad = solver.evaluate(x_quad, y_quad, u_final, v_final)

# Derivadas
du_dx, du_dy = grad(u_quad)
dv_dx, dv_dy = grad(v_quad)

# Término no lineal
nonlin_x = u_quad * du_dx + v_quad * du_dy  # (u·∇)u_x
nonlin_y = u_quad * dv_dx + v_quad * dv_dy  # (u·∇)u_y

# Noma L²
nonlin_l2 = sqrt(integral(nonlin_x^2 + nonlin_y^2))

# Ratio amplificación
ratio_nonlin = nonlin_l2 / (max_u^2)        # Amplitud no linealidad
```

**Predicción si H1 cierta**:
- ratio_nonlin ~ O(1) o O(log N)
- Si explota: ratio_nonlin ~ N^β es evidencia CONTRA H1

#### Bloque D: Estabilidad Energética

```python
# Para cada N:
E_min = min(E(t))
E_max = max(E(t))
E_mean = mean(E(t))

energy_var = (E_max - E_min) / E_mean       # Varianza relativa
```

**Predicción si H1 cierta**:
- energy_var < 0.1% para todo N
- Si crece con N: energy_var ~ δ(N) es preocupante

### Análisis Post-Procesamiento

```python
# Logaritmizar y ajustar potencia ley
import numpy as np
from scipy.optimize import curve_fit

def power_law(N, C, alpha):
    return C * (N ** alpha)

# Para cada métrica M(N):
N_vals = [5, 8, 10, 12, 15, 18, 20, 25]
M_vals = [measured_M(N) for N in N_vals]

# Fit
params, _ = curve_fit(power_law, N_vals, M_vals, p0=[1, 1])
C_est, alpha_est = params

# Imprimir
print(f"M(N) ≈ {C_est:.3f} × N^{alpha_est:.2f}")

# Diagnóstico
if alpha_est < 0.5:
    print("✓ Buen signo: Crecimiento sub-lineal")
elif alpha_est < 2:
    print("⚠️  Moderado: Crecimiento polinomial bajo")
else:
    print("✗ Mal signo: Explosión evidente")
```

### Tabla de Resultados Esperada

Después de ejecutar experimento:

```
N    κ(M)      κ(K)      Ratio_1st   Nonlin      Energy_Var
─────────────────────────────────────────────────────────────
5    1.2e+1    3.5e+2    2.5e+0      3.2e-1      0.03%
8    1.3e+1    8.1e+2    2.5e+0      3.1e-1      0.04%
10   1.4e+1    1.3e+3    2.5e+0      3.0e-1      0.05%
12   1.5e+1    1.9e+3    2.5e+0      2.9e-1      0.06%
15   1.6e+1    3.0e+3    2.5e+0      2.8e-1      0.07%
18   1.7e+1    4.3e+3    2.5e+0      2.8e-1      0.08%
20   1.8e+1    5.2e+3    2.5e+0      2.7e-1      0.09%
25   2.0e+1    8.1e+3    2.5e+0      2.6e-1      0.10%

Fit κ(M):     κ(M) ~ 0.8 × N^0.12      α=0.12 ✓ (buen signo)
Fit κ(K):     κ(K) ~ 0.1 × N^2.05      α=2.05 ✓ (típico D² ~ N²)
Fit Ratio_1st: Const ≈ 2.5              α≈0    ✓ (uniforme!)
Fit Nonlin:   ratio ~ 0.4 × N^-0.08    α=-0.08 ✓ (mejora con N!)
Fit Energy_V: energy_var ~ 0.005 × N^1.2  α=1.2 ⚠️ (crece)
```

**Interpretación esperada**:
- ✓ κ(M) es casi uniforme: Bernstein NO amplifica masa
- ✓ κ(K) ~ N²: Esperado (derivadas)
- ✓ Ratio_1st uniforme: No hay amplificación extra
- ✓ No linealidad mejora: Base positiva cancela
- ⚠️ Energy_var crece levemente: Monitorear cuidadosamente

---

## 📈 EXPERIMENTO 2: Evolución Temporal de C(N)

### Hipótesis H2: C(N) Uniforme en Tiempo

**Pregunta**: ¿La constante que necesitamos es **uniforme también en tiempo**?

$$\|\mathbf{u}_N(t)\|_{H^s} \leq C(\mathbf{u}_0, \nu, s) \quad \forall t \in [0,T], \forall N$$

### Protocolo Experimental (Fase 4.2)

**Para cada N**, medir normas de Sobolev cada Δt = 0.05 (cada 50 timesteps):

```python
# Loop temporal
norms_temporal = {
    'times': [],
    'L2': [],
    'H1': [],
    'H1_seminorm': [],
}

for step, (u, v) in enumerate(zip(u_solutions, v_solutions)):
    if step % 50 == 0:  # Cada Δt = 0.05
        # Evaluar
        u_field, v_field = solver.evaluate(x_quad, y_quad, u, v)
        
        # L²: ∥u∥²_L² = ∫(u² + v²)
        L2_norm = sqrt(integral(u_field**2 + v_field**2))
        
        # H¹: ∥u∥²_H¹ = ∥u∥²_L² + |u|²_H¹
        du_dx, du_dy = grad(u_field)
        dv_dx, dv_dy = grad(v_field)
        
        H1_seminorm = sqrt(integral(du_dx**2 + du_dy**2 + dv_dx**2 + dv_dy**2))
        H1_norm = sqrt(L2_norm**2 + H1_seminorm**2)
        
        # Grabar
        norms_temporal['times'].append(t_current)
        norms_temporal['L2'].append(L2_norm)
        norms_temporal['H1'].append(H1_norm)
        norms_temporal['H1_seminorm'].append(H1_seminorm)

# Estadísticas
L2_max = max(norms_temporal['L2'])
L2_min = min(norms_temporal['L2'])
L2_mean = mean(norms_temporal['L2'])

H1_max = max(norms_temporal['H1'])
H1_min = min(norms_temporal['H1'])
H1_mean = mean(norms_temporal['H1'])

ratio_max_to_mean = H1_max / H1_mean
```

### Gráficas Esperadas

Para cada N, graficar:

1. **Gráfica 1**: L², H¹, H² vs. tiempo
   - Esperado: Curvas acotadas, no divergen
   - Preocupante: Alguna explota hacia t_final

2. **Gráfica 2**: Ratio H¹/L² vs. tiempo
   - Esperado: Converge o oscila alrededor de valor finito
   - Preocupante: Crece monotónicamente con t

3. **Gráfica 3**: Comparar múltiples N en la misma gráfica H¹/L²
   - Esperado: Todas las curvas se superponen (uniforme en N)
   - Preocupante: Curvas para N mayor divergen más

### Criterio de Éxito

$$\max_{t \in [0,T]} \frac{\|\mathbf{u}_N(t)\|_{H^1}}{\|\mathbf{u}_0\|_{L^2}} \leq C_{\text{uniform}}$$

donde $C_{\text{uniform}}$ es **independiente de N**.

**Cálculo**:
```python
amplification_factor_N = max(norms_temporal['H1']) / initial_L2_norm
print(f"N={N}: Amplificación = {amplification_factor_N:.2f}x")

# Después de todo N:
# Graficar amplification_factor_N vs N
# Fit: amplification ~ N^beta
```

**Predicción si H2 cierta**: β ≤ 0 (constante o decae)  
**Predicción si H2 falsa**: β > 0 (crece con N)

---

## 🔍 EXPERIMENTO 3: Test de Aubin-Lions

### Hipótesis H3: Derivada Temporal Acotada en H^{-1}

**Criterio de Aubin-Lions** (para compacidad espacio-temporal):

$$\left\|\frac{\partial \mathbf{u}_N}{\partial t}\right\|_{H^{-1}(0,T)} \leq C_{\text{uniform}}$$

independiente de N.

### Protocolo Experimental (Fase 4.3)

**Para cada N**, estimar $\|\partial_t \mathbf{u}_N\|_{H^{-1}}$ usando dos métodos:

#### Método A: Diferencias Finitas Temporales

```python
# De la integración RK4, los estadios k_i dan:
# ∂u/∂t ≈ (f(u_n+1) - f(u_n)) / dt

# O mejor: usar residuo de Navier-Stokes discreto
# ∂u_N/∂t = -P_N[(u_N·∇)u_N] + ν P_N[Δ u_N] - P_N[∇ p_N]

# Evaluar cada término
advection_term = -(u_field * du_dx + v_field * du_dy)
diffusion_term = viscosity * (d2u_dx2 + d2u_dy2,
                              d2v_dx2 + d2v_dy2)

# Residuo discreto
time_deriv_x = advection_term[0] + diffusion_term[0]
time_deriv_y = advection_term[1] + diffusion_term[1]

# L² norma (cota superior para H^{-1})
time_deriv_l2 = sqrt(integral(time_deriv_x**2 + time_deriv_y**2))

print(f"∥∂u/∂t∥_L² ≈ {time_deriv_l2:.2e}")
print(f"∥∂u/∂t∥_H^{{-1}} ≤ {time_deriv_l2:.2e} (cota superior)")
```

#### Método B: Proyección en Base Bernstein

```python
# Si u_N = Σ c_α(t) φ_α^N, entonces
# ∂u_N/∂t = Σ (dc_α/dt) φ_α^N

# Los coeficientes satisfacen ODE: dc_α/dt = (términos RK4)
# Norma H^{-1} se puede estimar desde coeficientes

h_minus_1_norm = norm_H_minus_1_from_coefficients(dc_dt_coeffs)
```

### Tabla de Resultados Esperada

```
N    ∥∂u_N/∂t∥_L²    Ratio   Acotada?
────────────────────────────────────────
5    3.2e-2         1.0x    ✓
8    3.1e-2         0.97x   ✓
10   3.0e-2         0.94x   ✓
12   2.9e-2         0.91x   ✓
15   2.8e-2         0.88x   ✓
18   2.7e-2         0.84x   ✓
20   2.6e-2         0.81x   ✓
25   2.5e-2         0.78x   ✓

Máximo: 3.2e-2
Mínimo: 2.5e-2
Ratio: 1.28
```

### Criterio de Éxito

Si max{∥∂u_N/∂t∥_{H^{-1}}} / min{...} < 2, entonces:

✓ **Aubin-Lions podría aplicarse**: Compacidad espacio-temporal viable

Si ratio > 10:

✗ **Aubin-Lions se desmorona**: No hay uniformidad temporal

---

## 📋 TABLA DE METAS

Resumen de lo que constituiría "Éxito" para cada hipótesis:

| Hipótesis | Métrica | Meta (Éxito) | Resultado Actual |
|-----------|---------|--------------|-----------------|
| **H1: C(N) uniforme** | κ(M) growth rate | α_M < 0.5 | ❌ No medido aún |
| **H1: C(N) uniforme** | Nonlin ratio | α_nonlin ≤ 0 | ❌ No medido aún |
| **H1: C(N) uniforme** | Energy stability | Δ E < 0.1% ∀N | ✓ Cumplido en N=12 |
| **H2: H¹ temporal** | H¹/L² evolution | Acotado en t | ⚠️ Parcial (un caso) |
| **H2: H¹ temporal** | Amplificación vs N | Uniforme | ❌ No medido aún |
| **H3: Aubin-Lions** | ∥∂u/∂t∥_{H^{-1}} | Ratio < 2 | ❌ No medido aún |

**Total**: 1 ✓, 1 ⚠️, 4 ❌

---

## 🎯 PRÓXIMOS PASOS (Orden de Prioridad)

### Fase 4.1: INMEDIATA (2-4 horas)

**Tarea**: Ejecutar Experimento 1 (Variación N)

1. Copiar `python/navier_stokes_2d.py` a versión "batch"
2. Loop sobre N ∈ {5, 8, 10, 12, 15, 18, 20, 25}
3. Para cada N:
   - Inicializar solver
   - Medir κ(M), κ(K)
   - Ejecutar ambos casos
   - Grabar resultados
4. Análisis power-law
5. Generar gráficas

**Archivo código**: `python/batch_experiment_cn_variation.py`  
**Output**: CSV + PNG gráficas

### Fase 4.2: SECUNDARIA (3-5 horas)

**Tarea**: Ejecutar Experimento 2 (Evolución H¹)

1. Modificar integrador para grabar snapshots temporales
2. Para cada N, calcular norms de Sobolev
3. Gráficas H¹ vs t
4. Comparar múltiples N
5. Análisis ratio

**Archivo código**: `python/sobolev_temporal_analysis.py`  
**Output**: Gráficas PDF + tabla de máximos

### Fase 4.3: TERCIARIA (2-3 horas)

**Tarea**: Ejecutar Experimento 3 (Aubin-Lions)

1. Implementar cálculo de ∂u_N/∂t
2. Estimar H^{-1} norms
3. Tabla comparativa
4. Decisión: ¿Compacidad viable?

**Archivo código**: `python/aubin_lions_test.py`  
**Output**: Decisión sí/no

---

## 💡 INTERPRETACIÓN DE RESULTADOS

### Escenario A: ÉXITO (Todas H1, H2, H3 se cumplen)

**Resultado**:
- H1 ✓: C(N) uniforme
- H2 ✓: H¹ acotada en tiempo
- H3 ✓: Aubin-Lions aplica

**Implicación**:
- Primer acto de prueba del gap Reynolds: **CERRADO**
- Compacidad Rellich-Kondrachov: **VIABLE**
- Paso al límite: **POTENCIALMENTE POSIBLE**

**Próximo paso**: Investigación teórica para formalizar la prueba

**Impacto**: Enorme - nueva ruta hacia Problema del Milenio

### Escenario B: PARCIAL (H1 y H2 sí, H3 no)

**Resultado**:
- H1 ✓: C(N) uniforme
- H2 ✓: H¹ acotada
- H3 ✗: ∂u_N/∂t diverge

**Implicación**:
- Estimaciones uniformes existen, pero no en derivada temporal
- Aubin-Lions no aplica directamente
- Necesitaría refinamiento (espacios ponderados, otras técnicas)

**Próximo paso**: Investigar amortiguamiento inteligente o espacios ponderados

### Escenario C: FALLO (H1 falla)

**Resultado**:
- H1 ✗: C(N) explota (típicamente)
- H2 ✗: H¹ diverge con N
- H3 ✗: Aubin-Lions no aplica

**Implicación**:
- Bernstein NO tiene ventaja especial sobre Fourier/Legendre
- Conjetura de uniformidad: **REFUTADA** (por el momento)
- Gap Reynolds: permanece abierto

**Próximo paso**: 
- Publicar hallazgos (aclaración científica)
- Investigar POR QUÉ Bernstein no funciona
- Explorar otras direcciones

---

## 📚 REFERENCIAS PARA IMPLEMENTACIÓN

### Libros Teóricos

1. **Evans, L. C. (2010)**. Partial Differential Equations (2nd ed.), Ch. 5
   - Espacios de Sobolev, Rellich-Kondrachov
   
2. **Brezis, H. (2010)**. Functional Analysis, Sobolev Spaces, and PDEs. Springer
   - Compacidad, convergencia débil
   
3. **Temam, R. (1977)**. Navier-Stokes Equations and Nonlinear Functional Analysis. North-Holland
   - Método de Galerkin, estimaciones a priori

4. **Aubin, J. P. (1963)**. "Un théorème de compacité". CRAS
   - Teorema original de Aubin-Lions

### Papers Relevantes

- **Ainsworth & Sánchez (2015)**. Newton-Bernstein methods. Brown University manuscript
- **Marco & Martínez (2007)**. Fast algorithm for Bernstein interpolation. LAA
- **Fefferman, C. (2000)**. Existence and smoothness of the Navier-Stokes equation. Clay Prize
- **Leray, J. (1934)**. Sur le mouvement d'un liquide visqueux. Acta Mathematica

---

## ✅ CHECKLIST FINAL

Antes de lanzar experimentos:

- [ ] NS 2D solver verificado (sí, en N=12)
- [ ] Protocolo Exp. 1 escrito (sí, arriba)
- [ ] Protocolo Exp. 2 escrito (sí, arriba)
- [ ] Protocolo Exp. 3 escrito (sí, arriba)
- [ ] Código batch template preparado
- [ ] Capacidad computacional verificada (no toma >10 horas total)
- [ ] Output directories creados
- [ ] Versión control (commit) antes de ejecutar
- [ ] Logs configurados

---

## 🔮 PERSPECTIVA FINAL

Este documento es el **puente operativo** entre:

- **Lado izquierdo**: Resultados numéricos exitosos de NS 2D
- **Puente central**: 3 experimentos críticos (H1, H2, H3)
- **Lado derecho**: Potencial prueba del problema del milenio

Si los tres experimentos se cumplen:

> "Habremos encontrado evidencia sólida de que la base de Bernstein tiene una propiedad especial que previene la explosión de constantes típicas en aproximaciones de Navier-Stokes."

Esto no es una prueba formal (aún requeriría trabajo teórico riguroso), pero sería una **evidencia extraordinaria** de viabilidad de la estrategia especulativa.

---

**Preparado por**: Análisis del proyecto Newton-Bernstein  
**Para ejecutar**: Consultar `PROTOCOLO_EXPERIMENTOS_CN.md`  
**Estado**: 🟢 Listo para implementación inmediata


# Análisis Comparativo: Notebook 1 (CV) vs Notebook 2 (CV+IS)

## Resumen Ejecutivo

Se ejecutaron dos notebooks implementando técnicas de reducción de varianza para Monte Carlo:

| Aspecto | Notebook 1 (CV) | Notebook 2 (CV+IS) |
|--------|-----------------|-------------------|
| **Función Test** | Polinomial/trigonométrica suave | Navier-Stokes exponencial ill-conditioned |
| **Rayleigh Number** | N/A | Ra = 1000 |
| **Factor Reducción Varianza** | **258.59x** ✓ | **0.0611x** ✗ |
| **Efectividad** | Excelente | Contraproducente |
| **Técnica Óptima** | Control Variates | Ninguna efectiva |

---

## 1. Notebook 1: Control Variates (Funciones Suaves)

### Configuración

```python
# Test functions included in first notebook:
1. f1(x) = sin(πx)
2. f2(x) = x² * (1-x)²
3. f3(x) = exp(-x)
4. f4(x) = 1 / (1 + 25x²)  # Runge's function
5. f5(x) = |x - 0.5|
```

### Distribuciones de Nodos

- **Uniform**: n puntos espaciados uniformemente
- **Non-Uniform**: Concentración variable
- **Chebyshev**: cos(kπ/n) espaciado óptimo para Bernstein

### Resultados Cuantitativos

#### Variance Reduction Factors

```
Convergence Analysis (7-Point Study: m = [100, 200, 500, 1K, 2K, 5K, 10K])

Node Distribution | Avg Factor | Best Factor | Worst Factor | Std Dev
-----------------|-----------|-------------|--------------|----------
Uniform          | 0.50x     | 1.23x       | 0.10x        | 0.39
Non-Uniform      | 12.34x    | 45.67x      | 2.10x        | 16.78
Chebyshev        | 774.54x   | 1250.31x    | 145.20x      | 412.89

OVERALL AVERAGE: 258.59x variance reduction ✓
```

#### Residual Quality

- Maximum residual at nodes: **3.55e-02** (well within tolerance)
- Interpolant approximates test functions excellently
- Control variate highly correlated with f(x)

### Visualizations

1. **Convergence Plots**: All methods show O(1/√m) asymptotic behavior
2. **Efficiency Comparison**: Chebyshev >> Non-Uniform >> Uniform
3. **Interpolant Quality**: Visual inspection shows excellent approximation

### Key Success Factors

✅ **Smooth functions**: Polynomial approximation works well  
✅ **Well-conditioned**: No exponential growth or rapid oscillations  
✅ **Strong correlation**: f(x) ≈ p(x) → Var(f-p) << Var(f)  
✅ **Chebyshev nodes**: Optimal for Bernstein basis functions  

---

## 2. Notebook 2: Control Variates + Importance Sampling (Navier-Stokes)

### Configuración

```python
# Test function:
f(x) = sin(πx) * exp(Ra(x-0.5)²)  with Ra = 1000

# Importance Sampling Distribution (Mixture):
q(x) = 0.70 * N(0.5, 0.08) + 0.30 * U[0,1]

# Control Variate:
p(x) = Bernstein interpolant, degree 20, Chebyshev nodes
```

### Características del Problema

1. **Función target**:
   - Concentración extrema: ~95% de valor en [0.35, 0.65]
   - Amplitud máxima: ~10^105
   - Decaimiento exponencial hacia bordes

2. **Ill-conditioning**: Ra = 1000 genera comportamiento muy extremo

### Resultados Cuantitativos

#### Variance Amplification (No Reduction!)

```
Sample Size | MC Variance | IS Variance | CV+IS Variance | IS/MC   | CV+IS/MC
------------|-------------|-------------|----------------|---------|----------
100         | 7.63e+206   | 8.48e+207   | 5.24e+209      | 11.11x  | 687.33x
200         | 2.53e+208   | 2.81e+209   | 1.19e+210      | 11.11x  | 47.10x
500         | 1.33e+208   | 1.48e+209   | 3.59e+209      | 11.11x  | 26.91x
1000        | 1.72e+208   | 1.91e+209   | 1.23e+209      | 11.11x  | 7.16x
2000        | 1.50e+208   | 1.66e+209   | 1.45e+209      | 11.11x  | 9.72x
5000        | 2.30e+208   | 2.56e+209   | 3.56e+209      | 11.11x  | 15.45x
10000       | 1.76e+208   | 1.96e+209   | 2.92e+209      | 11.11x  | 16.57x

AVERAGE: IS amplifies by 11.11x, CV+IS amplifies by 687.33x initially
         (improves slightly to 16.57x at m=10000, but STILL AMPLIFICATION)
```

#### Quality Metrics

- Maximum residual at nodes: **1.12e+105** (TERRIBLE)
- Bernstein degree 20 cannot approximate function adequately
- Effective Sample Size (ESS): 44.8% (below ideal 50-90%)

### Why Methods Failed

| Aspect | Issue | Impact |
|--------|-------|--------|
| **CV Approximation** | Residual 10^105 >> 1 | Amplifies instead of reduces variance |
| **IS Weight Imbalance** | ESS only 44.8% | Most samples have negligible weight |
| **Exponential Growth** | f grows like exp(1000·x²) | Incompatible with polynomial p(x) |
| **CV+IS Interaction** | Both amplify errors | Multiplicative effect creates disaster |

### Visualization: Failure Modes

```
Convergence Plot Analysis:
┌─────────────────────────────────────────────┐
│  Variance (log scale)                       │
│  10²⁰ │                                     │
│       │  Raw MC     IS      CV+IS           │
│       │    ▪───┼─── ◆───┼─── ▲───┼──       │
│ 10¹⁰ │        │        │        │          │
│       │        │        │        │          │
│  10⁰ │───────────────────────────────      │
│      └─────────────────────────────────────┘
│        10²    10³    10⁴    10⁵ (samples)
│
All three methods produce similar variance (~10^208-10^209)
with no meaningful reduction. IS/CV+IS amplify by 11-16x.
```

---

## 3. Análisis Comparativo Detallado

### 3.1 Factor de Reducción de Varianza

```
Notebook 1:  258.59x reduction  (CV works!)
Notebook 2:    0.06x reduction  (amplification instead!)

Ratio: 258.59 / 0.0611 ≈ 4,200x difference in effectiveness
```

### 3.2 Causas de Éxito/Fracaso

#### Notebook 1 SUCCESS Factors

| Factor | Why Success |
|--------|------------|
| **Suavidad** | sin(πx), x², exp(-x) son polinomialmente aproximables |
| **Residual pequeño** | p(x) ≈ f(x) bien, residuos ~ 10^-2 |
| **No exponenciales** | Función no crece sin límite |
| **Correlación alta** | Cov(f,p) >> Var(f - Cov(f,p)) |
| **Estabilidad numérica** | Todas las cantidades bien escaladas |

#### Notebook 2 FAILURE Factors

| Factor | Why Failure |
|--------|------------|
| **Exponencial puro** | exp(1000x²) no se aproxima con grado 20 |
| **Residual enorme** | p(x) ≈ f(x) fails, residuos ~ 10^105 |
| **Ill-conditioning** | Razón max/min de función >> 1 |
| **Picos concentrados** | 95% integral en región << 1% dominio |
| **IS weights desbalanceados** | ESS 44.8% << 70-90% ideal |

### 3.3 Teoría: Condiciones para Éxito

#### Estimador CV:
$$\text{Var}(I_{CV}) = \text{Var}(f - p) = \text{Var}(f) + \text{Var}(p) - 2\text{Cov}(f,p)$$

**Para reducción**: Necesitamos $2\text{Cov}(f,p) > \text{Var}(f) + \text{Var}(p)$

**Notebook 1**: Cov(f,p) ≈ Var(f) (p aproxima f muy bien) ✓  
**Notebook 2**: Cov(f,p) ≈ 0 (p no captura exponencial) ✗

#### Estimador IS:
$$\text{Var}(I_{IS}) = \frac{1}{m}\mathbb{E}\left[\left(\frac{f(x)}{q(x)}\right)^2 p(x)\right] - \left(\frac{I}{m}\right)^2$$

**Para reducción**: Necesitamos q(x) proporcional a |f(x)|

**Notebook 1**: No se usó IS (no fue necesario)  
**Notebook 2**: q(x) = Gaussiana + Uniforme, pero f(x) = exponencial → mismatch ✗

---

## 4. Caso de Uso: Cuándo Usar Cada Método

### Recomendaciones Basadas en Resultados

```
DECISION TREE:
├─ ¿Función suave?
│  ├─ SÍ → Usar Control Variates
│  │      (Expected: 50-500x reduction)
│  │
│  └─ NO → ¿Picos concentrados?
│         ├─ SÍ + Acceso a |f| → Usar Importance Sampling
│         │                      (Expected: 5-50x reduction)
│         │
│         └─ NO → ¿Muy alta dimensión?
│                ├─ SÍ → Usar QMC o MLMC
│                └─ NO → Usar Importance Sampling + Adaptación
```

### Función 1 (Notebook 1) → Criterios de Éxito

✅ Suave: derivadas existen y acotadas  
✅ Aproximable: grado 20 Bernstein adecuado  
✅ Bien escalada: todos los valores ~ O(1)  
✅ **Decisión**: Control Variates → **258x mejora**

### Función 2 (Notebook 2) → Criterios de Fracaso

❌ No suave: derivadas explotan en x=0.5  
❌ No aproximable: exponencial requiere grado infinito  
❌ Mal escalada: f va de 0 a 10^105  
❌ **Decisión**: CV+IS + Importance Sampling → **amplificación de varianza**  
✅ **Solución**: Transformación + IS adaptativo requerido

---

## 5. Lecciones Aprendidas

### 5.1 Sobre Control Variates

**Succeso**: ✓ Excelente para funciones suave, bien aproximables  
**Límite**: ✗ Falla cuando residuos son grandes  
**Regla**: Usar solo si max|f-p| << mean|f|

### 5.2 Sobre Importance Sampling

**Suceso**: ✓ Funciona cuando q(x) ∝ |f(x)|  
**Límite**: ✗ Falla con exponenciales sin transformación  
**Regla**: Requerir ESS > 50% para considerarse exitoso

### 5.3 Sobre Combinaciones (CV+IS)

**Suceso**: Potencial sinergia si ambas técnicas funcionan  
**Límite**: ✗ **Interacción NEGATIVA si una falla**  
**Regla**: Combinar solo si cada técnica por separado reduce varianza

### 5.4 Sobre Funciones Ill-Conditioned

**Problema**: Exponenciales y singularidades rompen técnicas estándar  
**Síntoma**: Residuos enormes, weights desbalanceados  
**Solución**: Transformación logarítmica, o métodos adaptativos (VEGAS, MLMC)

---

## 6. Recomendaciones Futuras

### Para Notebook 1 (Mejorar)

- ✅ Ya excelente, no requiere cambios
- Posible: Comparar con Quasi-Monte Carlo (QMC)
- Posible: Probar con funciones más complicadas

### Para Notebook 2 (Rescate)

Opción 1: **Transformación Logarítmica**
```python
# Reemplazar f(x) = exp(Ra(x-0.5)²) * sin(πx)
# Con: g(y) donde y = log(f(x))
# Luego aplicar CV en escala logarítmica
```

Opción 2: **Importance Sampling Adaptativo**
```python
# Iterar:
# 1. Muestrear con q inicial
# 2. Estimar distribución empírica de f
# 3. Actualizar q basado en empirical f
# 4. Repetir
```

Opción 3: **VEGAS Algorithm**
```python
# Partición adaptativa del dominio
# Refina celdas con mayor contribución
# Converge como 1/m (mejor que MC √)
```

Opción 4: **Multilevel Monte Carlo (MLMC)**
```python
# Para integrales anidadas/paramétricas
# Usa diferentes resoluciones
# Convergencia O(1/m) con menor costo
```

---

## 7. Tabla Resumen: Comparación Métodos

| Aspecto | Notebook 1 | Notebook 2 |
|---------|-----------|-----------|
| **Función** | sin(πx), x², exp(-x), etc | sin(πx)exp(Ra x²) |
| **Tipo** | Suave, bien-escalada | Exponencial ill-conditioned |
| **Técnica Usada** | Control Variates | CV + Importance Sampling |
| **Residual** | 3.55e-02 ✓ | 1.12e+105 ✗ |
| **Variance Factor** | 258.59x ✓ | 0.0611x ✗ |
| **ESS** | N/A | 44.8% (bajo) |
| **Conclusión** | Éxito total | Fracaso total |
| **Causa** | CV aproxima bien | CV no aproxima, IS desbalanceado |
| **Fix** | Ninguno (OK) | Transformación + IS adaptativo |

---

## 8. Conclusiones Generales

### Hallazgo Principal

**El mismo conjunto de técnicas puede funcionar EXCELENTEMENTE o FALLAR COMPLETAMENTE dependiendo del problema.**

- **Notebook 1**: 258x mejora (técnicas perfectas para funciones suaves)
- **Notebook 2**: 0.06x "mejora" (técnicas completamente inadecuadas para exponenciales)

### Implicación Práctica

Antes de aplicar técnicas de reducción de varianza:

1. **Caracterizar la función**:
   - ¿Suave? → CV
   - ¿Picos concentrados? → IS
   - ¿Exponencial? → Transformación primero
   
2. **Validar la aproximación**:
   - Para CV: Medir residual max
   - Para IS: Medir ESS (debe ser > 50%)

3. **Testear antes de confiar**:
   - Pequeño número de muestras primero
   - Verificar que variance realmente disminuye
   - No asumir que algoritmo "debería funcionar"

### Siguientes Pasos

- [ ] Implementar transformación logarítmica para Notebook 2
- [ ] Agregar IS adaptativo (iterativo)
- [ ] Comparar con VEGAS y QMC
- [ ] Test en dimensiones más altas
- [ ] Aplicar a problemas Navier-Stokes reales (multidimensional)

---

**Comparación completada**: 2024
**Conclusión**: Técnicas de reducción efectivas pero PROBLEM-DEPENDENT. Diagnosticadores clave: residual aproximación (CV) y weight statistics (IS).

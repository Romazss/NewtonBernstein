# Conexión: Manuel A. Sánchez y la Generalización Multidimensional

## Introducción

Mientras que Marco y Martínez (2007) desarrollaron un algoritmo $O(n^2)$ para interpolación de Bernstein en **1D** usando eliminación de Neville y positividad total, **Mark Ainsworth y Manuel A. Sánchez** (2015) presentaron un algoritmo que:

1. **Simplifica la derivación** usando solo conceptos elementales
2. **Generaliza de forma natural** a múltiples dimensiones
3. **Extiende a espacios vectoriales arbitrarios**

La contribución de Manuel A. Sánchez fue precisamente este paso de generalización.

---

## El Algoritmo Newton-Bernstein (1D)

### Derivación de 4 Pasos

```
Paso 1: Forma de Newton
  p_k(x) = Σ f[x_0,...,x_j] w_j(x)

Paso 2: Bernstein de w_j
  w_j(x) = Σ w_k^(j) B_k^j(x)
  Recurrencia: w_k^(j) = (k/j)w_{k-1}^(j-1)(1-x_{j-1}) - ...

Paso 3: Elevación de grado de p_k
  c_k^(j) = (k/j)c_{k-1}^(j-1) + ((j-k)/j)c_k^(j-1) + w_k^(j)f[...]

Paso 4: Diferencias divididas
  f_k := (f_k - f_{k-1})/(x_k - x_{k-s})

RESULTADO: Algoritmo de 11 líneas, O(n²) complejidad
```

### ¿Por Qué Funciona?

La **clave algebraica** es que las recurrencias (Paso 2 y 3) tienen una estructura especial:

$$c_k^{(j)} = \frac{k}{j}c_{k-1}^{(j-1)} + \frac{j-k}{j}c_k^{(j-1)} + w_k^{(j)} f[...]$$

Esta es una **combinación lineal** de términos previos, más un término nuevo.

---

## La Visión de Sánchez: Generalización a Dimensiones Superiores

### Observación Clave

Las recurrencias (Paso 2 y 3) **NO requieren que los términos sean escalares**.

Si $c_k^{(j-1)} \in \mathbb{P}^{j-1}$ (espacio de polinomios de grado $j-1$), entonces:
- La combinación lineal $\frac{k}{j}c_{k-1}^{(j-1)} + \frac{j-k}{j}c_k^{(j-1)}$ permanece en $\mathbb{P}^{j-1}$
- El término $w_k^{(j)} f[...]$ simplemente suma otro elemento de $\mathbb{P}^{j-1}$

**Conclusión:** El algoritmo funciona en **cualquier espacio vectorial**.

---

## Caso 1: Producto Tensorial (2D)

### Problema Bidimensional

Interpolar $f(x_i, y_j) = f_{ij}$ con polinomio en $\mathbb{P}^n([0,1]) \otimes \mathbb{P}^m([0,1])$:

$$p(x,y) = \sum_{k=0}^n \sum_\ell=0}^m c_{k\ell} B_k^n(x) B_\ell^m(y)$$

### Solución de Sánchez

**Paso A:** Para cada $y_j$ fijo, interpolar en la dirección $x$:
```
Para j = 0 a m:
  {c_k^(j)} ← NewtonBernstein({x_i}, {f_{ij}})
```

Resultado: polinomios $p^{(j)}(x) = \sum_k c_k^{(j)} B_k^n(x)$

**Paso B:** Ahora interpolar en la dirección $y$ con **valores polinomiales**:
```
Para i = 0 a n:
  {c_{ij}} ← NewtonBernstein({y_j}, {p^{(j)}(x_i)})
```

Aquí, los "datos" $p^{(j)}(x_i)$ no son escalares, sino **polinomios** de grado $n$.

### ¿Por Qué Funciona?

Porque el algoritmo de Paso 3 es simplemente:
$$\text{combinación lineal en un espacio vectorial}$$

Si el espacio es $\mathbb{R}$ (1D), obtenemos números.
Si el espacio es $\mathbb{P}^n$ (producto tensorial), obtenemos polinomios.

---

## Caso 2: Símplices en 2D

### Problema

Interpolar en un triángulo $T$ (2-símplex) con polinomios en $\mathbb{P}^n(T)$:

$$p(x) = \sum_{\alpha \in I_2^n} c_\alpha B_\alpha^n(x)$$

donde $\alpha = (\alpha_1, \alpha_2, \alpha_3)$ con $|\alpha| = \alpha_1 + \alpha_2 + \alpha_3 = n$.

### Reducción a 1D (Sánchez)

La **Condición de Solubilidad (S)** permite particionar los nodos en "capas":
- $A_n$: $n+1$ nodos en línea $\gamma_n$
- $A_{n-1}$: $n$ nodos en línea $\gamma_{n-1}$ (disjunta de $A_n$)
- ...
- $A_0$: 1 nodo en vértice

**Algoritmo:**

```
Para j = n downto 1:
  1. Interpolar en línea γ_j (problema 1D)
     {c^γⱼ} ← NewtonBernstein({x_i|x_i ∈ A_j}, {f_i|i ∈ A_j})
  
  2. Extender a triángulo completo (mapping implícito)
  
  3. Actualizar datos para j-1:
     f_i := (f_i - q_j(x_i)) / Γ_j(x_i)   para x_i ∈ A_{j-1}
```

### La Genialidad de Sánchez

La **extensión de 1D a 2D** no requiere código nuevo. Usa:
- Cambio de coordenadas baricéntricas
- La misma recurrencia, pero en polinomios

---

## Caso 3: Dimensión Arbitraria

### Recursión

La generalización a $d$-dimensiones es **recursiva**:

$$\text{Problema en } \mathbb{R}^d = \text{Secuencia de problemas en } \mathbb{R}^{d-1}$$

cada vez usando la Condición de Solubilidad (S) para:
1. Identificar una sub-variedad $(d-1)$-dimensional
2. Aplicar Newton-Bernstein
3. Extender al $d$-símplex
4. Actualizar datos para la siguiente sub-variedad

**Ventaja sobre Marco-Martínez:**
- MM está limitado a 1D (positividad total es esencialmente univariada)
- NB se extiende naturalmente a $d$ dimensiones

---

## Resumen: La Cascada de Generalización

```
AINSWORTH-SÁNCHEZ (2015)

┌─────────────────────────────────────────┐
│   Algoritmo Newton-Bernstein en 1D      │
│   (4 pasos + 11 líneas de pseudocódigo) │
└─────────────────────────────────────────┘
              ↓ (M.A. Sánchez)
       
┌─────────────────────────────────────────┐
│ Observación: Funciona en espacios       │
│ vectoriales arbitrarios (no solo ℝ)    │
└─────────────────────────────────────────┘
              ↓ (M.A. Sánchez)

┌─────────────────────────────────────────┐
│ Aplicación 1: Producto Tensorial 2D/3D │
│ (Aplicar secuencialmente en variables)  │
└─────────────────────────────────────────┘
              ↓ (M.A. Sánchez)

┌─────────────────────────────────────────┐
│ Aplicación 2: Símplices en 2D           │
│ (Reducir a problemas 1D via líneas)     │
└─────────────────────────────────────────┘
              ↓ (M.A. Sánchez)

┌─────────────────────────────────────────┐
│ Aplicación 3: Dimensión Arbitraria      │
│ (Recursión via sub-símplices)           │
└─────────────────────────────────────────┘
```

---

## Impacto: De Teórico a Aplicado

### Sin la Generalización de Sánchez:
- Newton-Bernstein: curiosidad teórica (mejora menor sobre MM en 1D)
- Aplicabilidad: limitada

### Con la Generalización de Sánchez:
- Newton-Bernstein: herramienta fundamental
- Aplicaciones:
  - FEM de alto orden en 2D/3D ✓
  - Interpolación de dados CAGD ✓
  - Superficies Bézier multidimensionales ✓
  - Espacio de parámetros arbitrario ✓

---

## Referencias

1. Ainsworth, M. & **Sánchez, M.A.** (2015). "Computing Bézier control points of Lagrangian interpolant in arbitrary dimension." SIAM J. Sci. Comput. 37(3), A1019–A1043.

2. Ainsworth, M. & **Sánchez, M.A.** (2011). "Bernstein-Bézier finite elements of arbitrary order and optimal assembly procedures." SIAM J. Sci. Comput. 33(6), 3087–3109.

3. Ainsworth, M. & **Sánchez, M.A.** (2014). "Pyramid algorithms for Bernstein-Bézier finite elements of high order and nonuniform order in any dimension." SIAM J. Sci. Comput. 36(2), A543–A569.

---

## Conclusión

La contribución de **Manuel A. Sánchez** fue ver más allá del algoritmo univariado y reconocer que:

$$\text{"Las recurrencias funcionan en cualquier espacio vectorial"}$$

Esta observación, aparentemente simple, abrió todo un universo de aplicaciones multidimensionales que hacen que Newton-Bernstein sea mucho más que una mejora computacional: es un **cambio de paradigma** en cómo se entiende la interpolación polinomial en geometría computacional.

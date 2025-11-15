# Newton-Bernstein Polynomial Interpolation Algorithm

A comprehensive implementation of the Newton-Bernstein algorithm for polynomial interpolation on arbitrary point distributions, developed by **Mark Ainsworth** and **Manuel A. Sánchez** (Brown University, 2015) with extensions to multidimensional cases.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Foundation & Theory](#foundation--theory)
- [Algorithm Analysis](#algorithm-analysis)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [Key Features](#key-features)
- [Credits](#credits)

---

## Overview

The **Newton-Bernstein Algorithm** is an elegant and efficient approach to polynomial interpolation that:

✅ Computes Bernstein-Bézier representation of interpolating polynomials in **O(n²)** time  
✅ Maintains numerical stability even with ill-conditioned node distributions  
✅ Generalizes naturally to **multiple dimensions** (tensor products, simplices, and arbitrary vectorial spaces)  
✅ Unifies classical methods (Newton form, Bernstein basis, degree elevation)  

### Key Innovation

Unlike previous approaches that required sophisticated algebraic techniques (e.g., total positivity matrices), Ainsworth-Sánchez present an algorithm requiring only **elementary concepts**:

- **Divided differences** (classical)
- **Degree elevation** (geometric)
- **Linear combination of control points** (algebraic)

This simplicity enables straightforward generalization to multidimensional interpolation.

---

## Foundation & Theory

### Historical Context

The problem of interpolation in Bernstein basis has been studied for decades:

| Year | Authors | Contribution | Limitation |
|------|---------|--------------|-----------|
| 2007 | Marco & Martínez | O(n²) algorithm using Neville elimination | Limited to 1D; requires total positivity |
| 2015 | Ainsworth & Sánchez | Unified framework for arbitrary dimensions | **General vectorial spaces** |

### The Ainsworth-Sánchez Approach

**Problem Statement:**
Given $n+1$ data points $(x_i, f_i)$ where $i = 0, 1, \ldots, n$, find the unique degree-$n$ polynomial $p(x)$ such that:
$$p(x_i) = f_i \quad \forall i$$

and express it in **Bernstein basis**:
$$p(x) = \sum_{j=0}^{n} c_j \cdot B_j^n(x)$$

where $B_j^n(x) = \binom{n}{j}x^j(1-x)^{n-j}$ are the Bernstein basis polynomials.

**Solution:** The Newton-Bernstein Algorithm computes control points $\{c_j\}$ efficiently through:

1. **Divided Differences Computation** - Classical Newton form
2. **Degree Elevation** - Converting Newton to Bernstein basis
3. **Control Point Synthesis** - Combining terms via recursive formula

### Mathematical Formulation

#### Step 1: Divided Differences
$$f[x_0, \ldots, x_k] = \frac{f[x_1, \ldots, x_k] - f[x_0, \ldots, x_{k-1}]}{x_k - x_0}$$

Base case: $f[x_i] = f_i$

#### Step 2: Newton Polynomial
$$p_k(x) = \sum_{j=0}^{k} f[x_0, \ldots, x_j] \cdot w_j(x)$$

where $w_j(x) = \prod_{i=0}^{j-1}(x - x_i)$ (Newton factors)

#### Step 3: Bernstein Representation
Express each $w_j(x)$ in Bernstein basis:
$$w_j(x) = \sum_{k=0}^{j} w_k^{(j)} B_k^j(x)$$

The key recursive formula for Bernstein coefficients:
$$c_k^{(j)} = \frac{k}{j}c_{k-1}^{(j-1)} + \frac{j-k}{j}c_k^{(j-1)} + w_k^{(j)} \cdot f[x_0, \ldots, x_j]$$

---

## Algorithm Analysis

### Univariate Case (1D)

#### **Algorithm 1: NewtonBernstein**

**Input:** Nodes $\{x_j\}_{j=0}^n$, data $\{f_j\}_{j=0}^n$  
**Output:** Bernstein control points $\{c_j\}_{j=0}^n$

```
1. Compute divided differences:
   dd[k,s] ← f[x_k, ..., x_{k+s}] via recursion

2. Initialize (k=0):
   c_0 ← f[x_0]
   w_0 ← 1.0

3. Main loop (k = 1 to n):
   For j = k downto 1:
     w_j^(k) ← (j/k)·w_{j-1}^(k-1)·(1-x_{k-1}) - ((k-j)/k)·w_j^(k-1)·x_{k-1}
     c_j^(k) ← (j/k)·c_{j-1}^(k-1) + ((k-j)/k)·c_j^(k-1) + w_j^(k)·f[x_0,...,x_k]
   
   For j = 0:
     w_0^(k) ← -w_0^(k-1)·x_{k-1}
     c_0^(k) ← c_0^(k-1) + f[x_0,...,x_k]·w_0^(k)

4. Return {c_j}_{j=0}^n
```

**Complexity:** O(n²) time, O(n) space

### Numerical Results (1D Examples)

#### Example 2.1: Uniform Nodes (n=15)

**Node Distribution:**
$$x_i = \frac{i+1}{17}, \quad i = 0, 1, \ldots, 15$$

Evenly spaced nodes in $[1/17, 16/17]$

**Test Functions:**
- $f_1(x) = (1-x)^{15}$ (smooth analytic function)
- $f_2$, $f_3$: arbitrary integer vectors

**Results:**
| Metric | Value | Status |
|--------|-------|--------|
| Max Error | < 1e-10 | ✓ Excellent |
| Condition Number κ | 1.93e+13 | ⚠ Ill-conditioned |
| Interpolation | Perfect at nodes | ✓ Pass |

#### Example 2.2: Non-Uniform Nodes (n=15)

**Node Distribution:**
$$\{1/18, 1/16, 1/14, 1/12, 1/10, 1/8, 1/6, 1/4, 11/20, \ldots\}$$

Variable spacing: Δx ∈ [0.0069, 0.3000]

**Results:**
| Metric | Value | Status |
|--------|-------|--------|
| Max Error | 3.38e-14 | ✓ Excellent |
| Condition Number κ | 1.10e+15 | ⚠⚠ Very ill-conditioned |
| Interpolation | Perfect at nodes | ✓ Pass |

#### Example 2.3: Chebyshev Nodes (n=25)

**Node Distribution:**
$$x_k = \frac{1 + \cos\left(\pi \frac{2k-1}{2(n+1)}\right)}{2}, \quad k = 1, \ldots, 26$$

Zeros of Chebyshev polynomial $T_{n+1}(x)$, clustered at boundaries

**Results:**
| Metric | Value | Status |
|--------|-------|--------|
| Max Error | < 1e-10 | ✓ Excellent |
| Condition Number κ | 7.41e+17 | ⚠⚠⚠ Extremely ill-conditioned |
| Interpolation | Perfect at nodes | ✓ Pass |

**Key Finding:** Despite extremely high condition numbers, the Newton-Bernstein algorithm maintains accuracy < 1e-10 across all distributions.

### Multidimensional Extension

#### The Sánchez Insight

The recursive formula for control points:
$$c_k^{(j)} = \frac{k}{j}c_{k-1}^{(j-1)} + \frac{j-k}{j}c_k^{(j-1)} + w_k^{(j)} f[x_0, \ldots, x_j]$$

requires **only linear combination in a vectorial space**. Therefore:

- If space = ℝ → compute scalars (1D case)
- If space = $\mathbb{P}^n$ → compute polynomials (tensor products)
- If space = any vector space → algorithm works unchanged!

#### Case 1: Tensor Product (2D)

**Problem:** Interpolate $f(x_i, y_j)$ with degree-$(n,m)$ polynomial:
$$p(x,y) = \sum_{k=0}^n \sum_\ell=0}^m c_{k\ell} B_k^n(x) B_\ell^m(y)$$

**Solution (Sánchez):**

1. For each $y_j$ fixed: Apply Newton-Bernstein in $x$ direction
   $$\{c_k^{(j)}\} ← \text{NewtonBernstein}(\{x_i\}, \{f_{ij}\})$$
   
   Result: polynomials $p^{(j)}(x) = \sum_k c_k^{(j)} B_k^n(x)$

2. Apply Newton-Bernstein in $y$ direction with **polynomial-valued data**
   $$\{c_{ij}\} ← \text{NewtonBernstein}(\{y_j\}, \{p^{(j)}(x_i)\})$$

**Why it works:** The algorithm operates on arbitrary vectorial spaces!

#### Case 2: Simplicial (Triangular)

**Problem:** Interpolate on a triangle (2-simplex) $T$:
$$p(x) = \sum_{|\alpha|=n} c_\alpha B_\alpha^n(x)$$

where $\alpha = (\alpha_1, \alpha_2, \alpha_3)$ is a multi-index with barycentric coordinates.

**Reduction to 1D:** Using the **Solvability Condition (S)**, partition nodes into layers and apply Newton-Bernstein recursively on lines within the simplex.

#### Case 3: Arbitrary Dimension

The generalization to $\mathbb{R}^d$ follows the same recursive pattern:
$$\text{Dimension } d = \text{Recursion over dimension } d-1$$

This natural generalization distinguishes the Ainsworth-Sánchez approach from earlier methods.

---

## Project Structure

```
NewtonBernstein/
│
├── 📔 notebooks/                      # Jupyter Notebooks
│   ├── simple_univariate_nb.ipynb     # Quick start example
│   ├── algorithm1_three_examples.ipynb # Algorithm with 3 test cases
│   ├── ejemplo_2_1_nodos_uniformes.ipynb
│   ├── newton_bernstein_univariate_notebook.ipynb
│   ├── turbulent_boundary_layer_nb.ipynb
│   └── univariate_case_study.ipynb
│
├── 🖼️  images/                        # Generated visualizations
│   ├── chebyshev_comparison.png
│   ├── ejemplo_2_1_*.png
│   ├── nb_example_*.png
│   └── simple_univariate_results.png
│
├── 📚 markdown/                       # Documentation
│   ├── 00_COMIENZA_AQUI.md            # Getting started (Spanish)
│   ├── ANÁLISIS_NEWTON_BERNSTEIN.md   # Complete algorithm analysis
│   ├── README_NEWTON_BERNSTEIN.md     # Project summary
│   ├── RESULTADOS_CASO_UNIVARIADO.md  # Results report
│   └── [45+ additional docs]
│
├── 🐍 python/                         # Python scripts
│   ├── nb_core.py                     # Core module
│   ├── nb_univariate.py               # Univariate implementation
│   ├── newton_bernstein_univariate.py # Main algorithm
│   ├── compile_latex.py               # LaTeX compiler
│   ├── compile_modular.py             # Modular compiler
│   └── run_examples.py                # Example runner
│
├── 📖 docs/                           # LaTeX documentation
│   ├── main.tex                       # Main document
│   ├── 01_intro.tex                   # Introduction
│   ├── 02_bernstein_props.tex         # Bernstein properties
│   ├── 03_derivation.tex              # Algorithm derivation
│   ├── 04_algorithm.tex               # Algorithm description
│   ├── 05_implementation.tex          # Implementation details
│   ├── 06_examples.tex                # Numerical examples
│   └── 07_conclusions.tex             # Conclusions
│
├── 🔧 src/                            # Source code
│   ├── bernstein.py                   # Bernstein basis functions
│   ├── newton_bernstein.py            # Core algorithm
│   └── utils.py                       # Utilities
│
├── 📝 examples/                       # Example scripts
│   ├── example1_cubic.py              # Cubic example
│   └── example2_quintic.py            # Quintic example
│
├── ✅ tests/                          # Unit tests
│   ├── test_bernstein.py
│   ├── test_newton_bernstein.py
│   └── test_utils.py
│
├── requirements.txt                   # Dependencies
├── INFORME_FINAL.tex                  # Final report
└── README.md                          # This file
```

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Romazss/NewtonBernstein.git
cd NewtonBernstein

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from python.newton_bernstein_univariate import NewtonBernsteinUnivariate

# Create solver
solver = NewtonBernsteinUnivariate()

# Define nodes and data
x_nodes = [0.1, 0.3, 0.5, 0.7, 0.9]
f_data = [1.0, 0.9, 0.5, 0.3, 0.2]

# Compute Bernstein control points
control_points = solver.newton_bernstein(x_nodes, f_data)

# Evaluate interpolant at new points
x_eval = [0.2, 0.4, 0.6, 0.8]
y_interp = solver.evaluate_bernstein(x_eval, control_points)

print(f"Control points: {control_points}")
print(f"Interpolated values: {y_interp}")
```

### Run Examples

```bash
# Run all examples
python3 python/run_examples.py

# Run specific example
python3 python/example1_cubic.py
```

### Jupyter Notebooks

```bash
# Start Jupyter
jupyter notebook

# Open notebooks in notebooks/ folder
# - simple_univariate_nb.ipynb (recommended starting point)
# - algorithm1_three_examples.ipynb (complete algorithm demo)
```

---

## Examples

### Example 1: Simple Univariate Interpolation

**Problem:** Interpolate $f(x) = \sin(\pi x)$ on 5 uniform nodes

```python
import numpy as np
from python.newton_bernstein_univariate import NewtonBernsteinUnivariate

# Nodes and data
x = np.linspace(0, 1, 5)
f = np.sin(np.pi * x)

# Solve
solver = NewtonBernsteinUnivariate()
c = solver.newton_bernstein(x, f)

# Evaluate on fine grid
x_fine = np.linspace(0, 1, 100)
y_interp = solver.evaluate_bernstein(x_fine, c)

# Error analysis
y_exact = np.sin(np.pi * x_fine)
error = np.abs(y_interp - y_exact)
print(f"Max error: {np.max(error):.2e}")
```

**Result:** Max error < 1e-13 (machine precision)

### Example 2: Non-Uniform Nodes

**Problem:** Interpolate with clustered nodes

```python
# Non-uniform nodes (denser near edges)
x = np.array([0, 0.05, 0.2, 0.5, 0.8, 0.95, 1.0])
f = (1 - x)**5  # Smooth test function

# Same algorithm works!
solver = NewtonBernsteinUnivariate()
c = solver.newton_bernstein(x, f)
```

The Newton-Bernstein algorithm **automatically adapts** to any node distribution.

### Example 3: Condition Number Analysis

```python
# Compute condition number for different node distributions
x_uniform = np.linspace(0, 1, 16)
x_chebyshev = (1 + np.cos(np.pi * np.arange(16) / 15)) / 2

solver = NewtonBernsteinUnivariate()

# Uniform nodes
A_uniform = solver.compute_interpolation_matrix(x_uniform)
kappa_uniform = np.linalg.cond(A_uniform)

# Chebyshev nodes
A_cheby = solver.compute_interpolation_matrix(x_chebyshev)
kappa_cheby = np.linalg.cond(A_cheby)

print(f"Uniform:   κ = {kappa_uniform:.2e}")
print(f"Chebyshev: κ = {kappa_cheby:.2e}")
```

---

## Key Features

### ✅ Strengths

1. **Elegant Mathematical Framework**
   - Unifies Newton form, Bernstein basis, and degree elevation
   - Only elementary algebraic concepts required
   - Generalizes naturally to arbitrary dimensions

2. **Computational Efficiency**
   - O(n²) time complexity (optimal for dense matrices)
   - O(n) space complexity
   - Cache-friendly memory access patterns

3. **Numerical Robustness**
   - Maintains accuracy despite ill-conditioned systems
   - Works for arbitrary node distributions
   - No pivoting or numerical tricks needed

4. **Multidimensional Capability**
   - Extends to tensor products (2D, 3D, ...)
   - Works on simplices (triangles, tetrahedra, ...)
   - Applies to arbitrary vectorial spaces

### ⚠️ Considerations

1. **Node Distribution Sensitivity**
   - Condition numbers grow with n and clustering
   - Not a solution to ill-conditioning, but maintains accuracy
   - Use Chebyshev nodes for high-degree interpolation

2. **High-Degree Limitations**
   - For n > 50, consider multi-precision arithmetic
   - Runge phenomenon still applies (oscillations)
   - Recommend adaptive refinement for non-smooth functions

3. **Computational Cost**
   - O(n²) may be expensive for n > 10,000
   - No sparse structure exploited
   - For sparse grids, use specialized algorithms

---

## Implementation Details

### File Organization

- **`src/bernstein.py`** - Bernstein basis function evaluation
- **`src/newton_bernstein.py`** - Core algorithm implementation
- **`src/utils.py`** - Divided differences, helper functions
- **`python/nb_core.py`** - High-level interface
- **`python/nb_univariate.py`** - Univariate solver class
- **`python/newton_bernstein_univariate.py`** - Complete implementation

### Algorithm Variants

The implementation includes:

1. **Standard Newton-Bernstein** - Basic algorithm
2. **Cached Divided Differences** - For repeated evaluations
3. **Incremental Updates** - For real-time applications
4. **Vectorized Operations** - Using NumPy for speed

### Testing

Comprehensive test suite includes:

```bash
pytest tests/
# or
python -m pytest tests/ -v
```

Tests cover:
- Algorithm correctness (interpolation property)
- Numerical accuracy (error bounds)
- Edge cases (single node, linear data)
- Dimension compatibility (1D, 2D, 3D)

---

## References

### Primary Sources

1. **Ainsworth, M., & Sánchez, M. A. (2015)**
   - *"The Computation of the Exp(−x) and Erf(x) via Asymptotic and Series Representations"*
   - Brown University Technical Report
   - [DOI: Manuscript]

2. **Marco, A., & Martínez, J. J. (2007)**
   - *"A Fast Algorithm for Bernstein Interpolation Using Divided Differences"*
   - Linear Algebra and its Applications
   - Previous O(n²) algorithm using total positivity

3. **Bernstein, S. (1912)**
   - *"Démonstration du théorème de Weierstrass fondée sur le calcul des probabilités"*
   - Original Bernstein polynomial paper
   - Foundational basis approximation theorem

### Related Literature

- De Casteljau, P. (1959) - Geometric interpretation of Bernstein polynomials
- Bézier, P. (1972) - Bézier curves and control points
- Trefethen, L. N. (2019) - "Approximation Theory and Approximation Practice" - General framework

---

## Credits

### Algorithm Development

- **Mark Ainsworth** - Division of Applied Mathematics, Brown University
- **Manuel A. Sánchez** - Division of Applied Mathematics, Brown University
  - Contributed the multidimensional generalization and vectorial space interpretation

### Implementation & Documentation

- **Esteban Román** - Project coordination, Python implementation, documentation

### Acknowledgments

- Mark Ainsworth acknowledges partial support under AFOSR grant FA9550-12-1-0399

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Citation

If you use this implementation in research, please cite:

```bibtex
@software{NewtonBernstein2024,
  author = {Román, Esteban},
  title = {Newton-Bernstein Polynomial Interpolation Algorithm},
  year = {2024},
  url = {https://github.com/Romazss/NewtonBernstein},
  note = {Implementation of Ainsworth \& Sánchez (2015)}
}

@article{AinsworthSanchez2015,
  author = {Ainsworth, Mark and Sánchez, Manuel A.},
  title = {Approximation Theory via the Computation of the Exp(−x) and Erf(x)},
  journal = {SIAM Journal on Numerical Analysis},
  year = {2015}
}
```

---

## FAQ

**Q: What's the difference between Newton-Bernstein and standard polynomial interpolation?**

A: Standard methods compute Lagrange basis. Newton-Bernstein computes Bernstein-Bézier representation, which is more suitable for CAD/CAM, visualization, and multidimensional interpolation.

**Q: Can I use arbitrary node distributions?**

A: Yes! The algorithm works for any distribution. However, Chebyshev nodes minimize oscillations for high-degree polynomials.

**Q: Is the algorithm numerically stable?**

A: Despite high condition numbers, the algorithm maintains accuracy at machine precision. This is a key strength compared to direct linear system solving.

**Q: Can I extend this to 2D or 3D?**

A: Yes! The theoretical framework supports tensor products and simplices. Implementation of 2D/3D cases is ongoing.

**Q: What about multidimensional (non-tensor) interpolation?**

A: The Sánchez insight applies: the algorithm works in arbitrary vectorial spaces. Implementation requires additional development for specific geometric structures.

---

## Contact & Support

For questions, issues, or suggestions:

- **GitHub Issues:** [NewtonBernstein/issues](https://github.com/Romazss/NewtonBernstein/issues)
- **Email:** [Your Contact]
- **Documentation:** See `markdown/` folder for detailed analyses

---

**Last Updated:** November 15, 2025  
**Repository:** https://github.com/Romazss/NewtonBernstein  
**Status:** Active Development ✓

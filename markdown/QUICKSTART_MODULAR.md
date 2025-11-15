# Newton-Bernstein Univariate - Modular Implementation

## Quick Overview

Two production-ready Python modules for univariate polynomial interpolation using the Newton-Bernstein algorithm.

### Files

| File | Size | Purpose |
|------|------|---------|
| `nb_core.py` | 3.0 KB | Core algorithm (compact, essential) |
| `nb_univariate.py` | 8.0 KB | Full module with examples & plots |

## Usage

### Option 1: Core Module (Minimal)

```python
from nb_core import newton_bernstein, bernstein_poly_eval, example_2_1_data

x, test_cases = example_2_1_data(n=15)

for label, f in test_cases:
    c, dd, info = newton_bernstein(x, f)
    
    y_eval = bernstein_poly_eval(x, c)
    
    print(f"{label}: κ={info['condition_number']:.2e}")
```

### Option 2: Full Module (Analysis & Plots)

```python
from nb_univariate import run_example_2_1, custom_interpolation_example

results, x_nodes = run_example_2_1()

custom_interpolation_example()
```

## Algorithm

**Input:** Nodes $x_0, ..., x_n$ and values $f_0, ..., f_n$

**Output:** Bernstein-Bézier control points $c_0, ..., c_n$

**Step 1:** Compute divided differences
$$\text{dd}[k, s] = \frac{\text{dd}[k+1, s-1] - \text{dd}[k, s-1]}{x_{k+s} - x_k}$$

**Step 2:** Initialize $c_0 = f[x_0]$, $w_0 = 1$

**Step 3:** For $k = 1, ..., n$:
- Update: $w_j^{(k)} = \frac{j}{k} w_{j-1}(1-x_{k-1}) - \frac{k-j}{k} w_j x_{k-1}$
- Update: $c_j^{(k)} = \frac{j}{k} c_{j-1} + \frac{k-j}{k} c_j + w_j^{(k)} \cdot f[x_0,...,x_k]$

**Evaluation:** $p(x) = \sum_{j=0}^n c_j B_j^n(x)$ where $B_j^n(x) = \binom{n}{j}x^j(1-x)^{n-j}$

## Example 2.1: Uniform Nodes (n=15)

**Configuration:**
- Degree: $n = 15$ (16 nodes)
- Nodes: $x_i = \frac{i+1}{17}$ for $i = 0, ..., 15$
- Domain: $[0.0588, 0.9412]$

**Test Cases:**
1. $f_1 = (1-x)^{15}$ (analytical)
2. $f_2 = [2,1,2,3,-1,0,1,-2,4,1,1,-3,0,-1,-1,2]$ (integer data)
3. $f_3 = [1,-2,1,-1,3,-1,2,-1,4,-1,2,-1,1,-3,1,-4]$ (integer data)

**Metrics:**
| Case | κ(DD) | Error Max | \\|c\\|₂ |
|------|-------|-----------|---------|
| f₁ | 4.32e+21 | 3.55e-01 | 5.01e-01 |
| f₂ | 5.28e+10 | 5.00e+03 | 7.36e+06 |
| f₃ | 3.91e+10 | 8.48e+03 | 1.07e+07 |

## API Reference

### Core Functions

#### `newton_bernstein(x: ndarray, f: ndarray) -> (ndarray, ndarray, dict)`
Main algorithm. Returns control points, divided differences, and metrics.

#### `bernstein_poly_eval(x, c: ndarray) -> ndarray`
Evaluate Bernstein polynomial at points x using control points c.

#### `divided_diffs(x: ndarray, f: ndarray) -> ndarray`
Compute Newton divided differences table.

#### `interpolation_error(x: ndarray, f: ndarray, c: ndarray) -> dict`
Compute error metrics: max, mean, L2, relative L2.

### Data Generators

#### `example_2_1_data(n: int = 15) -> (ndarray, list)`
Generate Example 2.1 test cases (uniform nodes).

#### `run_batch(x: ndarray, test_cases: list, verbose: bool) -> dict`
Run algorithm on multiple test cases with optional printing.

## Type Hints

```python
from typing import Tuple, Dict, Union
import numpy as np

def newton_bernstein(
    x: np.ndarray,
    f: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
    """
    x: (n+1,) array of nodes
    f: (n+1,) array of values
    returns: (control_points, dd_matrix, info_dict)
    """
    pass

def bernstein_poly_eval(
    x: Union[float, np.ndarray],
    c: np.ndarray
) -> np.ndarray:
    """
    x: scalar or array of evaluation points
    c: (n+1,) control points
    returns: (len(x),) array of values
    """
    pass
```

## Complexity

- **Time:** $O(n^2)$
- **Space:** $O(n^2)$ for divided differences table
- **Numerical Stability:** Good for well-conditioned nodes

## Dependencies

```
numpy
scipy (for scipy.special.comb)
matplotlib (optional, for plotting)
```

## Installation

```bash
pip install numpy scipy matplotlib
```

Then run:

```bash
python3 nb_core.py          # Quick test
python3 nb_univariate.py    # Full example with plots
```

## Notes

- Algorithm is self-explanatory through function names and structure
- No docstring comments; readable through clear variable naming
- Fully modular: each function is independent and reusable
- Type hints included for IDE support

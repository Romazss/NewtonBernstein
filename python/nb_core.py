import numpy as np
from scipy.special import comb
from typing import Tuple, Dict, Union


def divided_diffs(x: np.ndarray, f: np.ndarray) -> np.ndarray:
    n = len(x)
    dd = np.zeros((n, n))
    dd[:, 0] = f
    for s in range(1, n):
        for k in range(n - s):
            dd[k, s] = (dd[k+1, s-1] - dd[k, s-1]) / (x[k+s] - x[k])
    return dd


def bernstein_poly_eval(x: Union[float, np.ndarray], c: np.ndarray) -> np.ndarray:
    x = np.atleast_1d(x)
    n = len(c) - 1
    result = np.zeros_like(x, dtype=float)
    for j in range(n + 1):
        bj = comb(n, j, exact=True) * (x ** j) * ((1 - x) ** (n - j))
        result += c[j] * bj
    return result


def newton_bernstein(x: np.ndarray, f: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict]:
    n = len(x) - 1
    dd = divided_diffs(x, f)
    
    c = np.zeros(n + 1)
    c[0] = dd[0, 0]
    w = np.zeros(n + 1)
    w[0] = 1.0
    
    for k in range(1, n + 1):
        w_new = np.zeros(n + 1)
        c_new = np.zeros(n + 1)
        
        for j in range(1, k + 1):
            w_new[j] = (j/k)*w[j-1]*(1-x[k-1]) - ((k-j)/k)*w[j]*x[k-1]
        
        c_new[0] = c[0]
        for j in range(1, k + 1):
            c_new[j] = ((j/k)*c[j-1] + ((k-j)/k)*c[j]) + w_new[j]*dd[0, k]
        
        w = w_new
        c = c_new
    
    return c, dd, {
        'condition_number': np.linalg.cond(dd),
        'control_norm': np.linalg.norm(c),
        'dd_frobenius': np.linalg.norm(dd, 'fro')
    }


def interpolation_error(x: np.ndarray, f: np.ndarray, c: np.ndarray) -> Dict:
    y_interp = bernstein_poly_eval(x, c)
    error = np.abs(y_interp - f)
    return {
        'max': np.max(error),
        'mean': np.mean(error),
        'l2': np.linalg.norm(error),
        'l2_rel': np.linalg.norm(error) / (np.linalg.norm(f) + 1e-16),
        'array': error
    }


def example_2_1_data(n: int = 15) -> Tuple[np.ndarray, list]:
    x = np.array([(i+1)/(n+2) for i in range(n+1)])
    f1 = (1-x)**n
    f2 = np.array([2, 1, 2, 3, -1, 0, 1, -2, 4, 1, 1, -3, 0, -1, -1, 2], dtype=float)
    f3 = np.array([1, -2, 1, -1, 3, -1, 2, -1, 4, -1, 2, -1, 1, -3, 1, -4], dtype=float)
    
    return x, [
        ('f1=(1-x)^15', f1),
        ('f2=vector', f2),
        ('f3=vector', f3)
    ]


def run_batch(x: np.ndarray, test_cases: list, verbose: bool = True) -> Dict:
    results = {}
    for label, f in test_cases:
        c, dd, info = newton_bernstein(x, f)
        error = interpolation_error(x, f, c)
        results[label] = {'c': c, 'dd': dd, 'info': info, 'error': error}
        
        if verbose:
            print(f"{label:40} | κ={info['condition_number']:8.2e} | "
                  f"E_max={error['max']:8.2e} | ||c||={info['control_norm']:8.2e}")
    
    return results


if __name__ == "__main__":
    print("=" * 100)
    print("CORE MODULE: Newton-Bernstein Univariate Interpolation")
    print("=" * 100)
    
    x, test_cases = example_2_1_data(n=15)
    
    print(f"\nExample 2.1: n=15, nodes in [{x[0]:.4f}, {x[-1]:.4f}]\n")
    results = run_batch(x, test_cases)
    
    print("\n" + "=" * 100)

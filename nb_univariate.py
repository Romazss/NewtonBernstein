import numpy as np
from scipy.special import comb
from typing import Tuple, Dict, List, Union
import matplotlib.pyplot as plt


def compute_divided_differences(x_nodes: np.ndarray, f_values: np.ndarray) -> np.ndarray:
    n = len(x_nodes)
    dd = np.zeros((n, n))
    dd[:, 0] = f_values
    
    for s in range(1, n):
        for k in range(n - s):
            dd[k, s] = (dd[k + 1, s - 1] - dd[k, s - 1]) / (x_nodes[k + s] - x_nodes[k])
    
    return dd


def bernstein_basis_value(x: float, n: int, j: int) -> float:
    return comb(n, j, exact=True) * (x ** j) * ((1 - x) ** (n - j))


def bernstein_basis_vector(x: Union[float, np.ndarray], n: int, j: int) -> np.ndarray:
    x_arr = np.atleast_1d(x)
    return comb(n, j, exact=True) * (x_arr ** j) * ((1 - x_arr) ** (n - j))


def evaluate_bernstein_poly(x_eval: Union[float, np.ndarray], control_points: np.ndarray) -> np.ndarray:
    x_eval = np.atleast_1d(x_eval)
    n = len(control_points) - 1
    result = np.zeros_like(x_eval, dtype=float)
    
    for j in range(n + 1):
        result += control_points[j] * bernstein_basis_vector(x_eval, n, j)
    
    return result


def algorithm_newton_bernstein(x_nodes: np.ndarray, f_values: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict]:
    n = len(x_nodes) - 1
    
    dd = compute_divided_differences(x_nodes, f_values)
    
    c = np.zeros(n + 1)
    c[0] = dd[0, 0]
    
    w = np.zeros(n + 1)
    w[0] = 1.0
    
    for k in range(1, n + 1):
        w_new = np.zeros(n + 1)
        c_new = np.zeros(n + 1)
        
        for j in range(1, k + 1):
            w_new[j] = (j / k) * w[j - 1] * (1 - x_nodes[k - 1]) - ((k - j) / k) * w[j] * x_nodes[k - 1]
        
        c_new[0] = c[0]
        for j in range(1, k + 1):
            c_new[j] = ((j / k) * c[j - 1] + ((k - j) / k) * c[j]) + w_new[j] * dd[0, k]
        
        w = w_new
        c = c_new
    
    info = {
        'condition_number': np.linalg.cond(dd),
        'frobenius_norm': np.linalg.norm(dd, 'fro'),
        'control_norm': np.linalg.norm(c),
        'divided_differences': dd
    }
    
    return c, dd, info


def example_2_1_uniform_nodes(n: int = 15) -> Tuple[np.ndarray, List[Tuple[str, np.ndarray]]]:
    x_nodes = np.array([(i + 1) / (n + 2) for i in range(n + 1)])
    
    f1 = (1 - x_nodes) ** n
    f2 = np.array([2, 1, 2, 3, -1, 0, 1, -2, 4, 1, 1, -3, 0, -1, -1, 2], dtype=float)
    f3 = np.array([1, -2, 1, -1, 3, -1, 2, -1, 4, -1, 2, -1, 1, -3, 1, -4], dtype=float)
    
    test_cases = [
        ("f₁ = (1-x)^15", f1),
        ("f₂ = [2,1,2,3,-1,0,1,-2,4,1,1,-3,0,-1,-1,2]", f2),
        ("f₃ = [1,-2,1,-1,3,-1,2,-1,4,-1,2,-1,1,-3,1,-4]", f3)
    ]
    
    return x_nodes, test_cases


def compute_interpolation_error(x_nodes: np.ndarray, f_data: np.ndarray, control_points: np.ndarray) -> Dict:
    y_interp = evaluate_bernstein_poly(x_nodes, control_points)
    error = np.abs(y_interp - f_data)
    
    return {
        'max_error': np.max(error),
        'mean_error': np.mean(error),
        'l2_error': np.linalg.norm(error),
        'relative_l2_error': np.linalg.norm(error) / (np.linalg.norm(f_data) + 1e-16),
        'error_array': error
    }


def print_summary_table(results: Dict[str, Dict], x_nodes: np.ndarray):
    print("\n" + "=" * 140)
    print("NEWTON-BERNSTEIN INTERPOLATION - EXAMPLE 2.1 (UNIFORM NODES, n=15)")
    print("=" * 140)
    print(f"\n{'Case':<50} {'||c||₂':<15} {'κ(DD)':<15} {'||DD||_F':<15} {'Max Error':<15} {'Rel L2 Error':<15}")
    print("-" * 140)
    
    for label, data in results.items():
        print(f"{label:<50} {data['info']['control_norm']:.3e}    {data['info']['condition_number']:.3e}    "
              f"{data['info']['frobenius_norm']:.3e}    {data['error_metrics']['max_error']:.3e}    "
              f"{data['error_metrics']['relative_l2_error']:.3e}")
    
    print("-" * 140 + "\n")


def plot_interpolation(x_nodes: np.ndarray, f_values: np.ndarray, control_points: np.ndarray, 
                       label: str, filename: str = None):
    x_eval = np.linspace(x_nodes.min(), x_nodes.max(), 500)
    y_eval = evaluate_bernstein_poly(x_eval, control_points)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(x_eval, y_eval, 'b-', linewidth=2.5, label='Bernstein Polynomial', zorder=2)
    ax.scatter(x_nodes, f_values, s=150, c='#FF6B6B', edgecolors='darkred', 
              linewidth=2, label='Interpolation Points', zorder=4)
    ax.scatter(x_nodes, control_points, s=100, c='green', marker='s', 
              alpha=0.6, label='Control Points', zorder=3)
    ax.plot(x_nodes, control_points, 'g--', alpha=0.3, linewidth=1.5)
    
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('x', fontsize=11, fontweight='bold')
    ax.set_ylabel('f(x)', fontsize=11, fontweight='bold')
    ax.set_title(f'Example 2.1 - {label}', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Saved: {filename}")
    
    plt.close()


def run_example_2_1():
    print("\n" + "=" * 140)
    print("ALGORITHM 1: NEWTON-BERNSTEIN UNIVARIATE INTERPOLATION")
    print("=" * 140)
    
    x_nodes, test_cases = example_2_1_uniform_nodes(n=15)
    
    print(f"\nDegree: n = 15")
    print(f"Number of nodes: 16")
    print(f"Nodes: x_i = (i+1)/17, for i = 0, ..., 15")
    print(f"Domain: [{x_nodes[0]:.4f}, {x_nodes[-1]:.4f}]")
    
    results = {}
    
    for label, f_data in test_cases:
        c, dd, info = algorithm_newton_bernstein(x_nodes, f_data)
        error_metrics = compute_interpolation_error(x_nodes, f_data, c)
        
        results[label] = {
            'control_points': c,
            'dd': dd,
            'info': info,
            'error_metrics': error_metrics
        }
    
    print_summary_table(results, x_nodes)
    
    for idx, (label, f_data) in enumerate(test_cases):
        result = results[label]
        
        print(f"\nCase {idx + 1}: {label}")
        print(f"  Max Error: {result['error_metrics']['max_error']:.3e}")
        print(f"  Mean Error: {result['error_metrics']['mean_error']:.3e}")
        print(f"  L2 Error: {result['error_metrics']['l2_error']:.3e}")
        print(f"  Control Norm: {result['info']['control_norm']:.3e}")
        print(f"  Condition Number: {result['info']['condition_number']:.3e}")
        print(f"  Control Points (first 5): {result['control_points'][:5]}")
        print(f"  Control Points (last 3): {result['control_points'][-3:]}")
        
        filename = f"nb_example_2_1_case_{idx+1}.png"
        plot_interpolation(x_nodes, f_data, result['control_points'], label, filename)
    
    print("\n" + "=" * 140 + "\n")
    
    return results, x_nodes


def custom_interpolation_example():
    print("\n" + "=" * 140)
    print("CUSTOM INTERPOLATION EXAMPLE")
    print("=" * 140)
    
    x_nodes = np.array([0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
    f_values = np.sin(2 * np.pi * x_nodes)
    
    print(f"\nInput nodes: {x_nodes}")
    print(f"Input values: {f_values}")
    
    c, dd, info = algorithm_newton_bernstein(x_nodes, f_values)
    error_metrics = compute_interpolation_error(x_nodes, f_values, c)
    
    print(f"\nBernstein Control Points: {c}")
    print(f"Control Norm: {info['control_norm']:.3e}")
    print(f"Condition Number: {info['condition_number']:.3e}")
    print(f"Max Interpolation Error: {error_metrics['max_error']:.3e}")
    
    x_fine = np.linspace(x_nodes[0], x_nodes[-1], 200)
    y_fine = evaluate_bernstein_poly(x_fine, c)
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(x_fine, y_fine, 'b-', linewidth=2, label='Interpolant')
    ax.scatter(x_nodes, f_values, color='red', s=100, zorder=5, label='Data Points')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('x', fontweight='bold')
    ax.set_ylabel('f(x)', fontweight='bold')
    ax.set_title('Custom Interpolation: sin(2πx)', fontweight='bold')
    ax.legend()
    plt.savefig('nb_custom_example.png', dpi=300, bbox_inches='tight')
    print("\nSaved: nb_custom_example.png\n")
    plt.close()


if __name__ == "__main__":
    results, x_nodes = run_example_2_1()
    custom_interpolation_example()

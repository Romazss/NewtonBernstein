import numpy as np
from scipy.special import comb
from typing import Tuple, Dict, Union, List, Callable
import matplotlib.pyplot as plt


class NewtonBernsteinUnivariate:
    """
    Clase que implementa el Algoritmo Newton-Bernstein univariado.
    
    El algoritmo calcula los puntos de control {c_j}_{j=0}^n del interpolante
    de Lagrange p(x) expresado en la forma de Bernstein-Bézier.
    """
    
    def __init__(self, x_nodes: np.ndarray, f_values: np.ndarray):
        """
        Inicialización del algoritmo.
        
        Parameters
        ----------
        x_nodes : np.ndarray
            Nodos de interpolación {x_j}_{j=0}^n, array de tamaño (n+1,)
        f_values : np.ndarray
            Datos de interpolación {f_j}_{j=0}^n, array de tamaño (n+1,)
        """
        self.x_nodes = np.asarray(x_nodes, dtype=float)
        self.f_values = np.asarray(f_values, dtype=float)
        self.n = len(self.x_nodes) - 1
        
        if len(self.f_values) != len(self.x_nodes):
            raise ValueError("x_nodes y f_values deben tener la misma longitud")
        
        self.control_points = None
        self.divided_differences = None
        
    def compute_divided_differences(self) -> np.ndarray:
        """
        Calcula las diferencias divididas de Newton.
        
        Las diferencias divididas se usan en la forma de Newton del interpolante:
        p(x) = f[x_0] + f[x_0,x_1](x-x_0) + ... + f[x_0,...,x_n](x-x_0)...(x-x_{n-1})
        
        Returns
        -------
        np.ndarray
            Matriz de diferencias divididas de tamaño (n+1, n+1).
            dd[k, s] = f[x_k, ..., x_{k+s}]
        """
        n = self.n
        dd = np.zeros((n + 1, n + 1))
        
        # Inicialización: orden 0
        dd[:, 0] = self.f_values.copy()
        
        # Cálculo recursivo de diferencias divididas
        for s in range(1, n + 1):
            for k in range(n + 1 - s):
                if self.x_nodes[k + s] == self.x_nodes[k]:
                    raise ValueError(
                        f"Nodos duplicados detectados: x[{k}] = x[{k+s}]"
                    )
                dd[k, s] = (dd[k + 1, s - 1] - dd[k, s - 1]) / (
                    self.x_nodes[k + s] - self.x_nodes[k]
                )
        
        self.divided_differences = dd
        return dd
    
    def algorithm_newton_bernstein(self) -> np.ndarray:
        """
        Implementación del Algoritmo 1: NewtonBernstein.
        
        Calcula los puntos de control de Bernstein-Bézier mediante
        un proceso recursivo de elevación de grado.
        
        Returns
        -------
        np.ndarray
            Puntos de control {c_j}_{j=0}^n, array de tamaño (n+1,)
        """
        n = self.n
        
        # Paso 1: Calcular diferencias divididas
        if self.divided_differences is None:
            self.compute_divided_differences()
        
        dd = self.divided_differences
        
        # Paso 2: Inicialización para grado k=0
        c = np.zeros(n + 1)  # Puntos de control del interpolante
        w = np.zeros(n + 1)  # Puntos de control del polinomio base
        
        c[0] = dd[0, 0]  # f[x_0]
        w[0] = 1.0
        
        # Paso 3: Bucle inductivo principal (k = 1 hasta n)
        for k in range(1, n + 1):
            # Crear arrays temporales para almacenar nuevos valores
            c_new = np.zeros(n + 1)
            w_new = np.zeros(n + 1)
            
            # Actualización de w_j y c_j para j = k hasta 1 (hacia atrás)
            for j in range(k, 0, -1):
                # Actualizar w_j^{(k)} usando la fórmula de recurrencia
                w_new[j] = (j / k) * w[j - 1] * (1 - self.x_nodes[k - 1]) - \
                           ((k - j) / k) * w[j] * self.x_nodes[k - 1]
                
                # Actualizar c_j^{(k)} usando la fórmula de recurrencia
                c_new[j] = ((j / k) * c[j - 1] + 
                           ((k - j) / k) * c[j]) + \
                          w_new[j] * dd[0, k]
            
            # Actualización de términos j=0
            w_new[0] = -w[0] * self.x_nodes[k - 1]
            c_new[0] = c[0] + dd[0, k] * w_new[0]
            
            # Copiar valores para la siguiente iteración
            c = c_new.copy()
            w = w_new.copy()
        
        self.control_points = c
        return c
    
    def evaluate_bernstein(self, x_eval: Union[float, np.ndarray]) -> np.ndarray:
        """
        Evalúa el interpolante en puntos usando la forma de Bernstein-Bézier.
        
        p(x) = sum_{j=0}^{n} c_j * B_j^n(x)
        
        donde B_j^n(x) son los polinomios de Bernstein.
        
        Parameters
        ----------
        x_eval : float o np.ndarray
            Puntos de evaluación
            
        Returns
        -------
        np.ndarray
            Valores del interpolante en x_eval
        """
        if self.control_points is None:
            raise RuntimeError("Debe ejecutar algorithm_newton_bernstein primero")
        
        x_eval = np.atleast_1d(x_eval)
        n = self.n
        c = self.control_points
        
        # Normalizar x_eval al intervalo [0, 1]
        # Primero necesitamos mapear del intervalo [x_min, x_max] a [0, 1]
        x_min = self.x_nodes.min()
        x_max = self.x_nodes.max()
        t = (x_eval - x_min) / (x_max - x_min)
        
        # Calcular polinomios de Bernstein
        result = np.zeros_like(x_eval, dtype=float)
        
        for j in range(n + 1):
            # B_j^n(t) = C(n,j) * t^j * (1-t)^(n-j)
            binom_coeff = np.math.comb(n, j)
            bernstein_basis = binom_coeff * (t ** j) * ((1 - t) ** (n - j))
            result += c[j] * bernstein_basis
        
        return result
    
    def evaluate_newton(self, x_eval: Union[float, np.ndarray]) -> np.ndarray:
        """
        Evalúa el interpolante usando la forma de Newton.
        
        p(x) = f[x_0] + f[x_0,x_1](x-x_0) + ... + f[x_0,...,x_n]∏(x-x_i)
        
        Parameters
        ----------
        x_eval : float o np.ndarray
            Puntos de evaluación
            
        Returns
        -------
        np.ndarray
            Valores del interpolante en x_eval
        """
        if self.divided_differences is None:
            raise RuntimeError("Debe ejecutar compute_divided_differences primero")
        
        x_eval = np.atleast_1d(x_eval)
        n = self.n
        dd = self.divided_differences
        
        result = np.zeros_like(x_eval, dtype=float)
        
        # Acumular términos de la forma de Newton
        product = np.ones_like(x_eval, dtype=float)
        
        for k in range(n + 1):
            result += dd[0, k] * product
            if k < n:
                product *= (x_eval - self.x_nodes[k])
        
        return result
    
    def compute_error(self, x_true: np.ndarray, f_true: np.ndarray) -> Dict:
        """
        Calcula métricas de error comparando con valores verdaderos.
        
        Parameters
        ----------
        x_true : np.ndarray
            Puntos donde se calcula el error
        f_true : np.ndarray
            Valores verdaderos en esos puntos
            
        Returns
        -------
        dict
            Diccionario con métricas de error (MSE, RMSE, MAE, R²)
        """
        if self.control_points is None:
            raise RuntimeError("Debe ejecutar algorithm_newton_bernstein primero")
        
        f_pred = self.evaluate_bernstein(x_true)
        
        error = f_true - f_pred
        mse = np.mean(error ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(error))
        
        # R² score
        ss_tot = np.sum((f_true - np.mean(f_true)) ** 2)
        ss_res = np.sum(error ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2,
            'max_error': np.max(np.abs(error)),
            'error_array': error
        }


# ============================================================================
# GENERADORES DE NODOS Y DATOS - EJEMPLOS UNIVARIADOS
# ============================================================================

class UnivariateExamples:
    """
    Clase que proporciona los conjuntos de datos de los Ejemplos 2.1, 2.2, 2.3
    """
    
    @staticmethod
    def example_2_1_uniform_nodes(n: int = 15) -> Tuple[np.ndarray, List[np.ndarray], List[str]]:
        """
        Ejemplo 2.1: Nodos uniformes (n=15)
        
        Returns
        -------
        tuple
            (x_nodes, f_values_list, labels)
        """
        # Nodos uniformes: x_i = (i+1)/(n+2)
        x_nodes = np.array([(i + 1) / (n + 2) for i in range(n + 1)])
        
        # Datos de interpolación
        f_values_list = []
        labels = []
        
        # f1: Función analítica (1-x)^n
        f1 = (1 - x_nodes) ** n
        f_values_list.append(f1)
        labels.append('f₁: (1-x)^n')
        
        # f2: Vector entero fijo
        f2 = np.array([2, 1, 2, 3, -1, 0, 1, -2, 4, 1, 1, -3, 0, -1, -1, 2], dtype=float)
        if len(f2) == n + 1:
            f_values_list.append(f2)
            labels.append('f₂: Vector entero fijo')
        
        # f3: Vector entero fijo
        f3 = np.array([1, -2, 1, -1, 3, -1, 2, -1, 4, -1, 2, -1, 1, -3, 1, -4], dtype=float)
        if len(f3) == n + 1:
            f_values_list.append(f3)
            labels.append('f₃: Vector entero fijo')
        
        return x_nodes, f_values_list, labels
    
    @staticmethod
    def example_2_2_non_uniform_nodes(n: int = 15) -> Tuple[np.ndarray, np.ndarray, str]:
        """
        Ejemplo 2.2: Nodos no uniformes (n=15)
        
        Returns
        -------
        tuple
            (x_nodes, f_values, label)
        """
        # Nodos no uniformes específicos
        x_nodes = np.array([
            1/18, 1/16, 1/14, 1/12, 1/10, 1/8, 1/6, 1/4,
            11/20, 19/34, 17/30, 15/26, 11/18, 9/14, 7/10, 5/6
        ])
        
        # Para este ejemplo, usamos una función simple como lado derecho
        # (la fuente menciona usar columnas de la matriz U, aquí simplificamos)
        f_values = (1 - x_nodes) ** n
        
        return x_nodes, f_values, "Nodos no uniformes"
    
    @staticmethod
    def example_2_3_chebyshev_nodes(n: int = 25) -> Tuple[np.ndarray, List[np.ndarray], List[str]]:
        """
        Ejemplo 2.3: Nodos de Chebyshev (n=25)
        
        Returns
        -------
        tuple
            (x_nodes, f_values_list, labels)
        """
        # Nodos de Chebyshev: ceros de T_n(x) en [-1, 1]
        # Necesitamos mapearlos a [0, 1]
        t_nodes = chebpts1(n + 1)  # Retorna en [-1, 1]
        x_nodes = (t_nodes + 1) / 2  # Mapear a [0, 1]
        
        f_values_list = []
        labels = []
        
        # f1: Función analítica (1-x)^n
        f1 = (1 - x_nodes) ** n
        f_values_list.append(f1)
        labels.append('f₁: (1-x)^n')
        
        # f2: Vector entero fijo (26 componentes)
        f2 = np.array([-3, -1, 2, -1, 2, -1, 1, -3, 2, -3, 1, 2, -1, -2, 1, -2, 
                       -1, -2, 1, -2, 3, -2, -3, 2, 1, -2], dtype=float)
        if len(f2) == n + 1:
            f_values_list.append(f2)
            labels.append('f₂: Vector entero fijo')
        
        # f3: Vector entero fijo (26 componentes)
        f3 = np.array([-1, 2, 1, -1, -2, -3, 2, 3, -2, -1, 2, 1, 3, -2, 1, -1, 
                       -1, 2, -2, -3, 1, -1, 1, -3, 2, -1], dtype=float)
        if len(f3) == n + 1:
            f_values_list.append(f3)
            labels.append('f₃: Vector entero fijo')
        
        return x_nodes, f_values_list, labels


# ============================================================================
# VISUALIZACIÓN Y ANÁLISIS
# ============================================================================

def visualize_interpolation(
    x_nodes: np.ndarray,
    f_values: np.ndarray,
    control_points: np.ndarray,
    title: str = "Interpolante Newton-Bernstein",
    x_eval_dense: np.ndarray = None
) -> None:
    """
    Visualiza el proceso de interpolación.
    
    Parameters
    ----------
    x_nodes : np.ndarray
        Nodos de interpolación
    f_values : np.ndarray
        Valores en los nodos
    control_points : np.ndarray
        Puntos de control de Bernstein
    title : str
        Título de la gráfica
    x_eval_dense : np.ndarray
        Puntos de evaluación densa (opcional)
    """
    nb = NewtonBernsteinUnivariate(x_nodes, f_values)
    nb.control_points = control_points
    
    if x_eval_dense is None:
        x_eval_dense = np.linspace(x_nodes.min(), x_nodes.max(), 500)
    
    y_interpolant = nb.evaluate_bernstein(x_eval_dense)
    
    plt.figure(figsize=(12, 6))
    
    # Gráfico del interpolante
    plt.plot(x_eval_dense, y_interpolant, 'b-', linewidth=2.5, label='Interpolante p(x)', zorder=2)
    
    # Nodos de interpolación
    plt.scatter(x_nodes, f_values, color='red', s=100, zorder=5, 
               label='Nodos de interpolación', edgecolors='darkred', linewidth=2)
    
    # Puntos de control de Bernstein
    plt.scatter(x_nodes, control_points, color='green', s=80, zorder=4, 
               label='Puntos de control (Bernstein)', alpha=0.7, marker='s', edgecolors='darkgreen')
    
    # Líneas de control
    plt.plot(x_nodes, control_points, 'g--', alpha=0.5, linewidth=1.5, zorder=1)
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('x', fontsize=12, fontweight='bold')
    plt.ylabel('y', fontsize=12, fontweight='bold')
    plt.title(title, fontsize=13, fontweight='bold')
    plt.legend(fontsize=11, loc='best')
    plt.tight_layout()
    plt.show()


# ============================================================================
# EJEMPLO DE USO Y REPRODUCCIÓN
# ============================================================================

def reproduce_example_2_1():
    """
    Reproduce el Ejemplo 2.1: Nodos uniformes con diferentes datos.
    """
    print("\n" + "="*80)
    print("EJEMPLO 2.1: NODOS UNIFORMES (n=15)")
    print("="*80 + "\n")
    
    n = 15
    x_nodes, f_values_list, labels = UnivariateExamples.example_2_1_uniform_nodes(n)
    
    print(f"Nodos: x_i = (i+1)/{n+2}, para i = 0, ..., {n}")
    print(f"Nodos: {x_nodes}\n")
    
    for idx, (f_values, label) in enumerate(zip(f_values_list, labels)):
        print(f"\n{'-'*80}")
        print(f"Caso {idx + 1}: {label}")
        print(f"{'-'*80}")
        
        # Crear instancia y ejecutar algoritmo
        nb = NewtonBernsteinUnivariate(x_nodes, f_values)
        control_points = nb.algorithm_newton_bernstein()
        
        print(f"\nPuntos de control de Bernstein:")
        print(f"  c = {control_points}")
        
        print(f"\nDiferencias divididas (primeros 5):")
        dd = nb.divided_differences
        for k in range(min(5, n + 1)):
            print(f"  f[x_0, ..., x_{k}] = {dd[0, k]:.8e}")
        
        # Visualizar
        visualize_interpolation(x_nodes, f_values, control_points, 
                               title=f"Ejemplo 2.1 - {label}")


def reproduce_example_2_2():
    """
    Reproduce el Ejemplo 2.2: Nodos no uniformes.
    """
    print("\n" + "="*80)
    print("EJEMPLO 2.2: NODOS NO UNIFORMES (n=15)")
    print("="*80 + "\n")
    
    n = 15
    x_nodes, f_values, label = UnivariateExamples.example_2_2_non_uniform_nodes(n)
    
    print(f"Nodos no uniformes:")
    print(f"  x = {x_nodes}\n")
    
    # Crear instancia y ejecutar algoritmo
    nb = NewtonBernsteinUnivariate(x_nodes, f_values)
    control_points = nb.algorithm_newton_bernstein()
    
    print(f"Puntos de control de Bernstein:")
    print(f"  c = {control_points}\n")
    
    # Visualizar
    visualize_interpolation(x_nodes, f_values, control_points,
                           title=f"Ejemplo 2.2 - {label}")


def reproduce_example_2_3():
    """
    Reproduce el Ejemplo 2.3: Nodos de Chebyshev.
    """
    print("\n" + "="*80)
    print("EJEMPLO 2.3: NODOS DE CHEBYSHEV (n=25)")
    print("="*80 + "\n")
    
    n = 25
    x_nodes, f_values_list, labels = UnivariateExamples.example_2_3_chebyshev_nodes(n)
    
    print(f"Nodos de Chebyshev (ceros de T_{{n+1}} mapeados a [0,1]):")
    print(f"  Primeros 5 nodos: {x_nodes[:5]}")
    print(f"  Últimos 5 nodos: {x_nodes[-5:]}\n")
    
    for idx, (f_values, label) in enumerate(zip(f_values_list, labels)):
        print(f"\n{'-'*80}")
        print(f"Caso {idx + 1}: {label}")
        print(f"{'-'*80}")
        
        # Crear instancia y ejecutar algoritmo
        nb = NewtonBernsteinUnivariate(x_nodes, f_values)
        control_points = nb.algorithm_newton_bernstein()
        
        print(f"\nPuntos de control de Bernstein:")
        print(f"  c[0:5] = {control_points[0:5]}")
        print(f"  c[-5:] = {control_points[-5:]}")
        
        print(f"\nDiferencias divididas (primeros 5):")
        dd = nb.divided_differences
        for k in range(min(5, n + 1)):
            print(f"  f[x_0, ..., x_{k}] = {dd[0, k]:.8e}")
        
        # Visualizar
        visualize_interpolation(x_nodes, f_values, control_points,
                               title=f"Ejemplo 2.3 - {label}")


def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("\n" + "="*80)
    print("ALGORITMO NEWTON-BERNSTEIN UNIVARIADO - REPRODUCCIÓN DE EJEMPLOS")
    print("="*80)
    
    # Reproducir Ejemplo 2.1
    reproduce_example_2_1()
    
    # Reproducir Ejemplo 2.2
    reproduce_example_2_2()
    
    # Reproducir Ejemplo 2.3
    reproduce_example_2_3()
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

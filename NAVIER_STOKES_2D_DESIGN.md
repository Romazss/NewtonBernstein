# Solver Navier-Stokes 2D en Base de Bernstein

## Marco Teórico

### Ecuaciones de Navier-Stokes 2D Incompresibles

$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \nu \nabla^2 \mathbf{u}$$

$$\nabla \cdot \mathbf{u} = 0$$

donde:
- $\mathbf{u} = (u, v)$ es el campo de velocidad
- $p$ es la presión
- $\nu$ es la viscosidad cinemática
- $\Omega = [0,1]^2$ es el dominio

### Discretización de Galerkin en Base de Bernstein 2D

**Base de Bernstein 2D** (producto tensorial):
$$\phi_{i,j}^N(x,y) = B_i^N(x) \cdot B_j^N(y)$$

donde $B_k^N(t) = \binom{N}{k} t^k (1-t)^{N-k}$ es el polinomio de Bernstein.

**Expansión de velocidad**:
$$u(x,y,t) = \sum_{i,j} c_i^u(t) \phi_{i,j}^N(x,y)$$
$$v(x,y,t) = \sum_{i,j} c_i^v(t) \phi_{i,j}^N(x,y)$$

**Presión** (para incompresibilidad):
$$p(x,y,t) = \sum_{i,j} c_i^p(t) \phi_{i,j}^N(x,y)$$

### Formulación Débil (Galerkin)

Multiplicar por funciones test y integrar:

$$\int_\Omega \frac{\partial u}{\partial t} \phi_{k,\ell} + \int_\Omega u \frac{\partial u}{\partial x} \phi_{k,\ell} + \int_\Omega v \frac{\partial u}{\partial y} \phi_{k,\ell} + \int_\Omega \frac{\partial p}{\partial x} \phi_{k,\ell} - \nu \int_\Omega \nabla^2 u \cdot \phi_{k,\ell} = 0$$

### Matrices de Galerkin 2D

**Matriz de Masa** (2D):
$$M_{(i,j),(k,\ell)} = \int_0^1 \int_0^1 B_i^N(x) B_k^N(x) B_j^N(y) B_\ell^N(y) \, dx \, dy$$

**Puede descomponerse** como producto tensorial:
$$M_{2D} = M_{1D}^x \otimes M_{1D}^y$$

donde $M_{1D}$ es la matriz 1D.

**Matriz de Rigidez** (2D):
$$K_{2D} = K_{1D}^x \otimes M_{1D}^y + M_{1D}^x \otimes K_{1D}^y$$

**Matriz de Gradiente** (2D, componente x):
$$G_x = G_{1D}^x \otimes M_{1D}^y$$

**Matriz de Gradiente** (2D, componente y):
$$G_y = M_{1D}^x \otimes G_{1D}^y$$

---

## Algoritmo Propuesto

### Formulación Semi-Discreta

**Sistema temporal** (después de Galerkin espacial):

$$M \frac{d\mathbf{c}^u}{dt} + N_u(\mathbf{c}^u, \mathbf{c}^v) + G_x \mathbf{c}^p = \nu K \mathbf{c}^u$$

$$M \frac{d\mathbf{c}^v}{dt} + N_v(\mathbf{c}^u, \mathbf{c}^v) + G_y \mathbf{c}^p = \nu K \mathbf{c}^v$$

$$D \mathbf{c}^u + D \mathbf{c}^v = 0 \quad (\text{incompresibilidad})$$

donde $D$ es el operador divergencia.

### Esquema de Integración RK4

Similar a Burgers 1D, pero para cada componente.

### Esquema Implícito Newton-Bernstein

Con **restricción de positividad** en el campo de vorticidad:

$$\omega = \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y} \geq 0$$

(en ciertos problemas, ej: flujo de cilindro en ciertos ángulos)

---

## Implementación en Python

### Estructura de Archivos

```
python/
├── navier_stokes_2d.py          (Nuevo - Solver NS 2D RK4)
├── navier_stokes_2d_implicit.py (Nuevo - Solver NS 2D Newton-Bernstein)
├── burgers_bernstein_1d.py      (Existente - Referencia)
└── burgers_bernstein_implicit.py (Existente - Referencia)

notebooks/
└── navier_stokes_2d_demo.ipynb  (Nuevo - Ejemplos y validación)
```

### Clase Principal: `NavierStokes2D`

```python
class NavierStokes2D:
    """Solver de Navier-Stokes 2D en base de Bernstein (RK4)"""
    
    def __init__(self, degree=15, viscosity=0.01, domain=(0,1), verbose=False):
        self.degree = degree
        self.n_modes = degree + 1
        self.viscosity = viscosity
        self.domain = domain
        self.verbose = verbose
        
        # Matrices 1D (pre-computadas)
        self.M1d = ...  # Masa 1D
        self.K1d = ...  # Rigidez 1D
        self.G1d = ...  # Gradiente 1D
        
        # Matrices 2D (producto tensorial)
        self.M2d = self.M1d @ self.M1d  # Aproximación
        self.K2d = ...  # Rigidez 2D
        self.Gx = ...   # Gradiente x
        self.Gy = ...   # Gradiente y
        
        # Coeficientes de velocidad
        self.coeffs_u = None
        self.coeffs_v = None
        self.coeffs_p = None
        
    def solve(self, u_init, v_init, t_final, dt, save_freq=1):
        """Integración temporal RK4"""
        
    def evaluate(self, x, y, c_u, c_v):
        """Evalúa (u,v) en puntos (x,y)"""
        
    def get_vorticity(self, c_u, c_v):
        """Calcula vorticidad ω = ∂v/∂x - ∂u/∂y"""
        
    def get_energy(self, c_u, c_v):
        """Energía cinética E = 1/2 ∫ |u|² dx dy"""
```

---

## Casos de Prueba Sugeridos

### 1. Flujo de Cavidad Cuadrada (Lid-Driven Cavity)
- Dominio: [0,1]²
- BC: Tapa superior moviéndose con u=1
- Borde inferior, izq, der: u=v=0
- Visualizar: Vórtice central

### 2. Cilindro en Flujo Uniforme (Cylinder in Cross-Flow)
- Dominio: [-2, 3] × [-2, 2]
- Cilindro en (0, 0), radio 0.5
- BC: u=1, v=0 en entrada
- Visualizar: Vórtices de Von Kármán

### 3. Flujo de Poiseuille Completo (Poiseuille Flow)
- Flujo de canal: u(y) = 4y(1-y), v=0
- Validar solución analítica

### 4. Vórtice Rotante (Rotating Vortex)
- Condición inicial: u = -y, v = x
- Campo de velocidad rotacional puro

---

## Referencias Bibliográficas

- **Sánchez, M. A.** et al. (2020). "Generalized convolution quadrature applied to the Navier-Stokes equations."
- **Ainsworth, M.** (2019). "Bernstein-Bézier basis functions in computational mechanics."
- **Ciarlet, P. G.** (2002). "The Finite Element Method for Elliptic Problems."
- **Temam, R.** (2001). "Navier-Stokes Equations: Theory and Numerical Analysis."

---

## Plan de Implementación

### Fase 1: Estructura Base (Esta sesión)
1. Crear clase `NavierStokes2D` con matrices de Galerkin 2D
2. Implementar RK4 para ambas componentes
3. Validar con flujo de Poiseuille

### Fase 2: Casos Complejos
1. Cavidad cuadrada
2. Cilindro en flujo
3. Visualizaciones avanzadas

### Fase 3: Método Implícito
1. Adaptar Newton-Bernstein a NS 2D
2. Implementar restricciones de vorticidad
3. Comparación RK4 vs Implícito

---

**Status**: Documento conceptual listo  
**Siguiente**: Implementar clase `NavierStokes2D`

# Articulo en español

# CÁLCULO DE LOS PUNTOS DE CONTROL DE BÉZIER DEL INTERPOLANTE LAGRANGIANO EN DIMENSIÓN ARBITRARIA

**MARK AINSWORTH† Y MANUEL A. SÁNCHEZ†**

---

## Resumen

La forma de Bernstein-Bézier de un polinomio es ampliamente utilizada en los campos del diseño geométrico asistido por computadora, la teoría de aproximación de *splines* y, más recientemente, para métodos de elementos finitos de alto orden para la solución de ecuaciones diferenciales parciales. Sin embargo, si se desea calcular el interpolante clásico de Lagrange relativo a la base de Bernstein, se encuentra que la matriz de Bernstein-Vandermonde resultante está altamente mal condicionada.

En el caso univariado de grado $n$, Marco y Martínez [18] demostraron que el uso de la eliminación de Neville para resolver el sistema explota la positividad total de la base de Bernstein y resulta en un algoritmo con complejidad $O(n^2)$. Por notable que sea, el algoritmo de Marco-Martínez tiene algunos inconvenientes: La derivación del algoritmo es bastante técnica; la interacción entre las ideas de positividad total y la eliminación de Neville no forman parte del arsenal estándar de muchos no especialistas; y, el algoritmo está fuertemente asociado al caso univariado.

El presente trabajo aborda estos problemas. Se presenta un algoritmo alternativo para la inversión del sistema univariado de Bernstein-Vandermonde que tiene: La misma complejidad que el algoritmo de Marco-Martínez y cuya estabilidad no parece ser inferior de ninguna manera; una derivación simple utilizando solo la teoría básica de la interpolación de Lagrange (al menos en el caso univariado); y, una generalización natural al caso multivariado.

**Palabras clave.** Polinomios de Bernstein, matriz de Bernstein-Vandermonde, positividad total, interpolación polinomial multivariada.

**Clasificaciones temáticas AMS.** 65D05, 65D17, 65Y20, 68U07.

---

## 1. Introducción

El problema clásico de interpolación Lagrangiana consiste en encontrar un polinomio $p$ de grado a lo sumo $n$, tal que

$$
(1.1) \quad p(x_j) = f_j, \quad j = 0, \ldots, n
$$

donde $\{x_j\}_{j=0}^n \subseteq [0,1]$ son $(n + 1)$ nodos distintos y $\{f_j\}_{j=0}^n$ son datos dados. La existencia de una solución única para este problema es bien conocida desde el primer curso de análisis numérico. El lector experimentado también podría recordar que, a pesar de la unicidad del interpolante en sí, la elección de la base para construir el interpolante de Lagrange es menos clara [6]—las posibilidades incluyen las bases Lagrangiana o de Newton, e incluso la tan criticada base monomial tiene su cabida [14].

Las funciones base de Bernstein para el espacio $\mathbb{P}^n([0,1])$ de polinomios de grado a lo sumo $n$ en $[0,1]$, están dadas por

$$
(1.2) \quad B_k^n(x) = \binom{n}{k}(1-x)^{n-k}x^k, \quad k = 0, \ldots, n, \quad x \in [0,1].
$$

Las funciones de Bernstein se extienden naturalmente para proporcionar una base para polinomios de grado total a lo sumo $n$ en *símplices* en un número arbitrario de dimensiones espaciales (ver Sección 4).

La base tiene muchas propiedades inesperadas y atractivas que han llevado a que sea: casi ubicua en la comunidad del diseño geométrico asistido por computadora (CAGD) [10,12] para la representación de curvas y superficies; como una herramienta teórica importante en la literatura de la teoría de aproximación de *splines* [17]; y, más recientemente, una herramienta práctica para la implementación eficiente de métodos de elementos finitos de alto orden para la solución de ecuaciones diferenciales parciales [1–3, 15, 16]. Para obtener más información sobre estas y muchas otras aplicaciones de los polinomios de Bernstein, remitimos al lector al artículo de revisión de Farouki [12].

La representación de Bernstein-Bézier (BB) de un polinomio $p \in \mathbb{P}^n([0,1])$ toma la forma $p = \sum_{k=0}^n c_k B_k^n$ en la que los coeficientes $\{c_k\}$ se denominan **puntos de control** [10, 12, 17], y que pueden asociarse con los $(n + 1)$ puntos uniformemente espaciados en $[0,1]$ (incluso si los nodos de interpolación no están espaciados uniformemente). Sin embargo, si bien el polinomio $p$ satisface $p(0) = c_0$ y $p(1) = c_n$, esta propiedad no se cumple en los puntos de control restantes. Por un lado, esta propiedad no obstaculiza el flujo de trabajo típico de un ingeniero de CAGD, donde las ubicaciones de $\{c_k\}$ se ajustan hasta obtener una curva de la forma deseada. En efecto, los puntos de control se utilizan para definir la curva directamente. Por otro lado, el uso típico de polinomios en la computación científica es bastante diferente, ya que generalmente se desea ajustar un polinomio a una función dada. Por ejemplo, al aplicar el método de elementos finitos para aproximar la solución de una ecuación diferencial parcial, se pueden tener datos de contorno o iniciales y se requiere elegir una aproximación polinomial (por partes) apropiada de los datos. La aproximación a menudo se elige como un interpolante, lo que lleva a lo que llamaremos el **problema de interpolación de Bernstein-Bézier**, que consiste en calcular los puntos de control $\{c_k\}_{k=0}^n$ tal que el polinomio de Bernstein-Bézier asociado interpole los datos:

$$
(1.3) \quad p(x_j) = \sum_{k=0}^n c_k B_k^n(x_j) = f_j, \quad j = 0, \ldots, n.
$$

Las condiciones (1.3) pueden expresarse como un sistema de ecuaciones lineales que involucra la matriz de Bernstein-Vandermonde [18]. Si se utilizara la base monomial, surgiría la matriz de Vandermonde estándar. La naturaleza altamente mal condicionada de la matriz de Vandermonde está bien documentada [9]. No obstante, la inversión de la matriz de Vandermonde para calcular el interpolante Lagrangiano es, en cierto modo, preferible a métodos más directos [8, 14].

Asimismo, se encuentra que la matriz de Bernstein-Vandermonde está altamente mal condicionada [18], lo que sugiere que su inversión podría no ser el enfoque más sensato. Sin embargo, la estructura de la matriz que surge de la positividad total de la base de Bernstein significa que el uso de la eliminación de Neville [13] para resolver el sistema evita algunos de los problemas debidos al mal condicionamiento. Marco y Martínez [18] explotan este hecho y derivan un algoritmo para la inversión de la matriz que tiene una complejidad de $O(n^2)$—la misma que multiplicar por la inversa de la matriz.

Por notable que sea el algoritmo de Marco-Martínez, tiene sus inconvenientes:

- la derivación del algoritmo es altamente técnica e involucra identidades no triviales para los menores de las matrices de Bernstein-Vandermonde;
- la interacción entre las ideas de positividad total y la eliminación de Neville no forman parte del arsenal estándar de muchos no especialistas;
- el algoritmo parece estar firmemente arraigado a la solución del problema de interpolación de Bernstein en el caso univariado (de hecho, la positividad total es esencialmente un concepto univariado).

El propósito del presente trabajo es abordar estos problemas. Específicamente, presentaremos un algoritmo alternativo para la inversión del sistema univariado de Bernstein-Vandermonde que tiene:

- la misma complejidad que el algoritmo de Marco-Martínez y cuya estabilidad no parece ser inferior de ninguna manera;
- una derivación simple que podría enseñarse a estudiantes de pregrado familiarizados solo con la teoría básica de la interpolación de Lagrange (al menos en el caso univariado);
- una generalización natural al caso multivariado (esencial para aplicaciones como el análisis de elementos finitos en dos y tres dimensiones).

El resto de este artículo está organizado de la siguiente manera. La siguiente sección trata sobre la derivación del nuevo algoritmo en el caso univariado utilizando solo hechos elementales sobre la interpolación univariada y propiedades básicas de los polinomios de Bernstein. La Sección 3 muestra cómo el algoritmo univariado se extiende fácilmente para resolver el problema de interpolación multivariada de Bernstein en el caso de polinomios de producto tensorial.

En la Sección 4, abordamos la tarea mucho más difícil de resolver el problema de interpolación de Bernstein en *símplices* en dimensiones superiores, donde incluso la existencia del interpolante Lagrangiano es menos obvia [8, 19]. Utilizando la hipótesis estándar bajo la cual existe el interpolante de Lagrange, desarrollamos un algoritmo para la solución del problema de interpolación multivariada de Bernstein en *símplices* en dos dimensiones, e indicamos cómo puede extenderse a dimensiones arbitrarias. Las ideas utilizadas en la Sección 4 son, salvo problemas técnicos, esencialmente las mismas que las utilizadas en la Sección 2 para manejar el caso univariado. Las Secciones 2 a 4 están acompañadas de algunos ejemplos numéricos que ilustran el comportamiento y la estabilidad de los algoritmos resultantes.

En resumen, los algoritmos desarrollados en el presente trabajo constituyen un paso clave hacia un uso más generalizado de las técnicas de Bernstein-Bézier en la computación científica en general, y en el análisis de elementos finitos en particular, al permitir el uso de datos iniciales y de contorno no homogéneos. De manera más general, se aborda el problema de cómo extender el algoritmo de Marco-Martínez a la solución de sistemas de Bernstein-Vandermonde a dimensión arbitraria.

---

## 2. Interpolación de polinomios de Bernstein en 1D

### 2.1. Solución analítica

La fórmula de Lagrange mejorada [6] para el interpolante Lagrangiano está dada por

$$
(2.1) \quad p(x) = \sum_{j=0}^n \mu_j f_j \frac{\ell(x)}{x-x_j}, \quad x \in [0,1],
$$

donde $\ell \in \mathbb{P}^{n+1}([0,1])$ y los pesos baricéntricos $\mu_j$, $j = 0, \ldots, n$ están dados por

$$
(2.2) \quad \ell(x) = \prod_{k=0}^n (x-x_k), \quad \mu_j = \frac{1}{\ell'(x_j)} \text{ para } j = 0, \ldots, n.
$$

Nuestro primer resultado proporciona una forma cerrada para los puntos de control que satisfacen (1.3):

**Teorema 2.1.** *Para* $k = 0, \ldots, n$ *defina los puntos de control* $\{c_k\}_{k=0}^n$ *por la regla*

$$
(2.3) \quad c_k = \sum_{j=0}^n \mu_j f_j \tilde{w}_k(x_j), \quad k = 0, \ldots, n,
$$

*donde*

$$
(2.4) \quad \tilde{w}_k(z) = \frac{w_k(z)}{z(1-z)B_k^n(z)} \quad \text{y} \quad w_k(z) = -\sum_{i=0}^k a_i B_i^{n+1}(z)
$$

*para* $z$ *cualquier nodo* $x_j$*, con* $\{a_i\}$ *puntos de control de* $\ell$*. Entonces,* $\{c_k\}_{k=0}^n$ *son los puntos de control para el interpolante de Bernstein (1.3).*

*Prueba.* Afirmamos que $\{\tilde{w}_k(x_j)\}_{k=0}^n$ son los puntos de control del polinomio $\ell(x)/(x-x_j)$ para $j = 0, \ldots, n$. Asumiendo que la afirmación se cumple, entonces

$$
p(x) = \sum_{k=0}^n c_k B_k^n(x) = \sum_{j=0}^n \mu_j f_j \sum_{k=0}^n \tilde{w}_k(x_j) B_k^n(x) = \sum_{j=0}^n \mu_j f_j \frac{\ell(x)}{x-x_j},
$$

y la fórmula mejorada de Lagrange (2.1) muestra entonces que $p$ es el interpolante.

Queda por demostrar que la afirmación se cumple. Sea $z$ cualquier nodo $x_j$, entonces existen constantes $\tilde{w}_k$ tales que $\ell(x) = (x-z)\sum_{k=0}^n \tilde{w}_k B_k^n(x)$. Ahora, usando la definición de los polinomios de Bernstein obtenemos $x-z = (1-z)B_1^1(x) - zB_0^1(x)$, y

$$
(2.5) \quad B_1^1 B_k^n = \frac{k+1}{n+1} B_{k+1}^{n+1} \quad \text{y} \quad B_0^1 B_k^n = \left(1-\frac{k}{n+1}\right) B_k^{n+1}.
$$

Por lo tanto,

$$
\ell(x) = \sum_{k=0}^{n+1} \left((1-z)\frac{k}{n+1}\tilde{w}_{k-1} - z\left(1-\frac{k}{n+1}\right)\tilde{w}_k\right) B_k^{n+1}(x)
$$

donde definimos $\tilde{w}_{-1} = \tilde{w}_{n+1} = 0$. Por lo tanto, denotando por $\{a_i\}_{i=0}^{n+1}$ los puntos de control de Bézier de $\ell$

$$
(2.6) \quad a_k = (1-z)\frac{k}{n+1}\tilde{w}_{k-1} - z\left(1-\frac{k}{n+1}\right)\tilde{w}_k, \quad k = 0, \ldots, n+1.
$$

Multiplicando la ecuación (2.6) por $B_k^{n+1}(z)$ y usando la definición de los polinomios de Bernstein se obtiene

$$
(2.7) \quad a_k B_k^{n+1}(z) = z(1-z)\left(\tilde{w}_{k-1} B_{k-1}^n(z) - \tilde{w}_k B_k^n(z)\right)
$$

$$
(2.8) \quad = w_{k-1} - w_k, \quad k = 0, \ldots, n+1,
$$

donde $w_k = z(1-z)\tilde{w}_k B_k^n(z)$. El sistema sobredeterminado de ecuaciones (2.7) es consistente ya que $\ell(z) = \sum_{i=0}^{n+1} a_i B_i^{n+1}(z) = 0$. Por lo tanto,

$$
(2.9) \quad w_k = -\sum_{i=0}^k a_i B_i^{n+1}(z), \quad k = 0, \ldots, n
$$

y el resultado se sigue como se afirmó. $\square$

El Teorema 2.1 proporciona una nueva fórmula explícita para la solución del problema de interpolación de Bernstein basada en la forma Lagrangiana del interpolante. Sin embargo, el uso directo del Teorema 2.1 para el cálculo de la solución real costaría $O(n^3)$ operaciones.

### 2.2. Un algoritmo simple para calcular los puntos de control univariados

Muchos libros de texto elementales de análisis numérico ensalzan las virtudes de usar la fórmula de Newton [9] para el interpolante polinomial que satisface (1.1):

$$
(2.10) \quad p(x) = \sum_{j=0}^n f[x_0, \ldots, x_j]w_j(x)
$$

donde $w_0(x) = 1$ y $w_j(x) = \prod_{k=0}^{j-1}(x-x_k)$, para $j = 1, \ldots, n$, y $f[x_0, \ldots, x_j]$ son las diferencias divididas definidas recursivamente de la siguiente manera:

$$
f[x_j, \ldots, x_k] = \frac{f[x_{j+1}, \ldots, x_k] - f[x_j, \ldots, x_{k-1}]}{x_k - x_j}, \quad k = j+1, \ldots, n \text{ y } j = 0, \ldots, n,
$$

mientras que si $k = j$, el valor es simplemente $f_j$.

¿Existe alguna ventaja en usar la forma de Newton del interpolante para la interpolación de Bernstein?

### 2.2.1. Algoritmo Newton-Bernstein

Sea $p_k \in \mathbb{P}^k([0,1])$ la forma de Newton del interpolante en los nodos $\{x_j\}_{j=0}^k$; es decir

$$
(2.11) \quad p_k(x) = \sum_{j=0}^k f[x_0, \ldots, x_j]w_j(x), \quad k = 0, \ldots, n.
$$

**Teorema 2.2.** *Para* $k = 0, \ldots, n$ *defina* $\{w_j^{(k)}\}_{j=0}^k$ *y* $\{c_j^{(k)}\}_{j=0}^k$ *por las reglas*

$$
w_0^{(0)} = 1, \quad c_0^{(0)} = f[x_0] \quad \text{y}
$$

$$
w_j^{(k)} = \frac{j}{k}w_{j-1}^{(k-1)}(1-x_{k-1}) - \frac{k-j}{k}w_j^{(k-1)}x_{k-1},
$$

$$
c_j^{(k)} = \frac{j}{k}c_{j-1}^{(k-1)} + \frac{k-j}{k}c_j^{(k-1)} + w_j^{(k)}f[x_0, \ldots, x_k],
$$

*para* $j = 0, \ldots, k$*, donde usamos la convención* $c_{-1}^{(k-1)} = w_{-1}^{(k-1)} = 0$ *y* $c_k^{(k-1)} = w_k^{(k-1)} = 0$*. Entonces,* $\{w_j^{(k)}\}_{j=0}^k$ *son los puntos de control de* $w_k$ *y* $\{c_j^{(k)}\}_{j=0}^k$ *son los puntos de control de* $p_k$*.*

*Prueba.* El caso $k = 0$ se satisface trivialmente. Procedemos por inducción y suponemos que las formas de Bernstein de los polinomios, $p_{k-1}$ y $w_{k-1}$ están dadas por

$$
w_{k-1}(x) = \sum_{j=0}^{k-1} w_j^{(k-1)} B_j^{k-1}(x) \quad \text{y} \quad p_{k-1}(x) = \sum_{j=0}^{k-1} c_j^{(k-1)} B_j^{k-1}(x).
$$

Primero, derivamos los coeficientes de Bernstein del polinomio $w_k$ de grado $k$ de la siguiente manera:

$$
w_k(x) = (x-x_k)\sum_{j=0}^{k-1} w_j^{(k-1)} B_j^{k-1}(x)
$$

$$
= (x(1-x_{k-1}) - x_{k-1}(1-x))\sum_{j=0}^{k-1} w_j^{(k-1)} B_j^{k-1}(x).
$$

Usando (2.5) con $n = k-1$ concluimos que los coeficientes de Bernstein de $w_k$ están dados por

$$
(2.12) \quad w_j^{(k)} = \frac{j}{k}w_{j-1}^{(k-1)}(1-x_{k-1}) - \frac{k-j}{k}w_j^{(k-1)}x_{k-1}.
$$

Segundo, usamos la propiedad de elevación de grado

$$
(2.13) \quad B_k^{n-1} = \frac{n-k}{n}B_k^n + \frac{k+1}{n}B_{k+1}^n, \quad k = 0, \ldots, n-1,
$$

para escribir el polinomio $p_{k-1}$ de grado $k-1$, en términos de la base de Bernstein de polinomios de grado $k$.

$$
(2.14) \quad p_{k-1}(x) = \sum_{j=0}^k c_j^{(k-1)} B_j^{k-1}(x) = \sum_{j=0}^k \left(\frac{j}{k}c_{j-1}^{(k-1)} + \frac{k-j}{k}c_j^{(k-1)}\right) B_j^k(x)
$$

donde nuevamente usamos la convención $c_{-1}^{(k-1)} = 0$ y $c_k^{(k-1)} = 0$. Observamos de (2.11) que $p_k(x) = p_{k-1}(x) + w_k(x)f[x_0, \ldots, x_k]$. Por lo tanto, por (2.14) tenemos que

$$
c_j^{(k)} = \frac{j}{k}c_{j-1}^{(k-1)} + \frac{k-j}{k}c_j^{(k-1)} + w_j^{(k)}f[x_0, \ldots, x_k], \quad j = 0, \ldots, k
$$

son los puntos de control de $p_k$. $\square$

El Algoritmo 1 proporciona una implementación del resultado obtenido en el Teorema 2.2, en el que la simplicidad del procedimiento es inmediatamente aparente junto con una complejidad total de $O(n^2)$:

---

**Algoritmo 1:** NewtonBernstein($\{x_j\}_{j=0}^n, \{f_j\}_{j=0}^n$)

**Entrada:** Nodos de interpolación y datos $\{x_j\}_{j=0}^n, \{f_j\}_{j=0}^n$

**Salida:** Puntos de control $\{c_j\}_{j=0}^n$

```
1  c₀ ← f₀
2  w₀ ← 1
3  for s ← 1 to n do
4      for k ← n down to s do
5          fₖ ← (fₖ - fₖ₋₁)/(xₖ - xₖ₋ₛ)    // Diferencias divididas
6      end
7      for k ← s down to 1 do
8          wₖ ← (k/s)wₖ₋₁(1 - xₛ₋₁) - (1 - k/s)wₖxₛ₋₁
9          cₖ ← (k/s)cₖ₋₁ + (1 - k/s)cₖ + fₛwₖ
10     end
11     w₀ ← -w₀xₛ₋₁
12     c₀ ← c₀ + fₛw₀
13 end
14 return {cⱼ}ⁿⱼ₌₀
```

---

Los lectores que hayan estudiado la derivación del algoritmo de Marco-Martínez [18] para resolver el mismo problema, pueden sorprenderse por la relativa facilidad con la que se deriva el algoritmo Newton-Bernstein. La complejidad de ambos algoritmos es $O(n^2)$. En la siguiente sección, comparamos el rendimiento del algoritmo Newton-Bernstein y el algoritmo Marco-Martínez más sofisticado.

### 2.3. Ejemplos numéricos

En esta sección comparamos el rendimiento del Algoritmo 1 (NewtonBernstein) con el algoritmo de Marco-Martínez [18] (MM) y el comando `\` en Matlab para tres ejemplos. Los Ejemplos 2.1 y 2.2 se toman directamente de [18]. Las soluciones verdaderas de todos estos problemas se calculan utilizando el comando `linsolve` en Maple 18. En cada caso, presentamos el error relativo definido por

$$
(2.15) \quad \text{Error relativo} = \frac{|c_{\text{exact}} - c_{\text{approx}}|_2}{|c_{\text{exact}}|_2},
$$

donde $c_{\text{exact}}$ y $c_{\text{approx}}$ denotan los puntos de control de Bézier exactos y aproximados.

**Ejemplo 2.1.** Sea $n = 15$ y elija nodos distribuidos uniformemente dados por $x_i = (i+1)/(17)$, $i = 0, \ldots, n$. Sea $A$ la matriz de Bernstein-Vandermonde de grado $n$ generada por un conjunto dado de nodos de interpolación $\{x_j\}_{j=0}^n$,

$$
(2.16) \quad a_{i,j} = b_i^n(x_j) = \binom{n}{i}(1-x_j)^{n-i}x_j^i, \quad i, j = 0, \ldots, n.
$$

En este caso, el número de condición de la matriz de Bernstein-Vandermonde es $\kappa(A) = 2.3 \times 10^6$. Los lados derechos $f_1$, $f_2$ y $f_3$ están dados por

$$
(f_1)_j = (1-x_j)^n,
$$

$$
f_2 = (2, 1, 2, 3, -1, 0, 1, -2, 4, 1, 1, -3, 0, -1, -1, 2)^T,
$$

$$
f_3 = (1, -2, 1, -1, 3, -1, 2, -1, 4, -1, 2, -1, 1, -3, 1, -4)^T.
$$

Los errores relativos para cada algoritmo se muestran en la Tabla 1.

| $f_i$ | $A \backslash f_i$ | NewtonBernstein | MM |
| --- | --- | --- | --- |
| $f_1$ | 7.2e-13 | 7.9e-14 | 9.2e-13 |
| $f_2$ | 7.1e-11 | 5.9e-16 | 1.0e-15 |
| $f_3$ | 7.1e-11 | 5.2e-16 | 4.9e-16 |

**Tabla 1:** Ejemplo 2.1: Errores relativos en la norma $L^2$

Los resultados en la Tabla 1 indican que los algoritmos Newton-Bernstein y Marco-Martínez ofrecen estabilidad y precisión comparables, mientras que el solucionador `\` se desempeña mal.

---

†División de Matemáticas Aplicadas, Brown University, Providence, RI 02912, USA ([mark_ainsworth@brown.edu](mailto:mark_ainsworth@brown.edu), [manuel_sanchez_uribe@brown.edu](mailto:manuel_sanchez_uribe@brown.edu)). MA agradece el apoyo parcial de este trabajo bajo el contrato AFOSR FA9550-12-1-0399.

Los resultados en la Tabla 1 indican que los algoritmos Newton-Bernstein y Marco-Martínez ofrecen estabilidad y precisión comparables, mientras que el solucionador `\` se desempeña mal.

**Ejemplo 2.2.** Sea $n = 15$ y $A$ la matriz de Bernstein-Vandermonde generada por los datos

$$
\mathbf{x} = \left(\frac{1}{18}, \frac{1}{16}, \frac{1}{14}, \frac{1}{12}, \frac{1}{10}, \frac{1}{8}, \frac{1}{6}, \frac{1}{4}, \frac{11}{20}, \frac{19}{34}, \frac{17}{30}, \frac{15}{26}, \frac{11}{18}, \frac{9}{14}, \frac{7}{10}, \frac{5}{6}\right)^T.
$$

El número de condición de la matriz de Bernstein-Vandermonde es $\kappa(A) = 3.5 \times 10^9$. Consideremos la descomposición en valores singulares de la matriz de Bernstein-Vandermonde $A = U\Sigma V^T$. Resolveremos los sistemas lineales $A\mathbf{c} = f_j$, con $f_j = u_j$, $j = 0, \ldots, n$, donde $u_j$ denota la $j$-ésima columna de $U$, los vectores singulares izquierdos de $A$. Los errores relativos para cada algoritmo se muestran en la Tabla 2.

Este ejemplo ilustra el *buen condicionamiento efectivo* introducido por Chan y Foulser en [7]. En particular, la prueba confirma que el algoritmo Newton-Bernstein aumenta en precisión a medida que disminuye el número de Chan-Foulser, que es el mismo comportamiento (positivo) exhibido por el algoritmo de Marco-Martínez.

| $f_i$ | $\gamma(A, f_i)$ | $A \backslash f_i$ | NewtonBernstein | MM |
| --- | --- | --- | --- | --- |
| $f_1$ | 3.5e+09 | 3.3e-07 | 1.9e-08 | 3.1e-07 |
| $f_2$ | 2.6e+09 | 1.1e-07 | 6.2e-08 | 2.1e-08 |
| $f_3$ | 1.3e+09 | 8.4e-09 | 5.6e-09 | 2.7e-08 |
| $f_4$ | 1.2e+09 | 2.1e-08 | 1.1e-08 | 1.4e-08 |
| $f_5$ | 5.3e+08 | 3.8e-08 | 2.6e-09 | 1.7e-08 |
| $f_6$ | 4.0e+08 | 4.3e-08 | 1.0e-08 | 2.7e-09 |
| $f_7$ | 1.1e+08 | 3.7e-08 | 1.8e-09 | 7.4e-09 |
| $f_8$ | 5.8e+07 | 3.5e-08 | 6.5e-10 | 2.5e-09 |
| $f_9$ | 1.1e+07 | 1.5e-08 | 8.7e-10 | 3.2e-10 |
| $f_{10}$ | 3.7e+06 | 1.2e-08 | 1.5e-10 | 3.3e-10 |
| $f_{11}$ | 4.8e+05 | 1.4e-08 | 4.5e-12 | 3.6e-12 |
| $f_{12}$ | 1.2e+05 | 3.5e-09 | 1.3e-11 | 1.7e-11 |
| $f_{13}$ | 6.2e+03 | 8.2e-09 | 3.0e-12 | 2.3e-12 |
| $f_{14}$ | 9.3e+02 | 1.1e-08 | 7.6e-13 | 7.8e-13 |
| $f_{15}$ | 1.4e+01 | 1.2e-08 | 4.2e-14 | 4.2e-14 |
| $f_{16}$ | 1 | 5.0e-09 | 7.1e-15 | 7.9e-15 |

**Tabla 2:** Ejemplo 2.2: Errores relativos en la norma $L^2$

**Ejemplo 2.3.** Sea $n = 25$ y tome los nodos de interpolación como los ceros del polinomio de Chebyshev de primera especie. En este caso, el número de condición de la matriz de Bernstein-Vandermonde es $\kappa(A) = 2.1 \times 10^7$. Los lados derechos se toman como $f_1$, $f_2$ y $f_3$ dados por

$$
(f_1)_j = (1-x_j)^n \quad \text{para } j = 1, \ldots, 25,
$$

$$
f_2 = (-3, -1, 2, -1, 2, -1, 1, -3, 2, -3, 1, 2, -1, -2, 1, -2, -1, -2, 1, -2, 3, -2, -3, 2, 1, -2)^T,
$$

$$
f_3 = (-1, 2, 1, -1, -2, -3, 2, 3, -2, -1, 2, 1, 3, -2, 1, -1, -1, 2, -2, -3, 1, -1, 1, -3, 2, -1)^T.
$$

Los errores relativos para cada algoritmo se muestran en la Tabla 3.

| $f_i$ | $A \backslash f_i$ | NewtonBernsteinLeja | NewtonBernstein | MM |
| --- | --- | --- | --- | --- |
| $f_1$ | 7.7e-11 | 4.2e-11 | 4.2e-11 | 1.0e-09 |
| $f_2$ | 1.1e-10 | 3.2e-16 | 7.9e-13 | 1.4e-15 |
| $f_3$ | 1.1e-10 | 4.8e-16 | 1.6e-13 | 1.6e-15 |

**Tabla 3:** Ejemplo 2.3: Errores relativos en la norma $L^2$

Es bien sabido que puede haber ventajas al reordenar los nodos de interpolación. Una característica del Algoritmo Newton-Bernstein (no compartida por el Algoritmo Marco-Martínez (MM)) es la flexibilidad para reordenar los nodos de interpolación. La Tabla 3 compara los errores relativos obtenidos para los problemas de interpolación usando el orden ascendente (NewtonBernstein) y usando el orden de Leja (NewtonBernsteinLeja), ver [14, 20]. En este ejemplo, el orden de Leja de los nodos de interpolación produce mejores resultados y, al igual que en el ejemplo anterior, la precisión de nuestros algoritmos aumenta con el patrón de signo alternante del lado derecho.

---

## 3. Interpolación polinomial de producto tensorial

En esta sección mostramos brevemente cómo el Algoritmo Newton-Bernstein 1 puede usarse para interpolar en rejillas de producto tensorial en dimensiones superiores. Consideremos el caso bidimensional. Sean $\{x_i\}_{i=0}^n \subseteq [0,1]$ y $\{y_j\}_{j=0}^m \subseteq [0,1]$ nodos dados y sean $\{f_{i,j}\}_{i,j=0}^{n,m}$ datos dados. El problema de interpolación polinomial consiste en encontrar el polinomio $p \in \mathbb{P}^n([0,1]) \times \mathbb{P}^m([0,1])$ que satisfaga las condiciones:

$$
(3.1) \quad p(x_i, y_j) = f_{i,j}, \quad i = 0, \ldots, n, \quad j = 0, \ldots, m.
$$

El problema de interpolación de Bernstein asociado consiste en encontrar los puntos de control $\{c_{k,\ell}\}_{k=0, \ell=0}^{n,m}$ tales que el polinomio de Bernstein de producto tensorial

$$
(3.2) \quad p(x, y) = \sum_{\ell=0}^m \sum_{k=0}^n c_{k,\ell} B_k^n(x) B_\ell^m(y), \quad (x, y) \in [0,1]^2
$$

satisfaga (3.1).

La naturaleza de producto tensorial del problema significa que podemos explotar el algoritmo Newton-Bernstein para el caso univariado para resolver el problema (3.2). La idea básica es:

**a)** primero construir los puntos de control para el interpolante de Bernstein univariado $p^{(j)}$ en las líneas $y = y_j$ para cada $j$, es decir, para cada $j = 0, \ldots, n$:

$$
(3.3) \quad p^{(j)}(x) = \sum_{k=0}^n c_k^{(j)} B_k^n(x); \quad p^{(j)}(x_i) = f_{i,j}, \quad i = 0, \ldots, n;
$$

y, **b)** resolver un problema de interpolación univariada para la variable $y$ en el que los datos son los polinomios univariados obtenidos en el paso a), es decir, encontrar el polinomio univariado $p$ que satisfaga

$$
(3.4) \quad p(x, y_j) = p^{(j)}(x), \quad j = 0, \ldots, m.
$$

El problema en el paso b) no es más que un problema de interpolación univariada con la única diferencia de que los datos ahora tienen valor polinomial. La derivación del algoritmo Newton-Bernstein presentado en la sección anterior se aplica igualmente bien al problema más general de interpolar valores de un espacio vectorial $\mathcal{X}$. En particular, elegir $\mathcal{X}$ como polinomios muestra que el Algoritmo Newton-Bernstein 1 puede aplicarse en cada una de las etapas a) y b). Esta idea constituye la base del Algoritmo 2.

---

**Algoritmo 2:** TensorProduct2D($\{x_i\}_{i=0}^n, \{y_j\}_{j=0}^m, \{f_{i,j}\}_{i,j=0}^{n,m}$)

**Entrada:** Nodos de interpolación y datos $\{x_i\}_{i=0}^n, \{y_j\}_{j=0}^m, \{f_{i,j}\}_{i,j=0}^{n,m}$

**Salida:** Puntos de control $\{c_{i,j}\}_{i,j=0}^{n,m}$

```
1  for j ← 0 to m do
2      {c̃ₖ⁽ʲ⁾}ᵏ₌₀ⁿ ← NewtonBernstein({xᵢ}ⁿᵢ₌₀, {fᵢ,ⱼ}ⁿᵢ₌₀)
3  end
4  for i ← 0 to n do
5      {cᵢ,ⱼ}ᵐⱼ₌₀ ← NewtonBernstein({yⱼ}ᵐⱼ₌₀, {c̃ᵢ⁽ʲ⁾}ᵐⱼ₌₀)
6  end
7  return {cᵢ,ⱼ}ⁿ'ᵐᵢ,ⱼ₌₀
```

---

La idea básica utilizada en el algoritmo bidimensional se extiende fácilmente a dimensiones superiores, lo que resulta en el Algoritmo 3 que calcula la solución de la versión tridimensional del problema de interpolación (3.2).

---

**Algoritmo 3:** TensorProduct3D($\{x_i\}_{i=0}^n, \{y_j\}_{j=0}^m, \{z_k\}_{k=0}^l, \{f_{i,j,k}\}_{i,j,k=0}^{n,m,l}$)

**Entrada:** Nodos de interpolación y datos $\{x_i\}_{i=0}^n, \{y_j\}_{j=0}^m, \{z_k\}_{k=0}^l, \{f_{i,j,k}\}_{i,j,k=0}^{n,m,l}$

**Salida:** Puntos de control $\{c_{i,j,k}\}_{i,j,k=0}^{n,m,l}$

```
1  for j ← 0 to m do
2      {c̃ᵢ,ⱼ,ₖ}ⁿᵢ₌₀ ← NewtonBernstein({xᵢ}ⁿᵢ₌₀, {fᵢ,ⱼ,ₖ}ⁿᵢ₌₀)
3  end
4  for i ← 0 to n do
5      {ĉᵢ,ⱼ,ₖ}ᵐⱼ₌₀ ← NewtonBernstein({yⱼ}ᵐⱼ₌₀, {c̃ᵢ,ⱼ,ₖ}ᵐⱼ₌₀)
6  end
7  for i ← 0 to n do
8      {cᵢ,ⱼ,ₖ}ˡₖ₌₀ ← NewtonBernstein({zₖ}ˡₖ₌₀, {ĉᵢ,ⱼ,ₖ}ˡₖ₌₀)
9  end
10 return {cᵢ,ⱼ,ₖ}ⁿ'ᵐ'ˡᵢ,ⱼ,ₖ₌₀
```

---

### 3.1. Ejemplos numéricos: Producto tensorial

En esta sección consideramos ejemplos de los problemas de interpolación de Bernstein-Bézier bidimensional y tridimensional, ilustrando el rendimiento de los Algoritmos 2 y 3.

**Ejemplo 3.1.** Considere $n = 15$ y el problema de interpolación bidimensional con rejilla inducida por los siguientes nodos

$$
x_i = \frac{i+1}{n+2}, \quad y_j = \frac{j+1}{n+3}, \quad i, j = 0, \ldots, n.
$$

Tenga en cuenta que en este caso el número de condición de la matriz de Bernstein-Vandermonde bidimensional $A_2$ (tamaño $256 \times 256$) es $\kappa(A_2) = 1.4 \times 10^{13}$. Como vectores de carga consideramos $f_1$ y $f_2$ generados aleatoriamente, tomando valores enteros entre $-3$ y $3$ para cada componente. Los errores relativos se muestran en la Tabla 4.

| $f_i$ | $A_2 \backslash f_i$ | NewtonBernstein | $A \backslash f_i$ MM |
| --- | --- | --- | --- |
| $f_1$ | 4.2e-5 | 2.5e-15 | 2.3e-11 |
| $f_2$ | 2.6e-5 | 9.7e-16 | 3.5e-11 |

**Tabla 4:** Errores relativos en la norma $L^2$ para soluciones del Ejemplo 3.1 usando Matlab `\` y TensorProduct2D. También se presentan los resultados obtenidos cuando NewtonBernstein es reemplazado en TensorProduct2D por los solucionadores univariados `\` y MM.

Observe la precisión significativamente mayor del algoritmo Newton-Bernstein en comparación con los resultados de `\`.

**Ejemplo 3.2.** Considere $n = 10$ y el problema de interpolación tridimensional con rejilla inducida para los siguientes nodos

$$
x_i = \frac{i+1}{n+2}, \quad y_j = \frac{j+1}{n+3}, \quad z_k = \frac{k+2}{n+4}, \quad i, j = 0, \ldots, n.
$$

Tenga en cuenta que en este caso el número de condición de la matriz de Bernstein-Vandermonde tridimensional (tamaño $1331 \times 1331$) es $\kappa(A_3) = 7.6 \times 10^{13}$. Como vectores de carga consideramos $f_1$ y $f_2$ generados aleatoriamente, tomando valores enteros entre $-3$ y $3$ para cada componente. Los errores relativos se muestran en la Tabla 5.

| $f_i$ | $A_3 \backslash f_i$ | NewtonBernstein | $A \backslash f_i$ MM |
| --- | --- | --- | --- |
| $f_1$ | 8.4e-6 | 6.0e-16 | 2.1e-12 |
| $f_2$ | 8.2e-6 | 5.2e-16 | 2.2e-12 |

**Tabla 5:** Errores relativos en la norma $L^2$ para soluciones del Ejemplo 3.2 usando Matlab `\` y TensorProduct3D. También se presentan los resultados obtenidos cuando NewtonBernstein es reemplazado en TensorProduct3D por los solucionadores univariados `\` y MM.

El caso tridimensional también muestra una gran precisión del algoritmo Newton-Bernstein en comparación con el solucionador de Matlab, ver Tabla 5.

---

†División de Matemáticas Aplicadas, Brown University

El caso tridimensional también muestra una gran precisión del algoritmo Newton-Bernstein en comparación con el solucionador de Matlab, ver Tabla 5.

---

## 4. Puntos de control para la interpolación polinomial en un *símplex*

El cálculo de los puntos de control del interpolante de Lagrange en un *símplex* en $\mathbb{R}^d$, $d \in \mathbb{N}$ es bastante más problemático que el caso de producto tensorial. Sin embargo, en esta sección, mostramos cómo el algoritmo univariado Newton-Bernstein puede generalizarse para resolver el problema.

### 4.1. Preliminares

Para $n \in \mathbb{N}$ definimos el conjunto de índices $I_d^n = \{\alpha = (\alpha_1, \ldots, \alpha_{d+1}) \in \mathbb{Z}_*^{d+1} : |\alpha| = n\}$ donde $|\alpha| = \sum_{j=1}^{d+1} \alpha_j$, $\mathbb{Z}_* = \{0\} \cup \mathbb{N}$ y $|I_d^n| = \text{card}(I_d^n) = \binom{n+d}{d}$.

Para $n, m \in \mathbb{N}$, $\alpha \in I_d^n$, $\beta \in I_d^m$ y $\lambda \in \mathbb{R}^{d+1}$, definimos

$$
\binom{\alpha}{\beta} = \prod_{j=1}^{d+1} \binom{\alpha_k}{\beta_k}, \quad \binom{n}{\alpha} = n! \left(\prod_{j=1}^{d+1} \alpha_j!\right)^{-1}, \quad \lambda^\alpha = \prod_{j=1}^{d+1} \lambda_j^{\alpha_j}.
$$

Sea $T = \text{conv}\{v_1, \ldots, v_{d+1}\}$ un $d$-*símplex* no degenerado en $\mathbb{R}^d$. La siguiente propiedad de los *símplices* no degenerados será útil [1]:

**Lema 4.1.** *Las siguientes condiciones son equivalentes:*

1. $*T$ es un $d$-símplex no degenerado;*
2. *para todo $x \in T$, existe un conjunto único de escalares no negativos* $\lambda_1, \lambda_2, \ldots, \lambda_{d+1}$ *tal que* $\sum_{\ell=1}^{d+1} \lambda_\ell v_\ell = x$ *y $\sum_{\ell=1}^{d+1} \lambda_\ell = 1$.*

Sea $\mathcal{D}_d^n$ el conjunto de puntos de dominio de $T$ definidos por $x_\alpha = \frac{1}{n}\sum_{k=1}^{d+1} \alpha_k v_k$, $\alpha \in I_d^n$, donde $\lambda \in \mathbb{R}^{d+1}$ se definen como en el Lema 4.1. Los polinomios de Bernstein de grado $n \in \mathbb{Z}^+$ asociados con el *símplex* $T$ se definen por

$$
(4.1) \quad B_{\alpha}^{T,n}(x) = B_\alpha^n(x) = \binom{n}{\alpha}\lambda(x)^\alpha, \quad \alpha \in I_d^n
$$

y satisfacen

$$
(4.2) \quad B_\alpha^m B_\beta^n = \binom{\alpha+\beta}{\alpha}\binom{m+n}{n}^{-1} B_{\alpha+\beta}^{m+n} \quad \alpha \in I_d^m, \beta \in I_d^n.
$$

El problema de interpolación polinomial de Bernstein en el *símplex* $T$ se lee: dado un conjunto de nodos de interpolación distintos $\{x_j\}_{j=1}^{|I_d^n|}$ y datos de interpolación $\{f_j\}_{j=1}^{|I_d^n|}$, encontrar puntos de control $\{c_\alpha\}_{\alpha \in I_d^n}$ tales que

$$
(4.3) \quad p(x) = \sum_{\alpha \in I_d^n} c_\alpha B_\alpha^n(x) : \quad p(x_j) = f_j, \quad \text{para } j = 1, \ldots, |I_d^n|.
$$

### 4.2. Caso bidimensional

El problema de interpolación polinomial en dimensiones superiores requiere que los nodos de interpolación que aparecen en (4.3) satisfagan condiciones adicionales más allá de ser simplemente distintos para que el problema de interpolación esté bien planteado [8]:

**Condición de Solubilidad (S):** *Existen líneas distintas* $\gamma_0, \gamma_1, \ldots, \gamma_n$ *tales que los nodos de interpolación pueden ser particionados en conjuntos (no superpuestos)* $A_n, A_{n-1}, \ldots, A_0$ *donde* $A_j$ *contiene* $j+1$ *nodos localizados en* $\gamma_j \setminus (\gamma_{j+1} \cup \ldots \cup \gamma_n)$*.*

Asumiremos que la Condición (S) se satisface en todo momento. En particular, la Condición (S) implica que existe una línea $\gamma_n$ en la que se encuentran $n+1$ nodos de interpolación distintos. Esto significa que existe un polinomio (no único) $q_n \in \mathbb{P}^n(T)$ que satisface el problema de interpolación polinomial univariada en la línea $\gamma_n$:

$$
(4.4) \quad q_n(x_i) = f_i \quad \forall x_i \in A_n.
$$

Igualmente, la Condición (S) implica que la línea $\gamma_{n-1}$ contiene $n$ nodos de interpolación distintos, ninguno de los cuales se encuentra en $\gamma_n$, lo que significa que el problema de interpolación polinomial univariada para estos nodos está bien planteado. Los datos para este problema de interpolación se eligen de la siguiente manera. Sea $\Gamma_n$ un polinomio afín que describe la línea $\gamma_n$, es decir, $x \in \gamma_n$ si y solo si $\Gamma_n(x) = 0$. Existe un polinomio (no único) $q_{n-1} \in \mathbb{P}^{n-1}(T)$ que satisface el siguiente problema de interpolación polinomial univariada en la línea $\gamma_{n-1}$:

$$
(4.5) \quad q_{n-1}(x_i) = \frac{f_i - q_n(x_i)\Gamma_n(x_i)}{\Gamma_n(x_i)} \quad \forall x_i \in A_{n-1}.
$$

Obsérvese que estos datos están bien definidos gracias a la Condición (S). La no unicidad del polinomio se deriva del hecho de que si bien los valores de $q_n$ en la línea $\gamma_n$ están definidos de forma única, hay muchas maneras de extender $q_n$ al *símplex*—un enfoque canónico para definir la extensión se presentará en la Sección 4.2.1.

Los argumentos anteriores pueden aplicarse repetidamente para definir una secuencia de polinomios $q_j \in \mathbb{P}^j(T)$ que satisface un problema de interpolación univariada en la línea $\gamma_j$:

$$
(4.6) \quad q_j(x_i) = \frac{f_i - \sum_{k=j+1}^n q_k(x_i)\prod_{l=k+1}^n \Gamma_l(x_i)}{\prod_{l=j+1}^n \Gamma_l(x_i)} \quad \forall x_i \in A_j
$$

donde $\Gamma_k$ es un polinomio afín que satisface $x \in \gamma_k$ si y solo si $\Gamma_k(x) = 0$, $k = 0, \ldots, n$.

El siguiente resultado presenta una construcción general para la solución del problema de interpolación completo (4.3) en términos de soluciones $q_j$ de problemas de interpolación univariada en las líneas $\gamma_j$:

**Teorema 4.2.** *Sea* $\{q_j\}_{j=0}^n$ *definido como se indicó anteriormente y defina* $p \in \mathbb{P}^n(T)$ *como*

$$
(4.7) \quad p(x) = \sum_{j=0}^n q_j(x) \prod_{i=j+1}^n \Gamma_i(x), \quad x \in T.
$$

*Entonces* $p$ *resuelve el problema de interpolación (4.3).*

*Prueba.* El polinomio $p$ definido en (4.7) claramente pertenece a $\mathbb{P}^n(T)$. Sea $j \in \{0, \ldots, n\}$ y $x_i \in A_j$, $j \in \{0, \ldots, n\}$. Insertar $x_i$ en la fórmula (4.7) da

$$
p(x_i) = \sum_{k=0}^n q_k(x_i)\prod_{l=k+1}^n \Gamma_l(x_i) = \sum_{k=j}^n q_k(x_i)\prod_{l=k+1}^n \Gamma_l(x_i)
$$

$$
= q_j(x_i)\prod_{l=j+1}^n \Gamma_l(x_i) + \sum_{k=j+1}^n q_k(x_i)\prod_{l=k+1}^n \Gamma_l(x_i),
$$

donde hemos usado el hecho de que $\Gamma_j(x_i) = 0$ debido a la Condición (S). El resultado se sigue gracias a (4.6). $\square$

El Teorema 4.2 reduce la solución del problema de interpolación multivariada a la solución de una secuencia de problemas de interpolación univariada. Esta característica puede utilizarse junto con el algoritmo Newton-Bernstein univariado para construir un algoritmo para resolver el problema de interpolación multivariada de Bernstein (4.3) de la siguiente manera:

---

**Algoritmo 4:** NewtonBernstein2D($\{x_j, f_j\}_{j=0}^{|I_2^n|}$)

**Entrada:** Nodos de interpolación y datos $\{x_j, f_j\}_{j=0}^{|I_2^n|}$

**Salida:** Puntos de control $c_p$

```
1  Initialise cₚ
2  for j ← n down to 1 do
3      Gⱼ ← BBAffine(Aⱼ)                      // Forma BB de Γⱼ
4      [z₁, z₂, κ] ← GcapT(Gⱼ)                // Γⱼ ∩ T
5      Ā̄ⱼ ← Transform1D(Aⱼ, z₁, z₂)           // Mapear [z₁,z₂] → [0,1]
6      c^γⱼ ← NewtonBernstein(Ā̄ⱼ)
7      c^qⱼ ← BBExtension(c^γⱼ, z₁, z₂, κ)   // qⱼ resuelve (4.6)
8      a ← c^qⱼ
        // Calcula la forma BB de qⱼ ∏ᵢ₌ⱼ₊₁ⁿ Γᵢ
9      for i ← j+1 to n do
10         a ← BBProduct(a, Gᵢ)
11     end
12     cₚ ← cₚ + a
13     for i ← 1 to |Iⱼ₋₁²| do              // Diferencias divididas
14         fᵢ ← (fᵢ - DeCasteljau(c^qⱼ, xᵢ)) / DeCasteljau(Gⱼ, xᵢ)
15     end
16 end
17 return cₚ
```

---

El Algoritmo 4 llama a cinco subrutinas. La subrutina **DeCasteljau** se refiere al conocido algoritmo de de Casteljau [10] para la evaluación de un polinomio escrito en forma de Bernstein a un costo de $O(n^{d+1})$ operaciones en $d$-dimensiones. Las cuatro subrutinas restantes son el tema de las siguientes secciones. Resultará que la complejidad general del Algoritmo 4 es $O(n^{d+1})$, donde $d = 2$ en el caso actual. Un ejemplo numérico que ilustra el rendimiento del algoritmo se presenta en la Sección 4.3.

---

**Algoritmo 5:** BBAffine($A_j$)

**Entrada:** Nodos de interpolación y datos $A_j$

**Salida:** Forma BB de $Gamma$, $G$

```
1  Compute coefficients a, b, c of line ax + by + c = 0 
   fitting the interpolation nodes Aⱼ
2  d = max{|c|, |a+c|, |b+c|}
3  G₍₁,₀,₀₎ = c/d
4  G₍₀,₁,₀₎ = (a+c)/d
5  G₍₀,₀,₁₎ = (b+c)/d
6  return G
```

---

### 4.2.1. BBExtension

La subrutina BBExtension extiende el dominio de una solución del problema de interpolación univariada (4.6) desde la línea $\gamma_j$ a todo el *símplex* $T$. Para lograr esta tarea, es necesario obtener puntos $z_1$ y $z_2$ que satisfagan $\gamma_j \cap T = \text{conv}\{z_1, z_2\}$. En términos generales, $z_1$ y $z_2$ son los puntos en los que la línea $\gamma_j$ interseca el contorno del *símplex*. Sin pérdida de generalidad, suponga que $\gamma_j$ separa los vértices de $T$ en conjuntos $\{v_1, v_2\}$ y $\{v_3\}$ tales que $\lambda_1(z_1) > 0$, $\lambda_1(z_2) = 0$ y $\lambda_2(z_1) = 0$, $\lambda_2(z_2) > 0$, donde $\lambda_1$ y $\lambda_2$ son las coordenadas baricéntricas en el *símplex* $T$.

En particular, $\text{conv}\{z_1, z_2\}$ es un 1-*símplex* no degenerado y, por lo tanto, en vista del Lema 4.1, podemos definir coordenadas baricéntricas en el 1-*símplex* $\text{conv}\{z_1, z_2\}$. En vista de la teoría presentada en la Sección 2.2, podemos encontrar puntos de control $\{c_\alpha^{\gamma_j}\}$ del interpolante polinomial de Bernstein univariado de los datos $A_j$ en $\text{conv}\{z_1, z_2\}$. Estos puntos de control corresponden a la forma de Bernstein del interpolante relativa a las coordenadas baricéntricas en el 1-*símplex* $\text{conv}\{z_1, z_2\}$. Por lo tanto, solo queda transformar estos puntos de control a puntos de control para las coordenadas baricéntricas en el *símplex* $T$, extendiendo así implícitamente el polinomio univariado a todo el *símplex*:

**Lema 4.3.** *Sea* $\{c_\alpha^{\gamma_j}\}_{\alpha \in I_1^j}$ *los puntos de control de un polinomio* $q^{\gamma_j} \in \mathbb{P}^j(\text{conv}\{z_1, z_2\})$ *definido en el 1-*símplex **$\text{conv}\{z_1, z_2\}$*. Defina los puntos de control* $\{c_\alpha^T\}_{\alpha \in I_2^j}$ *de un polinomio* $q_T \in \mathbb{P}^j(T)$ *en el* símplex **$T$ *por la regla: para* $(\alpha_1, \alpha_2, \alpha_3) \in I_2^j$

$$
(4.8) \quad c_{(\alpha_1,\alpha_2,\alpha_3)}^T = \begin{cases} c_{(\alpha_1,\alpha_2)}^{\gamma_j}(\lambda_1(z_1))^{-\alpha_1}(\lambda_2(z_2))^{-\alpha_2}, & \text{si } \alpha_3 = 0; \\ 0, & \text{de lo contrario}. \end{cases}
$$

*Entonces,* $q_T \in \mathbb{P}^j(T)$ *coincide con* $q^{\gamma_j}$ *en* $\gamma_j$*.*

*Prueba.* Considere la forma de Bernstein de $q_T$ y aplique la definición (4.8)

$$
q_T(x) = \sum_{\alpha \in I_2^j : \alpha_3=0} c_\alpha^T B_{T,\alpha}^j(x)
$$

$$
(4.9) \quad = \sum_{\alpha \in I_2^j, \alpha_3=0} c_{(\alpha_1,\alpha_2)}^{\gamma_j}\binom{j}{(\alpha_1, \alpha_2)}\left(\frac{\lambda_1(x)}{\lambda_1(z_1)}\right)^{\alpha_1}\left(\frac{\lambda_2(x)}{\lambda_2(z_2)}\right)^{\alpha_2}, \quad x \in T.
$$

Observe que el factor $\frac{\lambda_1(x)}{\lambda_1(z_1)}$ es lineal y toma valores 1 en $x = z_1$ y 0 en $x = z_2$, y como tal corresponde a las coordenadas baricéntricas en $\text{conv}\{z_1, z_2\}$. La misma consideración se aplica al otro factor en (4.9). Por lo tanto, si $x \in \gamma_j$, entonces

$$
q_T(x) = \sum_{\alpha \in I_1^j} c_\alpha^{\gamma_j} B_\alpha^{\gamma_j,j}(x) = q^{\gamma_j}(x),
$$

y el resultado se sigue. $\square$

El algoritmo para BBExtension correspondiente al Lema 4.3 se presenta en el Algoritmo 6.

---

**Algoritmo 6:** BBExtension($A_j$)

**Entrada:** $c^{\gamma_j}, z_1, z_2, \kappa$

**Salida:** Forma BB del polinomio $q_T$, $c_\alpha^T$

```
1  for α ∈ I₂ʲ do
2      if αₖ = 0 then
3          if κ = 3 then
4              c^T_α ← c^γʲ_(α₁,α₂) λ₁(z₁)^(-α₁) λ₂(z₂)^(-α₂)
5          end
6          if κ = 2 then
7              c^T_α ← c^γʲ_(α₃,α₁) λ₃(z₁)^(-α₃) λ₁(z₁)^(-α₁)
8          end
9          if κ = 1 then
10             c^T_α ← c^γʲ_(α₂,α₃) λ₂(z₁)^(-α₂) λ₃(z₁)^(-α₃)
11         end
12     end
13 end
14 return c^T_α
```

---

### 4.2.2. GcapT

La implementación práctica del Lema 4.3 requiere la identificación de $z_1$ y $z_2$ que satisfagan $\gamma_j \cap T = \text{conv}\{z_1, z_2\}$. Observamos que $\gamma_j$ separa los vértices de $T$ en uno de los siguientes: $\{v_1, v_2\} \cup \{v_3\}$; $\{v_2, v_3\} \cup \{v_1\}$ y $\{v_3, v_1\} \cup \{v_2\}$. Supongamos que el nodo aislado está dado por $v_k$, $k \in \{1, 2, 3\}$. Sea $z$ que denote a $z_1$ o $z_2$, y sean las coordenadas baricéntricas de $z$ dadas por $\lambda_1, \lambda_2$ y $\lambda_3$, entonces

$$
(4.10) \quad \begin{cases} \lambda_k = 0 \\ \sum_{i=1}^3 G_{e_i}\lambda_i = 0 \\ \sum_{i=1}^3 \lambda_i = 1 \end{cases} \quad \text{sujeto a } 0 \leq \lambda_i \leq 1, \text{ para } i = 1, 2, 3
$$

donde $e_k \in I_2^1$ es el multi-índice $(e_k)_i = \delta_{k,i}$ para $i = 1, 2, 3$. La primera condición se cumple porque $z$ está en la arista opuesta al vértice $v_k$, la segunda porque $\Gamma_j(z) = 0$ y la tercera por la propiedad de las coordenadas baricéntricas. Dado que existen solo dos puntos $z$ de este tipo, sabemos que el sistema (4.10) es resoluble precisamente para dos de los casos $k \in \{1, 2, 3\}$. Estas observaciones proporcionan el enfoque simple para la identificación de $z_1$ y $z_2$ implementado en el Algoritmo 7.

---

**Algoritmo 7:** GcapT($G$)

**Entrada:** Puntos de control $G$ de $\Gamma$

**Salida:** Cálculo de los puntos de intersección $z_1, z_2$ y el índice del vértice aislado $\kappa$

```
1  for k = 1, 2, 3 do
2      if (4.10) is solvable for k then
3          z^k_temp = ∑³ᵢ₌₁ vᵢλᵢ
4      else
5          κ = k
6      end
7  end
8  κ₁ = κ + 1 mod 3
9  κ₂ = κ + 2 mod 3
10 z₁ ← z^κ¹_temp
11 z₂ ← z^κ²_temp
12 return z₁, z₂, κ
```

---

### 4.2.3. Transform1D

Para utilizar el algoritmo Newton-Bernstein unidimensional, necesitamos transformar los nodos bidimensionales que se encuentran en $\gamma_j$ a unidimensionales. La subrutina Transform1D transforma los nodos $\{x_j\}$ en el segmento $[z_1, z_2]$ a los nodos $\{x_i\}$ en $[0,1]$. Esto se implementa en el Algoritmo 8.

---

**Algoritmo 8:** Transform1D($A_j$)

**Entrada:** Nodos de interpolación bidimensionales y datos $(x_i, f_i)_{i=1}^{j+1} = A_j$

**Salida:** Datos de interpolación unidimensionales $\bar{A}_j$

```
1  for k = 1 to j+1 do
2      xₖ ← ‖xₖ - z₁‖₂ / ‖z₂ - z₁‖₂
3  end
4  Ā̄ⱼ ← (xᵢ, fᵢ)ʲ⁺¹ᵢ₌₁
5  return Ā̄ⱼ
```

---

### 4.2.4. BBProduct - Forma de Bernstein del producto

Queda por definir un procedimiento para calcular la forma BB del producto $q_j\Gamma$ en términos de la forma BB de $q_j \in \mathbb{P}^j(T)$ y $\Gamma \in \mathbb{P}^1(T)$. Esto se puede lograr mediante la fórmula (4.2). Sean $\{c_\alpha\}_{\alpha \in I_2^j}$ y $\{G_\alpha\}_{\alpha \in I_2^1}$ los puntos de control de $q_j$ y $\Gamma$, respectivamente. Entonces, los puntos de control del producto están dados por 

$$
(4.11) \quad a_\alpha = \sum_{k=1}^3 c_{\alpha-e_k} G_{e_k} \frac{\alpha_k}{j+1}, \quad \alpha \in I_2^{j+1}
$$

donde los términos que involucran multi-índices negativos se tratan como cero. Esta expresión constituye la base del Algoritmo 9, que calcula el producto deseado para el caso general de $d$-dimensiones.

---

**Algoritmo 9:** BBProduct($\{c_\alpha\}_{\alpha \in I_d^j}, \{G_\alpha\}_{\alpha \in I_d^1}$)

**Entrada:** Forma BB de $q \in \mathbb{P}^j(T)$, $\{c_\alpha\}_{\alpha \in I_d^j}$ y Forma BB de $\Gamma \in \mathbb{P}^1(T)$,

**Salida:** Forma BB del producto $q_j\Gamma$, $\{a_\alpha\}_{\alpha \in I_d^{j+1}}$

```
1  for α ∈ I^(j+1)_d do
2      for k ← 1 to d+1 do
3          if αₖ > 0 then
4              aₐ ← aₐ + c_(α-eₖ) G_eₖ (αₖ/(j+1))
5          end
6      end
7  end
8  return {aₐ}_(α∈I^(j+1)_d)
```

---

### 4.3. Ejemplo numérico: *Símplex* 2D

En esta sección consideramos el problema de interpolación de Bernstein-Bézier bidimensional sobre un *símplex* con datos de interpolación no triviales. Comparamos el rendimiento del Algoritmo 4 con el comando `\` en Matlab.

**Ejemplo 4.1.** Consideramos $n = 10$ y una distribución de puntos que satisface la Condición de Solubilidad (S). Los errores relativos se muestran en la Tabla 6.

| $f_i$ | $A \backslash f_i$ | S2D-NewtonBernstein |
| --- | --- | --- |
| $f_1$ | 4.9e-11 | 4.9e-13 |
| $f_2$ | 3.1e-11 | 3.3e-13 |

**Tabla 6:** Ejemplo 4.1: Errores relativos en la norma $L^2$

Observamos en la Tabla 6 la precisión superior del Algoritmo 4 con respecto al solucionador de Matlab.

### 4.4. Generalización a $d$-dimensiones

La extensión del procedimiento descrito en el Algoritmo 4 al caso general no es difícil. En primer lugar, la Condición de Solubilidad (S) se generaliza a $d$-dimensiones de forma recursiva al requerir la existencia de una partición no superpuesta de los datos de interpolación en conjuntos $A_n, A_{n-1}, \ldots, A_0$ de nodos de dimensión apropiada en un *sub-símplex*, aumentada por la condición de solubilidad en cada uno de los $(d-1)$-*sub-símplices* para los problemas de interpolación asociados con los conjuntos $A_j$, $j = n, n-1, \ldots, 0$. La Fórmula (4.7) puede extenderse de manera similar a dimensiones superiores con las funciones $\Gamma_j$ reemplazadas por funciones afines que se anulan en el *sub-símplex* apropiado. En tercer lugar, al utilizar el Algoritmo 4 para resolver los sub-problemas de interpolación de $(d-1)$-dimensiones junto con una extensión obvia del Lema 4.3, obtenemos una subrutina equivalente a BBExtension que extiende el polinomio en el $(d-1)$-*símplex* al $d$-*símplex*. Finalmente, una subrutina que extiende BBAffine a $d$-dimensiones se obtiene fácilmente y la subrutina BBProduct se escribe en términos de $d$-dimensiones.

---

## Referencias

[1] Mark Ainsworth. Pyramid algorithms for Bernstein-Bézier finite elements of high, nonuniform order in any dimension. *SIAM J. Sci. Comput.*, 36(2):A543–A569, 2014.

[2] Mark Ainsworth, Gaelle Andriamaro, and Oleg Davydov. Bernstein-Bézier finite elements of arbitrary order and optimal assembly procedures. *SIAM J. Sci. Comput.*, 33(6):3087–3109, 2011.

[3] Mark Ainsworth, Gaelle Andriamaro, and Oleg Davydov. A Bernstein-Bézier basis for arbitrary order Raviart-Thomas finite elements. *Constr. Approx.*, 41(1):1–22, 2015.

[6] Jean-Paul Berrut and Lloyd N. Trefethen. Barycentric Lagrange interpolation. *SIAM Rev.*, 46(3):501–517 (electronic), 2004.

[7] Tony F. Chan and David E. Foulser. Effectively well-conditioned linear systems. *SIAM J. Sci. Statist. Comput.*, 9(6):963–969, 1988.

[8] Charles K. Chui and Hang-Chin Lai. Vandermonde determinant and Lagrange interpolation in $mathbb{R}^s$. In *Nonlinear and convex analysis (Santa Barbara, Calif., 1985)*, volume 107 of *Lecture Notes in Pure and Appl. Math.*, pages 23–35. Dekker, New York, 1987.

[9] Philip J. Davis. *Interpolation and approximation*. Dover Publications, Inc., New York, 1975.

[10] Gerald Farin. *Curves and Surfaces for CAGD: A Practical Guide*. Morgan Kaufmann Publishers Inc., San Francisco, CA, USA, 5th edition, 2002.

[12] Rida T. Farouki. The Bernstein polynomial basis: a centennial retrospective. *Comput. Aided Geom. Design*, 29(6):379–419, 2012.

[13] M. Gasca and J. M. Peña. Total positivity and Neville elimination. *Linear Algebra Appl.*, 165:25–44, 1992.

[14] Nicholas J. Higham. *Accuracy and stability of numerical algorithms*. Society for Industrial and Applied Mathematics (SIAM), Philadelphia, PA, second edition, 2002.

[15] Robert C. Kirby. Fast simplicial finite element algorithms using Bernstein polynomials. *Numer. Math.*, 117(4):631–652, 2011.

[16] Robert C. Kirby and Kieu Tri Thinh. Fast simplicial quadrature-based finite element operators using Bernstein polynomials. *Numer. Math.*, 121(2):261–279, 2012.

[17] Ming-Jun Lai and Larry L. Schumaker. *Spline functions on triangulations*, volume 110 of *Encyclopedia of Mathematics and its Applications*. Cambridge University Press, Cambridge, 2007.

[18] Ana Marco and José-Javier Martínez. A fast and accurate algorithm for solving Bernstein-Vandermonde linear systems. *Linear Algebra Appl.*, 422(2-3):616–628, 2007.

[19] Peter J. Olver. On multivariate interpolation. *Stud. Appl. Math.*, 116(2):201–240, 2006.

[20] Lothar Reichel. Newton interpolation at Leja points. *BIT*, 30(2):332–346, 1990.

---

†División de Matemáticas Aplicadas, Brown University
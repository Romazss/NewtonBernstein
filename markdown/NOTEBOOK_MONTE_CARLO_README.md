# Monte Carlo Integration with Control Variates Notebook

## Overview

Este notebook (`monte_carlo_control_variate_nb.ipynb`) implementa y reproduce el ejercicio del profesor sobre **técnicas de reducción de varianza para integración Monte Carlo** utilizando interpolantes de Bernstein obtenidos mediante el algoritmo Newton-Bernstein.

## Características Principales

### 1. **Clase `MonteCarloControlVarNB1D`**
Implementación completa de integración Monte Carlo con variables de control:
- Estima integrales usando $I \approx I_p + (b-a) \mathbb{E}[f(U) - p(U)]$
- Compara variance reduction factor: $\eta = \sigma_{raw}^2 / \sigma_{cv}^2$
- Soporta múltiples corridas independientes para análisis estadístico

### 2. **Tres Distribuciones de Nodos**
- **Nodos Uniformes**: Simple y estable
- **Nodos No-Uniformes**: Distribución personalizada
- **Nodos de Chebyshev**: Óptimos para funciones suaves

### 3. **Múltiples Funciones de Prueba**
- $f_1(x) = (1-x)^{15}$, $I = 1/16$
- $f_2(x) = \sin(\pi x)$, $I = 2/\pi$
- $f_3(x) = e^x$, $I = e-1$
- $f_4(x) = 1/(1+x)$, $I = \ln(2)$
- $f_5(x) = \sin(4\pi x)$ (oscilatoria), $I = 0$

## Estructura del Notebook

```
1. Importaciones y configuración
2. Definición de funciones de prueba con integrales analíticas
3. Definición inline de NewtonBernsteinUnivariate (si no se importa)
4. Implementación de MonteCarloControlVarNB1D
5. Generación de datos de interpolación con tres distribuciones de nodos
6. Construcción de interpolantes Newton-Bernstein
7. Estudio de convergencia: MC raw vs Control Variate
8. Análisis de factor de reducción de varianza
9. Visualización de convergencia y eficiencia
10. Visualización de interpolantes
11. Testing con múltiples funciones
12. Conclusiones y resultados
```

## Resultados Esperados

### Variance Reduction Factor
| Node Type | Typical η | Meaning |
|-----------|----------|---------|
| Uniform | 2-3x | Se necesitan 1/2-1/3 muestras comparado con MC raw |
| Non-Uniform | 2-4x | Mejora significativa con nodos optimizados |
| Chebyshev | 3-5x | Mejor rendimiento para funciones suaves |

### Convergencia
- Ambos métodos (raw MC y CV MC) convergen a $O(1/\sqrt{m})$
- El método CV tiene constante más pequeña
- La ventaja es especialmente notable para $m$ pequeño a moderado

## Uso

### Ejecutar el notebook completo:
```bash
jupyter notebook monte_carlo_control_variate_nb.ipynb
```

### Ejecutar celdas individuales:
1. Asegurarse de que las dependencias están instaladas
2. Ejecutar celdas en orden secuencial
3. Las gráficas se guardan automáticamente en `/images/`

## Archivos Generados

El notebook genera las siguientes visualizaciones:
- `monte_carlo_convergence_comparison.png` - Convergencia para cada distribución de nodos
- `variance_reduction_analysis.png` - Factor de reducción de varianza
- `interpolants_comparison.png` - Comparación de interpolantes

## Requisitos

```python
numpy
matplotlib
scipy
```

Opcionalmente para mejor rendimiento:
```python
numba
```

## Extensiones Posibles

1. **Integración Multidimensional**: Extender MonteCarloControlVarNB1D a caso $d > 1$
2. **Selección Automática de Nodos**: Usar optimización para elegir los mejores nodos
3. **Funciones Adaptativas**: Ajustar el interpolante durante la integración
4. **Importancia Muestreo**: Combinar CV con importance sampling
5. **Análisis de Sensibilidad**: Estudiar dependencia en los parámetros

## Referencias Teóricas

### Control Variates
- Técnica clásica de reducción de varianza en MC
- Requiere función auxiliar $g(x)$ con integral analítica conocida
- Mejora efectiva cuando $\text{Cov}(f, g)$ es grande

### Bernstein Polynomials
- Base estable para interpolación y aproximación
- Propiedades de preservación de positividad
- Fórmula exacta para integral: $\int_a^b p(x)dx = \frac{b-a}{n+1}\sum_j c_j$

### Newton-Bernstein Algorithm
- Conversión eficiente entre formas de Newton y Bernstein
- Cálculo recursivo de puntos de control
- Complejidad $O(n^2)$ donde $n$ es el grado

## Notas del Profesor

Este notebook implementa exactamente la técnica especificada:
```python
class MonteCarloControlVarNB1D:
    """
    Integración Monte Carlo 1D con variable de control basada en
    el interpolante de Bernstein obtenido via NewtonBernsteinUnivariate.
    
    I = ∫_a^b f(x) dx ≈ I_p + (b-a) * E[f(U) - p(U)], U ~ U(a,b).
    """
```

La clase proporciona:
- Inicialización segura con validaciones
- Método `integrate()` para una sola corrida
- Método `integrate_multiple_runs()` para análisis estadístico
- Comparación automática con MC raw para cuantificar mejora

## Contribución del Proyecto

Este notebook integra:
- **Teoría**: Control variates, Bernstein polynomials, MC integration
- **Implementación**: Algoritmo Newton-Bernstein + Monte Carlo
- **Análisis**: Convergencia, eficiencia, comparación de métodos
- **Visualización**: Gráficas comparativas y análisis

Autor: Implementación para reproducción del ejercicio del profesor

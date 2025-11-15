# Estructura Modular del Informe LaTeX

## Descripción

El informe ha sido modularizado en archivos `.tex` independientes que se incluyen en un archivo principal. Esto facilita:

- **Mantenimiento**: Cada sección es independiente y fácil de editar
- **Colaboración**: Múltiples autores pueden trabajar en secciones diferentes
- **Organización**: Estructura lógica clara del documento
- **Derivación Formal**: Desarrollo paso-a-paso del algoritmo

## Estructura de Archivos

```
docs/
├── 00_main.tex                  # Archivo principal (compilar este)
├── 01_intro.tex                 # Introducción y motivación
├── 02_bernstein_props.tex       # Propiedades fundamentales de Bernstein
├── 03_derivation.tex            # Derivación formal paso-a-paso
├── 04_algorithm.tex             # Teorema principal y algoritmo
├── 05_implementation.tex        # Implementación en Python
├── 06_examples.tex              # Ejemplos numéricos
├── 07_conclusions.tex           # Conclusiones y referencias
└── main.pdf                     # PDF compilado (generado)
```

## Contenido de Cada Módulo

### 1. `00_main.tex` - Archivo Principal
- Define la clase de documento
- Carga paquetes necesarios
- Incluye todos los módulos con `\input{}`
- **Este es el archivo que debe compilarse**

### 2. `01_intro.tex` - Introducción
**Palabras clave:** Problema de interpolación, matriz de Bernstein-Vandermonde, mal condicionamiento, contribuciones

**Contenido:**
- Formulación del problema de interpolación Lagrangiana (Ec. 1.1)
- Representación de Bernstein-Bézier (Ec. 1.2-1.3)
- Desafío numérico: mal condicionamiento de matriz
- Estado del arte: Marco y Martínez (2007)
- Contribuciones de Ainsworth-Sánchez (2015)

### 3. `02_bernstein_props.tex` - Propiedades de Bernstein
**Palabras clave:** Propiedades fundamentales, relaciones de producto, elevación de grado, fórmula de Lagrange

**Contenido:**
- **P1 (Ec. 2.1-2.2)**: Relaciones de producto con polinomios lineales
  - Cómo multiplicar $B_k^n$ por $B_1^1$ o $B_0^1$ produce $B_{k±1}^{n+1}$
  
- **P2 (Ec. 2.5)**: Elevación de grado
  - Expresar $B_k^{n-1}$ como combinación lineal de $B_k^n$ y $B_{k+1}^n$
  - Importancia para pasar de grado $n-1$ a grado $n$ sin pérdida de información
  
- **P3 (Ec. 2.8)**: Fórmula de Lagrange mejorada
  - Representación numérica estable del interpolante

### 4. `03_derivation.tex` - Derivación Formal (❤️ CORAZÓN)
**Palabras clave:** Forma de Newton, recurrencias, Bernstein, elevación de grado

**Contenido - 4 Pasos:**

**Paso 1 (Sec. 3.1):** Forma de Newton del Interpolante
- Construcción recursiva: $p_0 \subset p_1 \subset \cdots \subset p_n$
- Forma de Newton: $p_k = \sum_{j=0}^k f[x_0,\ldots,x_j] w_j(x)$
- Ventaja: Agregar un nodo solo requiere una adición

**Paso 2 (Sec. 3.2):** Representación de Bernstein de $w_j(x)$
- ¿Cómo expresar $w_j(x) = \prod_{i=0}^{j-1}(x-x_i)$ en forma de Bernstein?
- Usar $x - x_{j-1} = (1-x_{j-1})B_1^1 - x_{j-1}B_0^1$ + propiedades P1
- **Resultado:** Recurrencia (Ec. 3.3) para coeficientes $w_k^{(j)}$

**Paso 3 (Sec. 3.3):** Elevación de Grado y Construcción de $p_k$
- Al pasar de $p_{k-1}$ a $p_k$:
  1. Elevar $p_{k-1}$ de grado $k-1$ a $k$ (usando P2)
  2. Sumar término nuevo $w_k(x) f[x_0,\ldots,x_k]$
- **Resultado:** Recurrencia (Ec. 3.5) para coeficientes $c_k^{(j)}$

**Paso 4 (Sec. 3.4):** Actualización de Diferencias Divididas
- Fórmula estándar (Ec. 3.7) para actualizar en cada iteración
- Costo: $O(n^2)$ total

**Resumen:** Tres recurrencias elegantes que lo dicen todo.

### 5. `04_algorithm.tex` - Teorema y Algoritmo
**Palabras clave:** Teorema principal, complejidad, generalización multidimensional

**Contenido:**
- **Teorema 4.1 (Ainsworth-Sánchez):**
  - $w_j^{(k)}$ son coeficientes de Bernstein de $w_j(x)$
  - $c_j^{(k)}$ son puntos de control de $p_j(x)$
  - Demostración por inducción usando propiedades P1-P2

- **Algoritmo 4.1:** Pseudocódigo completo (11 líneas)
  - Entrada: Nodos $\{x_j\}$ y datos $\{f_j\}$
  - Salida: Puntos de control $\{c_j\}$
  - Correspondencia línea-por-línea con Pasos 1-4

- **Análisis de Complejidad:**
  - Bucle externo: $n$ iteraciones
  - Bucles internos: $O(n^2)$ total
  - **Complejidad final: $O(n^2)$ operaciones** ✓

- **Contribución de M.A. Sánchez:** Generalización a:
  - Producto tensorial (múltiples variables)
  - Símplices en dimensión arbitraria
  - Espacios vectoriales generales (no solo $\mathbb{R}$)

### 6. `05_implementation.tex` - Python
**Palabras clave:** Modularidad, estructura de código, verificabilidad

**Contenido:**
- Tres módulos principales:
  - `bernstein.py`: Clase `BernsteinPolynomial`
  - `newton_bernstein.py`: Clase `NewtonBernstein` (implementa Alg. 4.1)
  - `utils.py`: Funciones auxiliares

- Ejemplo de uso mínimo
- Correspondencia entre teoría e implementación

### 7. `06_examples.tex` - Ejemplos Numéricos
**Palabras clave:** Validación, comparación con Marco-Martínez, raíces múltiples

**Contenido:**
- **Ejemplo 1:** Del artículo original
  - Polinomio cúbico, nodos uniformes
  - $\kappa(A) = 2.3 \times 10^6$
  - Precisión: $\sim 10^{-15}$

- **Ejemplo 2:** Raíces múltiples
  - Polinomio de grado 5 con raíz doble
  - $\kappa(A) = 3.5 \times 10^9$ (peor)
  - Precisión: $\sim 10^{-12}$ (degradación esperada)

- **Tabla Comparativa:** NB vs Marco-Martínez
  - Misma complejidad
  - Estabilidad comparable
  - Ventaja: derivación simple

### 8. `07_conclusions.tex` - Conclusiones
**Palabras clave:** Síntesis, impacto, futuro

**Contenido:**
- **Síntesis:** Cuatro logros del algoritmo NB
- **Contribución de Sánchez:** Generalización multidimensional
- **Aplicaciones:** CAGD, FEM, splines
- **Perspectivas futuras**
- **Referencias bibliográficas**

## Cómo Compilar

### Opción 1: Script Python (Recomendado)
```bash
python compile_modular.py
```

### Opción 2: Comando pdflatex directo
```bash
cd docs
pdflatex -interaction=nonstopmode 00_main.tex
pdflatex -interaction=nonstopmode 00_main.tex  # Compilar dos veces
```

### Opción 3: latexmk (si está instalado)
```bash
cd docs
latexmk -pdf 00_main.tex
```

## Estructura Lógica del Informe

```
Introducción (01)
    ↓
Propiedades Bernstein (02)
    ↓
Derivación Formal - 4 Pasos (03)
    ├─ Paso 1: Forma de Newton
    ├─ Paso 2: Representación Bernstein de w_j
    ├─ Paso 3: Elevación de grado para p_j
    └─ Paso 4: Actualización diferencias divididas
    ↓
Teorema + Algoritmo (04)
    ├─ Teorema 4.1 (Ainsworth-Sánchez)
    ├─ Algoritmo 4.1 (pseudocódigo)
    ├─ Análisis complejidad: O(n²)
    └─ Generalización de Sánchez
    ↓
Implementación Python (05)
    ├─ Módulo bernstein.py
    ├─ Módulo newton_bernstein.py
    └─ Módulo utils.py
    ↓
Ejemplos Numéricos (06)
    ├─ Ejemplo 1: caso del artículo
    ├─ Ejemplo 2: raíces múltiples
    └─ Comparativa con MM
    ↓
Conclusiones (07)
    ├─ Síntesis de resultados
    ├─ Contribución de Sánchez
    ├─ Aplicaciones
    └─ Referencias
```

## Ventajas de la Modularización

| Aspecto | Beneficio |
|---------|-----------|
| **Lectura** | Leer sección por sección sin cargar todo el documento |
| **Edición** | Cambiar una sección sin abrir 50 páginas |
| **Revisión** | Revisor puede revisar módulo por módulo |
| **Versionado** | Git diffs más legibles (cambios por sección) |
| **Reutilización** | Otros documentos pueden `\input{}` módulos |
| **Mantenimiento** | Fácil agregar, eliminar o reordenar secciones |

## Próximos Pasos

1. ✅ Compilar con `python compile_modular.py`
2. ✅ Revisar PDF generado
3. ✅ Editar módulos individuales según sea necesario
4. ✅ Agregar figuras/tablas en módulos específicos
5. ✅ Compartir repositorio Git con estructura clara

## Referencias para Estructura Modular LaTeX

- [Using \input with multiple files](https://www.latex-tutorial.com/tutorials/multi-file-documents/)
- [Best practices for large documents](https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes)
- [Managing large projects](https://tug.org/texinfohtml/latex2e.html#Multi_002dFile-Documents)

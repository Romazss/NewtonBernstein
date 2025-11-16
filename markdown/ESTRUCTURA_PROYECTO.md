# Estructura Reorganizada del Proyecto Newton-Bernstein

## 📁 Carpetas principales

### `notebooks/`
Contiene todos los Jupyter Notebooks del proyecto:
- `simple_univariate_nb.ipynb` - Ejemplo univariado simple
- `algorithm1_three_examples.ipynb` - Algoritmo con tres ejemplos
- `ejemplo_2_1_nodos_uniformes.ipynb` - Ejemplo 2.1 con nodos uniformes
- `newton_bernstein_univariate_notebook.ipynb` - Notebook principal univariado
- `turbulent_boundary_layer_nb.ipynb` - Ejemplo de capa límite turbulenta
- `univariate_case_study.ipynb` - Caso de estudio univariado

### `images/`
Almacena todas las imágenes generadas por los análisis:
- Gráficos de comparación de métodos (Chebyshev, etc.)
- Visualizaciones de puntos de control
- Mapas de calor de diferencias divididas
- Análisis de errores
- Ejemplos computados

### `markdown/`
Documentación en formato Markdown y texto:
- Análisis técnicos detallados
- Guías de inicio rápido
- Informes y auditorías
- Resúmenes ejecutivos
- Conclusiones y lecciones aprendidas

### `python/`
Scripts Python principales:
- `nb_core.py` - Módulo core
- `nb_univariate.py` - Implementación univariada
- `newton_bernstein_univariate.py` - Algoritmo univariado
- `compile_latex.py` - Compilador LaTeX
- `compile_modular.py` - Compilador modular
- `run_examples.py` - Script para ejecutar ejemplos

### `docs/`
Documentación en LaTeX (estructura modular):
- `main.tex` - Archivo principal
- `01_intro.tex` - Introducción
- `02_bernstein_props.tex` - Propiedades de Bernstein
- `03_derivation.tex` - Derivación del algoritmo
- `04_algorithm.tex` - Descripción del algoritmo
- `05_implementation.tex` - Implementación
- `06_examples.tex` - Ejemplos
- `07_conclusions.tex` - Conclusiones

### `src/`
Código fuente Python:
- `bernstein.py` - Implementación de Bernstein
- `newton_bernstein.py` - Algoritmo Newton-Bernstein
- `utils.py` - Utilidades

### `examples/`
Scripts de ejemplo:
- `example1_cubic.py` - Ejemplo cúbico
- `example2_quintic.py` - Ejemplo quíntico

### `tests/`
Suite de pruebas unitarias:
- `test_bernstein.py`
- `test_newton_bernstein.py`
- `test_utils.py`

## 📊 Estructura visual

\`\`\`
NewtonBernstein/
├── notebooks/          ← Jupyter Notebooks
├── images/            ← Imágenes PNG
├── markdown/          ← Documentación Markdown
├── python/            ← Scripts Python principales
├── docs/              ← LaTeX
├── src/               ← Código fuente
├── examples/          ← Scripts de ejemplo
├── tests/             ← Pruebas
├── requirements.txt
├── INFORME_FINAL.tex
└── ESTRUCTURA_PROYECTO.md
\`\`\`

## 🚀 Cómo empezar

1. Revisar la documentación inicial: \`markdown/00_COMIENZA_AQUI.md\`
2. Explorar los notebooks en \`notebooks/\`
3. Consultar análisis técnicos en \`markdown/\`
4. Ver imágenes en \`images/\`
5. Ejecutar scripts desde \`python/\`

## 📚 Archivos en raíz

- \`requirements.txt\` - Dependencias del proyecto
- \`INFORME_FINAL.tex\` - Informe final en LaTeX

---
**Fecha de reorganización:** 15 de Noviembre, 2025

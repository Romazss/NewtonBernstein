# Guía de Inicio Rápido - Newton-Bernstein

## 🚀 Comenzar a Usar el Proyecto

### 1. Instalación de Dependencias

```bash
# Navegar al directorio del proyecto
cd /Users/estebanroman/Documents/GitHub/NewtonBernstein

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # En macOS/Linux

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar los Ejemplos

#### Opción A: Ejecutar todos los ejemplos
```bash
python run_examples.py
```

#### Opción B: Ejecutar ejemplos individuales
```bash
# Ejemplo 1: Polinomio cúbico
python examples/example1_cubic.py

# Ejemplo 2: Polinomio de grado 5
python examples/example2_quintic.py
```

### 3. Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con reporte de cobertura
pytest tests/ --cov=src --cov-report=html
```

### 4. Compilar el Informe LaTeX

#### Usando el script de Python:
```bash
python compile_latex.py
```

#### Manualmente:
```bash
cd docs
pdflatex main.tex
pdflatex main.tex  # Dos veces para referencias correctas
```

El PDF se generará en: `docs/main.pdf`

## 📝 Uso Básico en tus Propios Scripts

### Ejemplo Simple

```python
import numpy as np
from src.newton_bernstein import find_roots

# Definir polinomio: p(x) = x² - 4
coeffs = np.array([-4, 0, 1])  # [-4, 0, 1] representa -4 + 0x + 1x²

# Encontrar raíces en [-10, 10]
roots = find_roots(coeffs, interval=(-10, 10), tolerance=1e-10)

print(f"Raíces: {roots}")
# Output: Raíces: [-2.0, 2.0]
```

### Ejemplo Avanzado con Estadísticas

```python
import numpy as np
from src.newton_bernstein import NewtonBernstein

# Polinomio: (x-1)(x-2)(x-3)
coeffs = np.array([-6, 11, -6, 1])

# Crear solver
solver = NewtonBernstein(coeffs, tolerance=1e-10)

# Encontrar raíces
roots = solver.find_roots((0, 4))

# Verificar raíces
for root, error in solver.verify_roots(roots):
    print(f"Raíz: {root:.10f}, Error: {error:.2e}")

# Ver estadísticas
stats = solver.get_statistics()
print(f"\nSubdivisiones: {stats['num_subdivisions']}")
print(f"Pasos de Newton: {stats['num_newton_steps']}")
```

## 🎯 Estructura del Proyecto

```
NewtonBernstein/
├── docs/
│   └── main.tex           # Informe completo (>2 páginas)
├── src/
│   ├── __init__.py
│   ├── newton_bernstein.py   # Algoritmo principal
│   ├── bernstein.py           # Operaciones de Bernstein
│   └── utils.py               # Funciones auxiliares
├── examples/
│   ├── example1_cubic.py      # Ejemplo del artículo
│   └── example2_quintic.py    # Ejemplo propio
├── tests/
│   ├── test_newton_bernstein.py
│   ├── test_bernstein.py
│   └── test_utils.py
├── README.md
├── requirements.txt
├── run_examples.py
└── compile_latex.py
```

## ✅ Verificación de Instalación

Para verificar que todo está correctamente instalado:

```bash
# Verificar Python
python --version  # Debe ser 3.8+

# Verificar numpy
python -c "import numpy; print(f'NumPy {numpy.__version__}')"

# Verificar matplotlib
python -c "import matplotlib; print(f'Matplotlib {matplotlib.__version__}')"

# Verificar pytest
pytest --version

# Verificar LaTeX (opcional)
pdflatex --version
```

## 📊 Contenido del Informe LaTeX

El informe `docs/main.tex` incluye:

1. **Introducción** - Contexto y motivación
2. **Polinomios de Bernstein** - Definiciones y propiedades
3. **El Algoritmo** - Descripción detallada del método
4. **Análisis de Convergencia** - Teoremas y pruebas
5. **Ejemplos Numéricos** - Resultados de los dos ejemplos
6. **Conclusiones** - Ventajas y limitaciones

Total: ~8-10 páginas compiladas

## 🔍 Contenido de los Ejemplos

### Ejemplo 1 (`example1_cubic.py`)
- **Polinomio**: p(x) = x³ - 6x² + 11x - 6
- **Raíces**: x = 1, 2, 3
- **Características**: Caso clásico con tres raíces simples
- **Fuente**: Ejemplo común en la literatura

### Ejemplo 2 (`example2_quintic.py`)
- **Polinomio**: p(x) = (x - 0.5)² · (x + 1) · (x - 2) · (x - 3.5)
- **Raíces**: x = -1, 0.5 (doble), 2, 3.5
- **Características**: Raíz múltiple, raíces irracionales
- **Fuente**: Ejemplo original diseñado para el proyecto

## 🆘 Solución de Problemas

### Problema: "ModuleNotFoundError: No module named 'src'"
**Solución**: Asegúrate de ejecutar los scripts desde el directorio raíz:
```bash
cd /Users/estebanroman/Documents/GitHub/NewtonBernstein
python examples/example1_cubic.py
```

### Problema: "pdflatex: command not found"
**Solución**: Instala LaTeX:
```bash
# macOS
brew install --cask mactex

# O usa el script de Python que detecta si LaTeX está disponible
python compile_latex.py
```

### Problema: Tests fallan
**Solución**: Verifica las dependencias:
```bash
pip install -r requirements.txt --upgrade
```

## 📚 Recursos Adicionales

- Ver `README.md` para documentación completa
- Los tests en `tests/` sirven como ejemplos adicionales de uso
- Cada módulo tiene docstrings detallados

## 🎓 Próximos Pasos

1. ✅ Ejecuta `python run_examples.py` para ver el algoritmo en acción
2. ✅ Compila el LaTeX con `python compile_latex.py`
3. ✅ Lee el PDF generado en `docs/main.pdf`
4. ✅ Experimenta con tus propios polinomios
5. ✅ Ejecuta los tests con `pytest tests/ -v`

---

**¡Proyecto completado!** Tienes:
- ✅ Informe LaTeX de más de 2 páginas
- ✅ Algoritmo implementado en Python (modular)
- ✅ 2 ejemplos numéricos (uno del artículo, uno propio)
- ✅ Tests completos
- ✅ Documentación detallada

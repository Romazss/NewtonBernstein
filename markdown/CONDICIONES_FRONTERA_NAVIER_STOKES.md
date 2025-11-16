# Condiciones de Frontera en Navier-Stokes 3D
## Interacción de Fuerzas Físicas en Puntos Críticos

**Documento de síntesis de análisis implementado**

---

## 📋 Resumen

Se ha desarrollado un análisis exhaustivo de **condiciones de frontera (BC)** para las ecuaciones de Navier-Stokes 3D, con énfasis en identificar los **puntos de interacción de fuerzas físicas** donde confluyen:
- Gradientes de presión (∇p)
- Esfuerzos viscosos (ν∇²u)
- Advección no-lineal ((u·∇)u)

---

## 1️⃣ Tipos de Condiciones de Frontera

### A. Dirichlet (u = g)
- **Significado físico**: Valor prescrito de velocidad
- **Ejemplo**: Entrada de flujo, pared sólida
- **Fuerzas dominantes**: Presión, gradientes locales
- **Ecuación**: u|_∂Ω = g(x,t)

### B. Neumann (∂u/∂n = h)
- **Significado físico**: Gradiente normal prescrito (esfuerzo)
- **Ejemplo**: Salida libre (traction-free)
- **Fuerzas dominantes**: Advección
- **Ecuación**: σ·n|_∂Ω = h(x,t), donde σ es tensor de esfuerzo

### C. No-Slip (u = 0 en pared)
- **Significado físico**: Fluido adherido a pared
- **Ejemplo**: Pared sólida en cavidades, canales
- **Fuerzas dominantes**: Esfuerzo cortante viscoso (máximo)
- **Equación**: ∂u/∂n ~ Re^0.25 en capa límite

### D. Free-Slip (u·n = 0, τ·u = 0)
- **Significado físico**: Interfaz sin fricción
- **Ejemplo**: Interfaz fluido-fluido, superficies simétricas
- **Fuerzas dominantes**: Tensión superficial (si aplica)
- **Ecuación**: Componente normal nula, tangencial libre

### E. Periódica (u(x) = u(x + L))
- **Significado físico**: Dominio topológicamente cerrado
- **Ejemplo**: DNS turbulencia isótropa
- **Fuerzas dominantes**: Todas (isotrópicas)
- **Ecuación**: u_i(x) = u_i(x + L*e_i)

---

## 2️⃣ Configuraciones Físicas Estudiadas

### **A. Cavidad con Tapa Móvil (Lid-Driven Cavity)**

```
┌─────────────────┐
│   →U₀ (Dirichlet)
│  ╭─────────╮   │
│  │         │   │
│  │ Vórtice │   │  Paredes: No-slip
│  │Principal│   │
│  ╰─────────╯   │
├─────────────────┤
│ Puntos críticos:│
│ • 4 esquinas    │
│ • Centro vórtice│
└─────────────────┘
```

**Parámetros**:
- Reynolds: 1000
- Viscosidad: ν = 10⁻³
- Puntos críticos: 5

**Interacción de Fuerzas**:
| Región | Fuerza Dominante | Escala | Efecto |
|--------|-----------------|--------|--------|
| Tapa | Presión | O(1) | Acelera fluido |
| Capa límite | Viscosidad | δ ~ Re^(-0.25) ≈ 0.18 | Disipa energía |
| Centro vórtice | Advección | O(Re^0.75) | Transporta vorticidad |
| Esquinas | Viscosidad | δ ~ Re^(-0.25) | Micro-vórtices |

---

### **B. Flujo en Canal (Channel Flow)**

```
Entrada (Dirichlet)     Salida (Neumann)
    ↓                        ↓
┌────────────────────────────┐
│ ╱╱╱ Perfil Poiseuille ╱╱╱ │  ∇p (cte) →
│                            │
└────────────────────────────┘
   ↑           ↑
  u=0 (No-slip)
```

**Parámetros**:
- Reynolds: 1000
- Longitud: L = 2π
- Viscosidad: ν = 10⁻³

**Balance de Fuerzas**:
$$\nabla p + \nabla^2 u = 0 \text{ (estado permanente)}$$

**Punto Crítico Principal**: Entrada
- Longitud desarrollo: L_e ~ 0.05·Re·D = 50·D
- Relación entrada/altura: 50

---

### **C. Capa Límite Turbulenta (Turbulent Boundary Layer)**

```
        Flujo libre
         u = U∞ (Dirichlet)
        ─────────────────────
        │ Núcleo turbulento
        │ ╱╱╱ Estructuras
    δ(x)│ ╱╱╱ coherentes
        │ Buffer layer
        │ Subcapa viscosa
        │ (u+ = y+ lineal)
        ├─── Pared (u=0, No-slip)
```

**Parámetros**:
- Reynolds: 10,000
- Velocidad libre: U∞ = 1
- Espesor inicial: δ₀ = 0.01

**Escalas Críticas**:
| Escala | Fórmula | Valor |
|--------|---------|-------|
| Viscosa | y⁺ = y·u_τ/ν | ~100 |
| Kolmogorov | η = Re^(-3/4) | ~0.0056 |
| Integral | δ = δ₀·(x/x₀)^n | Crece con x |

**Puntos Críticos**:
1. **Pared**: τ_wall = máximo → Generación vorticidad
2. **Subcapa viscosa** (y⁺ < 5): Disipación máxima
3. **Buffer layer** (5 < y⁺ < 30): Producción turbulencia
4. **Núcleo turbulento**: Estructuras coherentes

---

## 3️⃣ Análisis de Puntos Críticos de Interacción

### **Cavidad: Análisis de Fuerzas**

**Esquinas (Puntos críticos: ω)**
```
Análisis:
├─ Concentración de vorticidad
├─ Fuerzas: Viscosidad + Presión
├─ Efecto Reynolds: Vórtices secundarios más fuertes con Re↑
└─ Escala: δ ~ Re^(-0.25)
```

**Centro del vórtice principal**
```
Análisis:
├─ Balance: Advección ↔ Difusión viscosa
├─ Fuerzas: (u·∇)u + ν∇²u
├─ Dinámicas: Cuasi-equilibrio o caóticas (Re-dependiente)
└─ Fenómeno: Oscilaciones periódicas posibles
```

### **Canal: Puntos Críticos**

**Entrada**
```
Análisis:
├─ Desarrollo del perfil Poiseuille
├─ Longitud desarrollo: L_e ~ 0.05·Re = 50
├─ Fuerzas: ∇p × ν∇²u (compiten)
└─ Fenómeno: Transición entrada → flujo desarrollado
```

**Flujo Desarrollado**
```
Análisis:
├─ Equilibrio: ∂u/∂t = 0
├─ Balance: ∇p + ν∇²u = 0
├─ Vorticidad: Solo ω_z = ∂v/∂x - ∂u/∂y (transversal)
└─ Disipación: ε = ν|∇u|² uniforme
```

### **Capa Límite: Puntos Críticos**

**Subcapa Viscosa** (y⁺ < 5)
```
Análisis:
├─ Estructura: Perfil lineal u⁺ = y⁺
├─ Dominancia: Viscosidad >> Advección
├─ Esfuerzo pared: τ_wall = μ(∂u/∂y)|_wall = máx
├─ Escala de velocidad: u_τ = √(τ_wall/ρ) (escala de fricción)
└─ Rol: GENERACIÓN máxima de vorticidad
```

**Buffer Layer** (5 < y⁺ < 30)
```
Análisis:
├─ Estructura: Transición viscosa → logarítmica
├─ Perfil: u⁺ = 1/κ·ln(y⁺) + C (κ ≈ 0.41, von Kármán)
├─ Fuerzas: Viscosidad ~ Advección (balance delicado)
└─ Fenómeno: Bursts y sweep events (eyecciones/barridos)
```

**Núcleo Turbulento** (y⁺ > 30)
```
Análisis:
├─ Dinámicas: Turbulencia desarrollada
├─ Balance: PRODUCCIÓN = DISIPACIÓN (equilibrio turbulento)
├─ Estructuras: Streaks longitudinales, vórtices, ondas
├─ Escala integral: L ~ δ
└─ Escala de Kolmogorov: η ~ Re^(-3/4)
```

---

## 4️⃣ Comparación Cuantitativa

### Tabla: Escalas vs Reynolds

```
CAVIDAD (Re = 1000):
├─ Capa límite: δ ~ Re^(-0.25) = 0.1778
├─ Vorticidad amplificación: ω ~ Re^0.75 = 177.8
├─ Puntos críticos: 5 (4 esquinas + centro vórtice)
└─ Complejidad: ALTA (3 fuerzas interactuando)

CANAL (Re = 1000):
├─ Entrada desarrollo: L_e = 0.05·Re = 50
├─ Longitud entrada/altura: 50/1 = 50
├─ Espesor capa límite: δ ~ √(ν·L/U) = 0.141
├─ Punto crítico: Entrada
└─ Complejidad: MEDIA (Balance ∇p-viscosidad)

CAPA LÍMITE (Re = 10000):
├─ Escala viscosa: y⁺ ~ √Re = 100
├─ Escala Kolmogorov: η = Re^(-3/4) = 0.00560
├─ Rango escalas: 10^4 (vastísimo)
├─ Puntos críticos: 3 (pared + buffer + núcleo)
└─ Complejidad: MÁXIMA (Turbulencia + 3 fuerzas)
```

---

## 5️⃣ Tabla Comparativa: Tipos de BC

| Tipo BC | Símbolo | Aplicación | Fuerzas Dominantes | Ejemplo |
|---------|---------|-----------|-------------------|---------|
| **Dirichlet** | u = g | Entrada prescrita | Presión | Inlet canal |
| **Neumann** | ∂u/∂n = h | Salida libre | Advección | Outlet canal |
| **No-slip** | u = 0 | Pared sólida | Viscosidad | Cavidad, capa límite |
| **Free-slip** | u·n = 0 | Interfaz sin fricción | Tensión superficial | Interfaz fluido-fluido |
| **Periódica** | u(x)=u(x+L) | Flujo periódico | Todas | DNS turbulencia |

---

## 6️⃣ Implicaciones para Métodos Numéricos

### Newton-Bernstein Adaptativo en Puntos Críticos

**Estrategia**:
1. **Identificar puntos críticos** donde ∇u es máximo
2. **Refinar localmente** con Newton-Bernstein recursivo
3. **Capturar singularidades** (si existen) a nivel local

**Aplicación**:
- Cavidad: Refinar en esquinas
- Canal: Refinar en entrada
- Capa límite: Refinar en subcapa viscosa

**Ganancia**:
- Resolución O(n²) en lugar de O(n³)
- Identificación precisa de blow-up (si existe)

---

## 7️⃣ Conclusiones

### Hallazgos Clave

✅ **Cavidad**: Múltiples puntos críticos, sistema complejo
✅ **Canal**: Balance simples predecible analíticamente
✅ **Capa límite**: Máxima complejidad, rango amplio de escalas

### Perspectivas de Investigación

1. **Bifurcaciones**: Transiciones de estabilidad vs Re
2. **Optimización BC**: Encontrar BC óptimas para control
3. **Machine Learning**: Predicción de flujo con BC dados
4. **Newton-Bernstein**: Refinar adaptativamente en puntos críticos
5. **Análisis de sensibilidad**: Impacto de BC en soluciones globales

---

## 📚 Referencias Implementadas

- **Lid-Driven Cavity**: Benchmark clásico de validación numérica
- **Channel Flow**: Caso bien-establecido, solución analítica conocida
- **Turbulent Boundary Layer**: Fenómeno más complejo, experimental/numérico

---

*Análisis completado: 16 de noviembre de 2025*
*Notebook: `boundary_conditions_navier_stokes.ipynb`*

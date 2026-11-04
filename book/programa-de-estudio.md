# Programa de estudio: Bases de Datos Orientadas a Objetos en 90 días

> **Meta:** llegar al 1 % superior en Bases de Datos Orientadas a Objetos (BDOO / OODBMS) en 90 días (13 semanas), es decir, poder **explicar, diseñar, implementar, optimizar y criticar** sistemas de persistencia de objetos a nivel de arquitecto o investigador.

---

## 1. El método: cuatro técnicas que se refuerzan entre sí

| Técnica | Qué es | Por qué funciona | Cómo se aplica en este curso |
|---|---|---|---|
| **Recuerdo activo** (*active recall*) | Sacar la información de la memoria sin mirar el material | Cada recuperación fortalece la huella de memoria (efecto de prueba, *testing effect*) | Cada lección cierra con preguntas de recuerdo; el banco de 60 reactivos y las apps de autoevaluación |
| **Repetición espaciada** (*spaced repetition*) | Repasar en intervalos crecientes: 1 → 3 → 7 → 14 → 30 días | Se repasa justo antes de olvidar (curva de Ebbinghaus) | Calendario de repasos de la sección 4 y tarjetas al final de cada lección |
| **Intercalación** (*interleaving*) | Mezclar temas distintos en una misma sesión | Obliga al cerebro a **discriminar** qué concepto aplica, no solo a repetirlo | Sesiones mixtas los sábados; ejercicios que combinan OQL + transacciones + evolución de esquema |
| **Técnica Feynman** | Explicar un concepto como si se lo enseñaras a un niño de 12 años | Las lagunas de comprensión aparecen cuando no puedes simplificar | Recuadro «Explícalo como Feynman» en cada lección y plantilla de la sección 5 |

### El ciclo diario (90–120 min)

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 1. CALENTAMIENTO (10 min)  Recuerdo libre: escribe sin mirar todo lo  │
│                            que recuerdes de la lección anterior.      │
│ 2. ADQUISICIÓN  (35 min)   Lee la lección del día. Haz los ejemplos.  │
│ 3. FEYNMAN      (15 min)   Explica en voz alta / por escrito el       │
│                            concepto clave. Marca lo que no supiste.   │
│ 4. PRÁCTICA     (25 min)   Ejercicio de /ejemplos o código propio.    │
│ 5. RECUPERACIÓN (10 min)   Preguntas de recuerdo de la lección + 5    │
│                            reactivos aleatorios del banco (mezclados).│
│ 6. REPASO ESPACIADO (10m)  Tarjetas que tocan hoy según el calendario.│
└──────────────────────────────────────────────────────────────────────┘
```

!!! tip "Regla de oro"
    **Nunca releas para repasar: ponte a prueba.** Releer da sensación de dominio (ilusión de fluidez); recuperar lo construye de verdad.

---

## 2. Mapa de lecciones (temario completo)

| # | Lección | Conceptos | Semana |
|---|---|---|---|
| 00 | [Cómo estudiar este libro](lecciones/00-como-estudiar.md) | Metacognición, curva del olvido, tarjetas | 1 |
| 01 | [Fundamentos y motivación](lecciones/01-fundamentos.md) | Desajuste de impedancia, historia, manifiestos, generaciones de SGBD | 1 |
| 02 | [El modelo de objetos](lecciones/02-modelo-de-objetos.md) | OID, identidad vs igualdad, estado, comportamiento, encapsulamiento, objetos complejos, tipos y clases, herencia, polimorfismo, *late binding*, extensiones | 2 |
| 03 | [El estándar ODMG](lecciones/03-odmg.md) | Object Model, ODL, relaciones e inversas, *extents*, claves, colecciones (Set, Bag, List, Array, Dictionary), *language bindings* | 3 |
| 04 | [OQL: Object Query Language](lecciones/04-oql.md) | Expresiones de ruta, *select-from-where*, colecciones anidadas, cuantificadores, agrupación, invocación de métodos, comparación con SQL | 4 |
| 05 | [Persistencia](lecciones/05-persistencia.md) | Persistencia ortogonal, por alcanzabilidad, por herencia, *pointer swizzling*, carga diferida, ZODB, db4o, ObjectDB, JDO | 5 |
| 06 | [Arquitectura física y almacenamiento](lecciones/06-almacenamiento.md) | Servidor de páginas vs de objetos, *clustering*, caché cliente, formatos de OID, índices de ruta, índices de jerarquía de clases | 6 |
| 07 | [Transacciones y concurrencia](lecciones/07-transacciones.md) | ACID en objetos, bloqueo jerárquico, transacciones largas y anidadas, *check-out/check-in*, control optimista, MVCC, recuperación | 7 |
| 08 | [Evolución de esquema y versionado](lecciones/08-evolucion-esquema.md) | Taxonomía de cambios, conversión inmediata vs perezosa, *screening*, versiones de objetos y de esquemas, configuraciones | 8 |
| 09 | [Bases de datos objeto-relacionales](lecciones/09-objeto-relacional.md) | SQL:1999/2003, UDT, REF, tablas tipadas, herencia de tablas, PostgreSQL y Oracle | 9 |
| 10 | [Mapeo objeto-relacional (ORM)](lecciones/10-orm.md) | Patrones de Fowler, estrategias de herencia, *identity map*, *unit of work*, carga diferida, problema N+1 | 10 |
| 11 | [Optimización de consultas y rendimiento](lecciones/11-optimizacion.md) | Álgebra de objetos, reescritura de rutas, materialización de métodos, *benchmarks* OO1/OO7 | 11 |
| 12 | [Sistemas reales y ecosistema](lecciones/12-sistemas-reales.md) | GemStone/S, ObjectStore, Versant, Objectivity/DB, InterSystems IRIS, ObjectDB, db4o, ZODB, Realm, comparación con NoSQL | 12 |
| 13 | [Diseño avanzado, casos y frontera de investigación](lecciones/13-diseno-avanzado.md) | Criterios de selección, modelado de dominios complejos, distribución, seguridad, multimodelo, temas abiertos | 13 |

Material transversal: [Ejemplos y ejercicios](ejemplos/index.md) · [Autoevaluación](autoevaluacion.md) · [Glosario](glosario.md).

---

## 3. Plan semanal detallado (13 semanas ≈ 90 días)

Cada semana sigue el mismo patrón:

| Día | Actividad principal | Técnica dominante |
|---|---|---|
| Lunes | Lección nueva, parte 1 + ejemplos | Adquisición + Feynman |
| Martes | Lección nueva, parte 2 + código | Adquisición + práctica |
| Miércoles | Ejercicio de `/ejemplos` + preguntas de la lección | Recuerdo activo |
| Jueves | Profundización: lectura de una fuente primaria o un experimento propio | Elaboración |
| Viernes | Explicación Feynman completa del tema de la semana (escrita o en video, 5 min) | Feynman |
| Sábado | **Sesión intercalada**: 20 reactivos mezclados de *todas* las semanas vistas + 1 ejercicio de otro tema | Intercalación |
| Domingo | Descanso activo: solo repaso de tarjetas que tocan hoy (15 min) | Repetición espaciada |

### Fase 1 · Cimientos (semanas 1–4, días 1–28)

| Semana | Objetivo medible | Entregable |
|---|---|---|
| **1** (días 1–7) | Explicar en 2 minutos por qué existen las BDOO y qué es el desajuste de impedancia | Ensayo Feynman de una página + mapa mental de los 13 puntos obligatorios del Manifiesto de 1989 |
| **2** (días 8–14) | Distinguir identidad, igualdad superficial y profunda; modelar herencia múltiple | Modelo de clases de una biblioteca con 8 clases y 3 niveles de herencia |
| **3** (días 15–21) | Escribir un esquema ODL completo con relaciones inversas, *extents* y claves | Esquema ODL de un sistema universitario (ejemplo B1) |
| **4** (días 22–28) | Escribir 20 consultas OQL de complejidad creciente | Colección de consultas + **Examen 1**: 20 reactivos básicos, umbral 85 % |

### Fase 2 · Mecanismos internos (semanas 5–8, días 29–56)

| Semana | Objetivo medible | Entregable |
|---|---|---|
| **5** (días 29–35) | Implementar persistencia por alcanzabilidad con ZODB | Mini-aplicación ZODB con transacciones y `persistent.mapping` |
| **6** (días 36–42) | Diseñar el *clustering* y los índices para un patrón de acceso dado | Informe de diseño físico (ejemplo I2) |
| **7** (días 43–49) | Razonar sobre conflictos en transacciones largas y anidadas | Diagrama de bloqueos jerárquicos + simulación de conflicto optimista en ZODB |
| **8** (días 50–56) | Planear una migración de esquema sin parar el sistema | Plan de evolución perezosa (ejemplo A1) + **Examen 2**: 20 reactivos básicos e intermedios, umbral 85 % |

### Fase 3 · Integración y maestría (semanas 9–13, días 57–90)

| Semana | Objetivo medible | Entregable |
|---|---|---|
| **9** (días 57–63) | Modelar el mismo dominio con tipos de usuario en PostgreSQL y Oracle | Script SQL objeto-relacional (ejemplo I1) |
| **10** (días 64–70) | Detectar y corregir N+1, elegir la estrategia de herencia JPA | *Refactor* de un repositorio JPA con métricas de consultas |
| **11** (días 71–77) | Optimizar consultas de ruta y justificar índices | Análisis de un plan de consulta OO7 simplificado |
| **12** (días 78–84) | Comparar 5 OODBMS reales con criterios técnicos | Matriz de decisión ponderada |
| **13** (días 85–90) | Defender una arquitectura completa ante un panel | **Proyecto final** (ejemplo A2) + **Examen final**: 60 reactivos, umbral 90 % |

!!! success "Criterio de 1 % superior al día 90"
    - ≥ 90 % en el examen final de 60 reactivos **con el orden mezclado**.
    - Explicar sin notas cualquiera de las 13 lecciones en 5 minutos (Feynman).
    - Resolver los 6 ejercicios de `/ejemplos` sin consultar la solución.
    - Argumentar *cuándo NO* usar una BDOO (la señal más clara de dominio experto).

---

## 4. Calendario de repetición espaciada

Cada lección genera tarjetas (sección «Tarjetas de repaso» al final de cada capítulo). Repásalas en estos días relativos a la primera lectura:

| Repaso | R1 | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|
| Intervalo | +1 día | +3 días | +7 días | +14 días | +30 días |

Calendario de repasos por lección (día del programa en que toca repasarla):

| Lección (día de estudio) | R1 | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|
| 01 (día 2) | 3 | 5 | 9 | 16 | 32 |
| 02 (día 8) | 9 | 11 | 15 | 22 | 38 |
| 03 (día 15) | 16 | 18 | 22 | 29 | 45 |
| 04 (día 22) | 23 | 25 | 29 | 36 | 52 |
| 05 (día 29) | 30 | 32 | 36 | 43 | 59 |
| 06 (día 36) | 37 | 39 | 43 | 50 | 66 |
| 07 (día 43) | 44 | 46 | 50 | 57 | 73 |
| 08 (día 50) | 51 | 53 | 57 | 64 | 80 |
| 09 (día 57) | 58 | 60 | 64 | 71 | 87 |
| 10 (día 64) | 65 | 67 | 71 | 78 | 90 |
| 11 (día 71) | 72 | 74 | 78 | 85 | 90 |
| 12 (día 78) | 79 | 81 | 85 | 90 | — |
| 13 (día 85) | 86 | 88 | 90 | — | — |

**Regla de ajuste (estilo Leitner):** si fallas una tarjeta, vuelve al intervalo R1; si la aciertas con facilidad, salta un intervalo.

---

## 5. Plantilla Feynman (cópiala en tu cuaderno)

```text
CONCEPTO: ______________________________________

1. Explicación para un niño de 12 años (sin jerga):
   ______________________________________________

2. Analogía de la vida cotidiana:
   ______________________________________________

3. ¿Dónde me trabé? (lagunas detectadas):
   ______________________________________________

4. Vuelvo al material, corrijo y simplifico de nuevo:
   ______________________________________________

5. Ejemplo concreto en código o diagrama:
   ______________________________________________
```

---

## 6. Patrones de intercalación recomendados

Los sábados mezcla temas que **se confunden fácilmente**; así entrenas la discriminación:

| Pareja confusa | Pregunta discriminante |
|---|---|
| OID vs clave primaria | ¿Cambia la identidad si cambia el valor? |
| Persistencia por alcanzabilidad vs persistencia por herencia | ¿Qué decide que el objeto se guarde: el grafo o la clase? |
| Servidor de páginas vs servidor de objetos | ¿Qué viaja por la red y dónde se evalúa la consulta? |
| Conversión de esquema inmediata vs perezosa | ¿Cuándo se paga el costo de la migración? |
| BDOO pura vs objeto-relacional vs ORM | ¿Dónde vive el modelo de objetos: en el motor, en el SQL o en la aplicación? |
| Transacción anidada vs transacción larga | ¿El problema es la estructura o la duración? |
| Índice de ruta vs índice de jerarquía de clases | ¿Se indexa a lo largo de referencias o a lo largo de la herencia? |

---

## 7. Autoevaluación continua

- **Diario:** 5 reactivos aleatorios (`python self-test-app/oodb_quiz_console.py` con `max_questions: 5`).
- **Semanal (sábado):** 20 reactivos mezclados de todos los niveles vistos.
- **Exámenes de fase:** días 28, 56 y 90.
- Registra tu porcentaje en una tabla; la tendencia importa más que el número aislado.

| Semana | % sábado | Temas fallados | Acción |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| … | | | |

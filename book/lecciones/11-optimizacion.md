# Lección 11 · Optimización de consultas y rendimiento

## Objetivos

- Explicar por qué optimizar consultas de objetos es más difícil que optimizar SQL.
- Aplicar reescrituras: **rutas a *joins***, recorrido **hacia delante vs hacia atrás**, **desanidamiento** y **migración de predicados costosos**.
- Conocer los algoritmos de ***join* basados en punteros**.
- Usar la **materialización de métodos** con criterio.
- Interpretar los *benchmarks* **OO1** y **OO7**.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Quieres encontrar a todos los niños cuyo papá trabaja en Monterrey. Puedes ir **casa por casa** preguntando a cada niño dónde trabaja su papá (hacia delante) o ir **a las oficinas de Monterrey** y preguntar qué papás trabajan ahí y luego buscar a sus hijos (hacia atrás). Si en Monterrey trabajan pocos papás, el segundo camino es mucho más corto. El optimizador elige el camino más corto.

## 1. ¿Por qué es difícil?

| Dificultad | Explicación |
|---|---|
| **Métodos opacos** | El optimizador no sabe cuánto cuesta `e.promedio()` ni qué tan selectivo es |
| **Encapsulamiento** | Si la consulta solo ve métodos, no ve los atributos para usar índices |
| **Rutas largas** | `a.b.c.d` puede evaluarse de muchas formas |
| **Herencia y polimorfismo** | Un *extent* mezcla tipos; la ligadura tardía impide saber qué código se ejecuta |
| **Colecciones anidadas** | Los resultados no son planos; hay cuantificadores y subconsultas por todas partes |
| **Falta de un álgebra estándar** | Hay varias propuestas: álgebra de Shaw y Zdonik, cálculo de comprensiones de monoides (Fegaras y Maier), álgebras de colecciones |

## 2. Reescritura de expresiones de ruta

Consulta:

```sql
select v
from vehiculos v
where v.fabricante.empresa.ciudad = "Monterrey"
```

### Estrategia A: recorrido hacia delante (*forward traversal*, *pointer chasing*)

```text
para cada v en vehiculos:            # |vehiculos| = 1 000 000
    si v.fabricante.empresa.ciudad == "Monterrey": emitir v
Costo ≈ 1 000 000 × (3 desreferencias)
```

### Estrategia B: recorrido hacia atrás (*backward traversal*), como *join* por valor

```text
E = select e from empresas e where e.ciudad = "Monterrey"       # 3 empresas (índice sobre ciudad)
F = select f from fabricantes f where f.empresa in E             # 40 fabricantes
V = select v from vehiculos v where v.fabricante in F            # índice sobre fabricante
```

Si hay índices sobre `empresa.ciudad`, `fabricante.empresa` y `vehiculo.fabricante` (un **multi-índice**), el costo baja de millones de desreferencias a unos cuantos accesos a índice. Con un **índice anidado** `ciudad → vehiculos`, la consulta es una sola búsqueda.

**Regla:** recorrer hacia atrás conviene cuando el predicado final es **muy selectivo** y existen índices o referencias inversas; hacia delante, cuando el conjunto inicial ya es pequeño.

## 3. Algoritmos de *join* basados en punteros

Shekita y Carey (SIGMOD 1990) compararon:

| Algoritmo | Idea | Mejor caso |
|---|---|---|
| ***Naive pointer join*** | Para cada objeto, seguir su puntero | Objetos destino ya en caché o bien agrupados |
| ***Pointer-based hash join*** | Agrupar los OID destino por página en una tabla *hash* y leer cada página una sola vez | Muchas referencias a pocas páginas |
| ***Pointer-based sort-merge*** | Ordenar los OID por dirección física y recorrer en orden | Lecturas secuenciales de disco |
| ***Hybrid hash*** | Mezcla de los anteriores con memoria limitada | Uso general |

```python
# Idea del pointer-based hash join: agrupar desreferencias por página
from collections import defaultdict

def pointer_hash_join(origenes, pagina_de, leer_pagina):
    por_pagina = defaultdict(list)
    for o in origenes:
        por_pagina[pagina_de(o.ref_oid)].append(o)        # agrupar por página destino
    for pagina, grupo in sorted(por_pagina.items()):      # cada página se lee UNA vez
        objetos = leer_pagina(pagina)
        for o in grupo:
            yield o, objetos[o.ref_oid]
```

## 4. Predicados costosos y métodos

### Migración de predicados (Hellerstein y Stonebraker, 1993)

Con predicados caros (métodos, UDF), no basta con «filtrar lo antes posible». Se ordenan por **rango**:

```text
rango(p) = (selectividad(p) − 1) / costo_por_tupla(p)
```

Se evalúan primero los predicados de **rango más bajo** (muy selectivos y baratos).

| Predicado | Selectividad | Costo | Rango |
|---|---|---|---|
| `e.semestre = 9` | 0.1 | 1 | −0.9 |
| `e.promedio() > 9` | 0.2 | 50 | −0.016 |
| `e.tiene_beca()` | 0.5 | 5 | −0.1 |

Orden óptimo: `semestre` (−0.9) → `tiene_beca` (−0.1) → `promedio` (−0.016).

### Materialización de métodos (*function materialization*, Kemper, Kilger y Moerkotte, 1991)

Precalcular y guardar el resultado de un método (`e.promedio()`) para indexarlo o evitar recalcularlo.

- Requiere que el método sea **determinista** y **sin efectos secundarios**.
- Hay que **invalidar** el valor cuando cambian los objetos de los que depende (aquí, las inscripciones y calificaciones): se registran sus **dependencias**.
- Es un compromiso entre consultas rápidas y actualizaciones más caras (equivale a una vista materializada).

## 5. Desanidamiento (*unnesting*)

```sql
-- Consulta anidada (correlacionada)
select d.nombre
from departamentos d
where exists p in d.profesores: p.salario > 80000

-- Reescritura como semi-join
select distinct p.pertenece_a.nombre
from profesores p
where p.salario > 80000
```

La segunda forma puede usar un índice sobre `salario` y evita recorrer todos los departamentos. El desanidamiento clásico de Kim (1982) se extendió a OQL para cuantificadores y colecciones (Steenhagen, Apers y Blanken, 1994; Fegaras y Maier, 2000).

## 6. *Benchmarks*

### OO1 (Cattell y Skeen, 1992) — «el *benchmark* de Sun»

- BD de **partes** (20 000 en la versión pequeña), cada una con **3 conexiones** a otras partes (90 % hacia partes «cercanas» para premiar el *clustering*).
- Operaciones: ***lookup*** (1 000 búsquedas por id), ***traversal*** (recorrido de 7 niveles = 3 280 partes) e ***insert*** (100 partes nuevas con sus conexiones y *commit*).
- Mostró que los OODBMS eran **órdenes de magnitud** más rápidos que los SGBDR de la época en recorridos con caché caliente.

### OO7 (Carey, DeWitt y Naughton, SIGMOD 1993)

- Modelo de diseño CAD: **módulos → ensambles → partes compuestas → partes atómicas**, más documentos y manuales.
- Mide **recorridos** (T1, T2, T6…), **consultas** (Q1–Q8: búsquedas exactas, por rango, *joins* por valor) y **modificaciones estructurales**.
- Conclusión: ningún sistema ganaba en todo; el resultado dependía fuertemente del *clustering*, de la caché y de la arquitectura (servidor de páginas vs de objetos).

!!! note "Lección práctica"
    Mide **con tu propia carga**. Los *benchmarks* sintéticos sirven para entender compromisos, no para elegir producto.

## 7. Lista de verificación de rendimiento en una BDOO

1. **Modelado:** literales para valores, objetos para entidades compartidas.
2. ***Clustering*** alineado con el recorrido dominante.
3. **Índices** sobre los predicados frecuentes y sobre las rutas críticas.
4. **Tamaño de transacción:** ni demasiado grande (memoria, conflictos) ni demasiado pequeño (sobrecosto de *commit*); usa *savepoints*.
5. **Caché cliente:** dimensiona la caché (`cache_size` en ZODB) según el conjunto de trabajo.
6. **Colecciones grandes:** árboles B (`BTrees`) en lugar de listas o diccionarios gigantes.
7. **Métodos en consultas:** baratos, deterministas y sin efectos secundarios.
8. **Monitorear** conflictos, *cache hits* y desreferencias por transacción.

## Errores comunes

- ❌ Suponer que filtrar primero siempre es mejor (falla con predicados costosos).
- ❌ Materializar métodos que dependen de datos muy volátiles.
- ❌ Guardar una colección de millones de elementos como una `PersistentList` (se carga y se reescribe entera).
- ❌ Extrapolar un *benchmark* de laboratorio a producción.

## Conexiones (intercalación)

- Multi-índice e índice anidado ↔ [Lección 06](06-almacenamiento.md).
- Cuantificadores y `partition` ↔ [OQL](04-oql.md).
- N+1 como problema de navegación ↔ [ORM](10-orm.md).

## Preguntas de recuerdo activo

1. ¿Cuándo conviene recorrer una ruta hacia atrás?
2. ¿Cómo se calcula el rango de un predicado y en qué orden se evalúan?
3. ¿Qué condiciones debe cumplir un método para materializarse?
4. ¿Qué mide OO1 y qué estructura modela OO7?
5. ¿Qué ventaja tiene un *pointer-based hash join* sobre el recorrido ingenuo?

??? success "Respuestas"
    1. Cuando el predicado sobre el final de la ruta es muy selectivo y hay índices o referencias inversas.
    2. `(selectividad − 1) / costo`; se evalúan de menor a mayor rango.
    3. Ser determinista, no tener efectos secundarios y tener dependencias rastreables para invalidarlo.
    4. OO1 mide *lookup*, *traversal* e *insert* sobre partes y conexiones; OO7 modela un diseño CAD con módulos, ensambles, partes compuestas y atómicas.
    5. Lee cada página destino una sola vez agrupando las desreferencias, en vez de saltar aleatoriamente por el disco.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| *Forward traversal* | Seguir punteros desde el *extent* inicial |
| *Backward traversal* | Partir del predicado final y subir con índices o referencias inversas |
| Materialización de métodos | Precalcular resultados de métodos con invalidación por dependencias |
| OO7 | *Benchmark* CAD de Carey, DeWitt y Naughton (1993) |
| Rango de predicado | (selectividad − 1) / costo |

# Lección 04 · OQL: Object Query Language

## Objetivos

- Escribir consultas OQL con **expresiones de ruta**, colecciones anidadas e invocación de métodos.
- Saber qué **tipo de resultado** devuelve cada consulta (`bag`, `set`, `list`, `struct`, objeto).
- Usar cuantificadores (`for all`, `exists`), agregación, `group by` con `partition`, `define`, `element`, `flatten` y conversiones de tipo.
- Comparar OQL con SQL y con JPQL.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    En SQL, para saber la ciudad del cliente de un pedido tienes que juntar dos listas y buscar coincidencias, como unir dos rompecabezas. En OQL sigues las flechas: `pedido.cliente.direccion.ciudad`, como seguir un hilo de una cuenta a otra en un collar.

## 1. Principios de diseño

1. **Lenguaje funcional y ortogonal:** toda consulta es una expresión; cualquier expresión que devuelve una colección puede usarse en `from`, y las consultas se componen libremente.
2. **Sintaxis cercana a SQL-92** para el bloque `select-from-where`.
3. **Sin operadores de actualización:** las modificaciones se hacen invocando métodos.
4. **Puntos de entrada:** *extents* y objetos con nombre.

## 2. Esquema de trabajo

Usaremos el esquema `Universidad` de la [Lección 03](03-odmg.md) (`personas`, `profesores`, `estudiantes`, `departamentos`, `cursos`, `inscripciones`).

## 3. Consultas básicas

```sql
-- Q1. Todos los profesores: el extent por sí solo es una consulta válida → set<Profesor>
profesores

-- Q2. Nombres de profesores con doctorado → bag<string>
select p.nombre
from profesores p
where p.grado = DOCTORADO

-- Q3. Sin duplicados → set<string>
select distinct p.pertenece_a.nombre
from profesores p

-- Q4. Resultado estructurado → bag<struct(nombre: string, sal: float)>
select struct(nombre: p.nombre, sal: p.salario)
from profesores p
where p.salario > 40000

-- Q5. Ordenado → list<...>
select p.nombre, p.salario
from profesores p
order by p.salario desc
```

### Tipo del resultado

| Forma | Tipo |
|---|---|
| `select ...` | `bag<T>` |
| `select distinct ...` | `set<T>` |
| `... order by ...` | `list<T>` |
| `select a, b ...` (varias proyecciones) | colección de `struct(a: ..., b: ...)` |
| `element(consulta)` | El único elemento (error si hay 0 o más de 1) |
| Nombre de objeto | El objeto mismo |

## 4. Expresiones de ruta

```sql
-- Q6. Ciudad del departamento de cada profesor: navegación implícita (≈ join)
select p.nombre, p.pertenece_a.nombre
from profesores p

-- Q7. Ruta que atraviesa una colección: se necesita una variable por cada colección
select e.nombre, i.curso.titulo, i.calificacion
from estudiantes e, e.inscripciones i
where i.curso.impartido_por.nombre = "Ada Lovelace"
```

!!! warning "Regla de rutas"
    Una expresión de ruta `x.a.b` es válida mientras cada paso sea **un solo valor**. Si un paso es una colección (`e.inscripciones`), no puedes escribir `e.inscripciones.curso`: debes **introducir una variable** en el `from` (`e.inscripciones i`). Las rutas a través de referencias simples equivalen a *joins* implícitos (*implicit joins*).

## 5. Invocación de métodos

```sql
-- Q8. Estudiantes con promedio mayor a 9 (promedio() es un método)
select e.nombre, e.promedio()
from estudiantes e
where e.promedio() > 9.0

-- Q9. Polimorfismo: personas mayores de 60; edad() puede estar redefinido en subclases
select x.nombre
from personas x
where x.edad() > 60
```

Los métodos usados en consultas **no deberían tener efectos secundarios**; el optimizador puede evaluarlos más o menos veces de lo esperado.

## 6. Cuantificadores y pertenencia

```sql
-- Q10. Profesores cuyos cursos son TODOS de 8 créditos o más
select p.nombre
from profesores p
where for all c in p.imparte: c.creditos >= 8

-- Q11. Departamentos con al menos un profesor que gana más de 80 000
select d.nombre
from departamentos d
where exists p in d.profesores: p.salario > 80000

-- Q12. Pertenencia
select c.titulo
from cursos c
where c.impartido_por in (select p from profesores p where p.grado = DOCTORADO)
```

## 7. Subconsultas en `from` y en `select`

```sql
-- Q13. Para cada departamento, la lista de títulos de sus cursos (colección anidada)
select struct(
         depto: d.nombre,
         cursos: (select c.titulo
                  from d.profesores p, p.imparte c))
from departamentos d

-- Q14. Consulta sobre el resultado de otra consulta
select x.nombre
from (select p from profesores p where p.salario > 50000) as x
where x.grado = MAESTRIA
```

**Resultados no planos:** OQL no obliga a la 1FN; Q13 devuelve un `bag<struct(depto: string, cursos: bag<string>)>`.

## 8. Agregación y agrupación

```sql
-- Q15. Agregados sobre colecciones
count(profesores)
avg(select p.salario from profesores p)
max(select c.creditos from cursos c)

-- Q16. group by con partition: cada grupo trae la colección de sus miembros
select depto, prom: avg(select x.p.salario from partition x)
from profesores p
group by depto: p.pertenece_a.nombre
having avg(select x.p.salario from partition x) > 45000
```

`partition` es una variable implícita: el `bag` de elementos del grupo. Cada elemento es un `struct` con las variables del `from` (aquí, `p`).

## 9. Operadores de colecciones y conversión de tipos

```sql
-- Q17. Aplanar colección de colecciones
flatten(select p.imparte from profesores p)       -- bag<set<Curso>> → bag<Curso>

-- Q18. Conversión
listtoset(select c.titulo from cursos c order by c.titulo)
distinct(bag(1, 1, 2))                            -- set(1, 2)

-- Q19. Operaciones de conjuntos
(select p from profesores p where p.grado = DOCTORADO)
union
(select p from profesores p where p.salario > 70000)

-- Q20. Indexación de listas
first(select p from profesores p order by p.salario desc)
(select p from profesores p order by p.salario desc)[0:2]   -- los 3 mejores pagados
```

### Conversión descendente (*downcasting*)

```sql
-- Q21. Del extent de personas, solo los profesores con su salario
select ((Profesor) x).salario
from personas x
where x in profesores
```

## 10. Consultas con nombre (`define`)

```sql
define doctores as
    select p from profesores p where p.grado = DOCTORADO;

select d.nombre from doctores d where d.salario > 60000
```

## 11. OQL vs SQL vs JPQL

| Aspecto | OQL | SQL (relacional) | JPQL |
|---|---|---|---|
| Navegación | Rutas `a.b.c` | `JOIN` explícito | Rutas + `JOIN` sobre asociaciones |
| Resultado | Cualquier tipo, anidado | Tabla plana | Entidades, escalares, DTO |
| Métodos en consultas | Sí | Funciones definidas por el usuario | No (solo propiedades mapeadas) |
| Polimorfismo | Nativo sobre *extents* | No | Sí, sobre jerarquías de entidades |
| Composición | Ortogonal total | Restringida por cláusulas | Restringida |
| Actualizaciones | Vía métodos | `UPDATE`/`DELETE` | `UPDATE`/`DELETE` masivos |

### Traducción OQL → SQL

```sql
-- OQL
select e.nombre, i.curso.titulo
from estudiantes e, e.inscripciones i
where i.curso.creditos > 6
```

```sql
-- SQL equivalente sobre un esquema normalizado
SELECT per.nombre, c.titulo
FROM estudiante e
JOIN persona per    ON per.curp = e.curp
JOIN inscripcion i  ON i.estudiante_id = e.curp
JOIN curso c        ON c.clave = i.curso_clave AND c.periodo = i.curso_periodo
WHERE c.creditos > 6;
```

## Errores comunes

- ❌ Escribir `e.inscripciones.curso` (ruta que atraviesa una colección sin variable).
- ❌ Suponer que `select` sin `distinct` devuelve un conjunto.
- ❌ Usar métodos con efectos secundarios dentro de `where`.
- ❌ Olvidar que `element()` falla si la subconsulta devuelve más de un elemento.

## Conexiones (intercalación)

- Rutas ↔ **índices de ruta** ([Lección 06](06-almacenamiento.md)) y **reescritura** ([Lección 11](11-optimizacion.md)).
- Polimorfismo ↔ inclusión de *extents* ([Lección 02](02-modelo-de-objetos.md)).
- JPQL y N+1 ↔ [Lección 10](10-orm.md).

## Preguntas de recuerdo activo

1. ¿Qué tipo devuelve `select distinct ...`? ¿Y con `order by`?
2. ¿Por qué `e.inscripciones.curso` es inválido?
3. ¿Qué contiene la variable `partition`?
4. ¿Cómo obtienes el salario de las personas que son profesores desde el *extent* `personas`?
5. ¿Por qué OQL no tiene `UPDATE`?

??? success "Respuestas"
    1. `set<T>`; con `order by`, `list<T>`.
    2. Porque `inscripciones` es una colección; hay que introducir una variable de iteración en el `from`.
    3. El *bag* de elementos del grupo; cada uno es un `struct` con las variables del `from`.
    4. Con un *downcast*: `select ((Profesor) x).salario from personas x where x in profesores`.
    5. Para respetar el encapsulamiento: los cambios se hacen invocando métodos de los objetos.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Ortogonalidad de OQL | Cualquier expresión que devuelva colección puede usarse donde se espera una colección |
| `flatten` | Convierte colección de colecciones en colección simple |
| `element(q)` | Extrae el único elemento de `q`; error si no hay exactamente uno |
| `define` | Crea una consulta con nombre reutilizable |
| Join implícito | Navegación por ruta a través de referencias simples |

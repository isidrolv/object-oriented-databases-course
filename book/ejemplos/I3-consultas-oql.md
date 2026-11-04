# I3 · Batería de consultas OQL

**Nivel:** 🟡 Intermedio · **Lección:** [04](../lecciones/04-oql.md) · **Tiempo:** 50 min

## 1. Planteamiento del problema

Escribe 8 consultas OQL sobre el esquema `Universidad` de la [Lección 03](../lecciones/03-odmg.md) y **predice el resultado exacto** (valor y tipo de colección) sobre los datos de prueba.

## 2. Escenario de ejecución

Datos de prueba en la BD:

| Profesor | Departamento | Grado | Salario | Imparte |
|---|---|---|---|---|
| Ada | Sistemas | DOCTORADO | 90 000 | BD (8 cr), Compiladores (8 cr) |
| Alan | Sistemas | MAESTRIA | 60 000 | IA (6 cr) |
| Emmy | Matemáticas | DOCTORADO | 70 000 | Álgebra (8 cr) |

| Estudiante | Inscripciones (curso: calificación) |
|---|---|
| Luis | BD: 9.5, IA: 8.0 |
| Sofía | BD: 10.0, Álgebra: 9.0 |
| Diego | IA: 7.0 |

`promedio()` es el promedio de las calificaciones del estudiante.

## 3. Entradas y salidas

| # | Pregunta | Salida esperada (tipo) |
|---|---|---|
| Q1 | Nombres de profesores con doctorado | `bag<string>` |
| Q2 | Departamentos (sin repetir) con algún profesor que gane más de 80 000 | `set<string>` |
| Q3 | Profesores cuyos cursos tienen **todos** 8 créditos | `bag<string>` |
| Q4 | Estudiante y calificación en cursos impartidos por Ada | `bag<struct>` |
| Q5 | Salario promedio por departamento | `bag<struct(depto, prom)>` |
| Q6 | El profesor mejor pagado (un objeto, no una colección) | `Profesor` |
| Q7 | Estudiantes con promedio mayor que 8.5, ordenados por nombre | `list<string>` |
| Q8 | Cada curso con la colección de nombres de sus inscritos | `bag<struct(curso, alumnos: bag<string>)>` |

## 4. Solución propuesta incompleta

```sql
-- Q1
select p.nombre from profesores p where ________

-- Q2
select ________ p.pertenece_a.nombre from profesores p where p.salario > 80000

-- Q3
select p.nombre from profesores p where ________ c in p.imparte: c.creditos = 8

-- Q4
select struct(alumno: i.estudiante.nombre, calif: i.calificacion)
from cursos c, ________
where c.impartido_por.nombre = "Ada"

-- Q5
select depto, prom: avg(select x.p.salario from ________ x)
from profesores p
group by depto: ________

-- Q6
________(select p from profesores p order by p.salario desc)

-- Q7
select e.nombre from estudiantes e where ________ order by ________

-- Q8
select struct(curso: c.titulo,
              alumnos: (select ________ from ________))
from cursos c
```

---

## 5. Respuesta correcta esperada

??? success "Ver soluciones y resultados"

    ```sql
    -- Q1 → bag("Ada", "Emmy")
    select p.nombre from profesores p where p.grado = DOCTORADO

    -- Q2 → set("Sistemas")
    select distinct p.pertenece_a.nombre from profesores p where p.salario > 80000

    -- Q3 → bag("Ada", "Emmy")   (Alan imparte IA de 6 créditos)
    select p.nombre from profesores p where for all c in p.imparte: c.creditos = 8

    -- Q4 → bag(struct(alumno:"Luis", calif:9.5), struct(alumno:"Sofía", calif:10.0))
    --      Compiladores no tiene inscritos, así que no aporta filas
    select struct(alumno: i.estudiante.nombre, calif: i.calificacion)
    from cursos c, c.inscritos i
    where c.impartido_por.nombre = "Ada"

    -- Q5 → bag(struct(depto:"Sistemas", prom:75000), struct(depto:"Matemáticas", prom:70000))
    select depto, prom: avg(select x.p.salario from partition x)
    from profesores p
    group by depto: p.pertenece_a.nombre

    -- Q6 → el objeto Profesor "Ada"
    first(select p from profesores p order by p.salario desc)
    -- alternativa: element(select p from profesores p
    --                      where p.salario = max(select q.salario from profesores q))

    -- Q7 → list("Luis", "Sofía")   (Luis 8.75, Sofía 9.5, Diego 7.0)
    select e.nombre from estudiantes e where e.promedio() > 8.5 order by e.nombre

    -- Q8 → bag(
    --   struct(curso:"BD",           alumnos: bag("Luis", "Sofía")),
    --   struct(curso:"Compiladores", alumnos: bag()),
    --   struct(curso:"IA",           alumnos: bag("Luis", "Diego")),
    --   struct(curso:"Álgebra",      alumnos: bag("Sofía")))
    select struct(curso: c.titulo,
                  alumnos: (select i.estudiante.nombre from c.inscritos i))
    from cursos c
    ```

    **Puntos de control:**

    - Q3: si un profesor no impartiera ningún curso, `for all` sería **verdadero** (cuantificación universal vacía). ¡Pregunta clásica de examen!
    - Q4 y Q8 muestran la diferencia entre un *join* (Q4 descarta Compiladores) y una colección anidada (Q8 conserva Compiladores con un `bag` vacío).
    - Q6: `first` sobre una lista; `element` exige exactamente un elemento (un empate en el salario máximo provocaría un error).

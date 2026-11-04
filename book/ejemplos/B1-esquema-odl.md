# B1 · Modelar un esquema ODL de biblioteca

**Nivel:** 🟢 Básico · **Lecciones:** [02](../lecciones/02-modelo-de-objetos.md), [03](../lecciones/03-odmg.md) · **Tiempo:** 40 min

## 1. Planteamiento del problema

Una red de bibliotecas quiere migrar su catálogo a una BDOO compatible con ODMG. Debes escribir el esquema **ODL** que represente libros, ejemplares físicos, autores, socios y préstamos, decidiendo correctamente qué es **objeto** y qué es **literal**, qué relaciones necesitan **inversa** y dónde van los ***extents*** y las **claves**.

## 2. Escenario de ejecución

- Un **libro** (obra) tiene ISBN único, título, año y uno o varios **autores**; un autor puede escribir muchos libros.
- Cada libro tiene varios **ejemplares** físicos, cada uno con código de barras único y estado (`DISPONIBLE`, `PRESTADO`, `BAJA`).
- Un **socio** tiene número de credencial único, nombre y una **dirección** (calle, ciudad, CP) que nadie más comparte.
- Un **préstamo** relaciona un socio con un ejemplar; tiene fecha de salida, fecha límite y fecha de devolución (opcional). Hay que poder preguntar «¿qué préstamos tiene este socio?» y «¿qué préstamos ha tenido este ejemplar?».
- Hay dos tipos de socio: **estudiante** (con matrícula) y **docente** (con número de empleado); los docentes pueden tener hasta 10 préstamos simultáneos y los estudiantes 3. Se debe preguntar a cualquier socio `limite_prestamos()`.

## 3. Entradas y salidas

| Entrada | Salida esperada |
|---|---|
| Requisitos anteriores | Un módulo ODL `Biblioteca` que compile conceptualmente |
| — | Justificación (máx. 5 líneas) de las decisiones objeto vs literal |
| — | Dos consultas OQL que validen el esquema: (a) títulos prestados actualmente al socio con credencial `"S-100"`; (b) autores con más de 5 libros |

## 4. Solución propuesta incompleta

Completa los `____`:

```text
module Biblioteca {

  struct Direccion { string calle; string ciudad; string cp; };

  enum Estado { DISPONIBLE, PRESTADO, BAJA };

  class Autor ( extent autores ) {
    attribute string nombre;
    relationship set<Libro> escribio inverse ____;
  };

  class Libro ( extent libros key ____ ) {
    attribute string isbn;
    attribute string titulo;
    attribute short  anio;
    relationship set<Autor>    autores    inverse Autor::escribio;
    relationship set<Ejemplar> ejemplares inverse ____;
  };

  class Ejemplar ( extent ejemplares key codigo_barras ) {
    attribute string codigo_barras;
    attribute Estado estado;
    relationship Libro obra inverse Libro::ejemplares;
    relationship ____ prestamos inverse Prestamo::ejemplar;
  };

  class Socio ( extent socios key credencial ) {
    attribute string    credencial;
    attribute string    nombre;
    attribute ____      direccion;            // ¿objeto o literal?
    relationship set<Prestamo> prestamos inverse Prestamo::socio;
    short limite_prestamos();
  };

  class Estudiante ____ Socio ( extent estudiantes ) {
    attribute string matricula;
    // ¿qué falta aquí?
  };

  class Docente ____ Socio ( extent docentes ) {
    attribute string num_empleado;
  };

  class Prestamo ( extent prestamos ) {
    attribute date salida;
    attribute date limite;
    attribute date devolucion;               // puede ser nula
    relationship Socio    socio    inverse ____;
    relationship Ejemplar ejemplar inverse Ejemplar::prestamos;
  };
};
```

Consultas por completar:

```sql
-- (a)
select p.ejemplar.obra.titulo
from ____ s, s.prestamos p
where s.credencial = "S-100" and ____

-- (b)
select a.nombre
from autores a
where ____(a.escribio) > 5
```

---

## 5. Respuesta correcta esperada

??? success "Ver solución completa"

    ```text
    module Biblioteca {

      struct Direccion { string calle; string ciudad; string cp; };

      enum Estado { DISPONIBLE, PRESTADO, BAJA };

      class Autor ( extent autores ) {
        attribute string nombre;
        relationship set<Libro> escribio inverse Libro::autores;
      };

      class Libro ( extent libros key isbn ) {
        attribute string isbn;
        attribute string titulo;
        attribute short  anio;
        relationship set<Autor>    autores    inverse Autor::escribio;
        relationship set<Ejemplar> ejemplares inverse Ejemplar::obra;
      };

      class Ejemplar ( extent ejemplares key codigo_barras ) {
        attribute string codigo_barras;
        attribute Estado estado;
        relationship Libro obra inverse Libro::ejemplares;
        relationship set<Prestamo> prestamos inverse Prestamo::ejemplar;
      };

      class Socio ( extent socios key credencial ) {
        attribute string    credencial;
        attribute string    nombre;
        attribute Direccion direccion;      // literal: no se comparte ni tiene vida propia
        relationship set<Prestamo> prestamos inverse Prestamo::socio;
        short limite_prestamos();
      };

      class Estudiante extends Socio ( extent estudiantes ) {
        attribute string matricula;
        short limite_prestamos();           // redefinición: devuelve 3
      };

      class Docente extends Socio ( extent docentes ) {
        attribute string num_empleado;
        short limite_prestamos();           // redefinición: devuelve 10
      };

      class Prestamo ( extent prestamos ) {
        attribute date salida;
        attribute date limite;
        attribute date devolucion;
        relationship Socio    socio    inverse Socio::prestamos;
        relationship Ejemplar ejemplar inverse Ejemplar::prestamos;
      };
    };
    ```

    **Justificación de decisiones:**

    1. `Direccion` es un **literal** (`struct`): no se comparte y no tiene identidad propia.
    2. `Prestamo` es una **clase** porque es una asociación M:N entre socios y ejemplares **con atributos** (fechas).
    3. Libro y Ejemplar son clases distintas: la obra es abstracta y el ejemplar es físico (patrón *tipo/instancia*).
    4. `limite_prestamos()` se **redefine** en las subclases; gracias a la ligadura tardía, `s.limite_prestamos()` sobre el *extent* `socios` devuelve 3 o 10 según el tipo real.
    5. Los *extents* `estudiantes` y `docentes` están **incluidos** en `socios`.

    ```sql
    -- (a) préstamos activos (sin devolución) del socio S-100
    select p.ejemplar.obra.titulo
    from socios s, s.prestamos p
    where s.credencial = "S-100" and p.devolucion = nil

    -- (b) autores prolíficos
    select a.nombre
    from autores a
    where count(a.escribio) > 5
    ```

    **Errores frecuentes:** declarar `Direccion` como clase; olvidar las inversas; usar `s.prestamos.ejemplar` sin variable de iteración; no redefinir `limite_prestamos()` en las subclases.

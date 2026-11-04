# Lección 03 · El estándar ODMG 3.0

## Objetivos

- Conocer los **cinco componentes** del estándar ODMG 3.0.
- Escribir esquemas en **ODL** con atributos, relaciones con inversas, operaciones, *extents* y claves.
- Distinguir los tipos de **colecciones** y de **literales**.
- Comprender los objetos con nombre (*named objects*), el ciclo de vida y los *language bindings*.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    El ODMG fue un grupo de empresas que se puso de acuerdo en un **idioma común** para las bases de datos de objetos, igual que todos los países usan las mismas señales de tránsito. ODL sirve para **dibujar los planos** de los objetos, OQL para **hacerles preguntas**, y los *bindings* son los **traductores** a C++, Java y Smalltalk.

## 1. Componentes del estándar

| Componente | Función |
|---|---|
| **Object Model** | Conceptos: objetos, literales, tipos, propiedades, operaciones, colecciones, relaciones |
| **ODL** (*Object Definition Language*) | Lenguaje de definición de esquemas, independiente del lenguaje de programación; extiende el IDL de OMG/CORBA |
| **OIF** (*Object Interchange Format*) | Formato textual para volcar y cargar objetos entre BD |
| **OQL** (*Object Query Language*) | Lenguaje declarativo de consultas, con sintaxis inspirada en SQL-92 |
| ***Language bindings*** | Integración con C++, Smalltalk y Java (ODL/OML/OQL dentro del lenguaje) |

## 2. El modelo de objetos de ODMG

### Primitivas

- **Objetos** (con OID) y **literales** (sin OID).
- **Propiedades:** *atributos* (valores o referencias) y *relaciones* (asociaciones binarias con inversa).
- **Operaciones:** firmas con parámetros `in`, `out`, `inout`, tipo de retorno y excepciones (`raises`).

### Tipos de literales

| Categoría | Tipos |
|---|---|
| Atómicos | `long`, `long long`, `short`, `unsigned long`, `unsigned short`, `float`, `double`, `boolean`, `octet`, `char`, `string`, `enum` |
| Estructurados | `date`, `time`, `timestamp`, `interval`, `struct` |
| Colección (literal) | `set<t>`, `bag<t>`, `list<t>`, `array<t>`, `dictionary<k,v>` |

### Colecciones como objetos

`Set`, `Bag`, `List`, `Array`, `Dictionary` heredan de `Collection`, con operaciones como `cardinality()`, `is_empty()`, `insert_element()`, `remove_element()`, `contains_element()`, `create_iterator()`.

### La interfaz `Object`

Todo objeto hereda operaciones de ciclo de vida y control:

```text
interface Object {
    void     lock(in Lock_Type mode) raises(LockNotGranted);
    boolean  try_lock(in Lock_Type mode);
    boolean  same_as(in Object anObject);   // identidad
    Object   copy();                        // nueva identidad, mismo estado
    void     delete();
};
```

### Objetos con nombre y puntos de entrada

Una BD expone **raíces** mediante nombres: `db.bind(obj, "Departamento_Ventas")` y `db.lookup("Departamento_Ventas")`. Los *extents* también son puntos de entrada para OQL.

## 3. ODL en la práctica

### Esquema universitario completo

```text
module Universidad {

  struct Direccion { string calle; string ciudad; string cp; };

  enum Grado { LICENCIATURA, MAESTRIA, DOCTORADO };

  class Persona
    ( extent personas
      key curp )
  {
    attribute string    curp;
    attribute string    nombre;
    attribute date      fecha_nacimiento;
    attribute Direccion direccion;          // literal estructurado: sin OID
    short edad();
  };

  class Profesor extends Persona
    ( extent profesores )
  {
    attribute float  salario;
    attribute Grado  grado;
    relationship Departamento pertenece_a
        inverse Departamento::profesores;
    relationship set<Curso> imparte
        inverse Curso::impartido_por;
    void aumentar_salario(in float porcentaje) raises (SalarioInvalido);
  };

  class Estudiante extends Persona
    ( extent estudiantes
      key matricula )
  {
    attribute string matricula;
    relationship set<Inscripcion> inscripciones
        inverse Inscripcion::estudiante;
    float promedio();
  };

  class Departamento
    ( extent departamentos
      key nombre )
  {
    attribute string nombre;
    relationship set<Profesor> profesores
        inverse Profesor::pertenece_a;
    attribute Profesor jefe;               // referencia unidireccional: atributo de tipo objeto, sin inversa
  };

  class Curso
    ( extent cursos
      key (clave, periodo) )               // clave compuesta
  {
    attribute string clave;
    attribute string periodo;
    attribute string titulo;
    attribute short  creditos;
    relationship Profesor impartido_por
        inverse Profesor::imparte;
    relationship set<Inscripcion> inscritos
        inverse Inscripcion::curso;
    relationship set<Curso> prerrequisitos
        inverse Curso::es_prerrequisito_de;
    relationship set<Curso> es_prerrequisito_de
        inverse Curso::prerrequisitos;
  };

  class Inscripcion                         // relación M:N con atributos → se reifica como clase
    ( extent inscripciones )
  {
    attribute float calificacion;
    relationship Estudiante estudiante inverse Estudiante::inscripciones;
    relationship Curso      curso      inverse Curso::inscritos;
  };
};
```

!!! warning "Sobre `jefe`"
    En ODMG, `relationship` **siempre** declara su inversa. Por eso la referencia unidireccional `jefe` se modela como `attribute Profesor jefe;` (atributo de tipo objeto). La diferencia: con `relationship` el sistema **mantiene la integridad referencial** en ambos lados; con `attribute` no.

### Reglas de oro de ODL

| Situación | Modelado |
|---|---|
| Valor sin vida propia, no compartido | `struct` o atributo literal |
| Asociación con integridad en ambos sentidos | `relationship ... inverse ...` |
| 1:N | `set<B>` en un lado, referencia simple en el otro |
| M:N sin atributos | `set<B>` y `set<A>` con inversas |
| M:N **con** atributos | Clase intermedia (`Inscripcion`) |
| Relación recursiva | Dos relaciones inversas en la misma clase (`prerrequisitos` / `es_prerrequisito_de`) |
| Relaciones ternarias o superiores | Siempre se reifican como clase (ODMG solo admite relaciones **binarias**) |

### Integridad referencial automática

Si ejecutas `profesor.imparte.insert_element(curso)`, el sistema actualiza automáticamente `curso.impartido_por = profesor`. Si borras el curso, se elimina de `profesor.imparte`. Esto **no** sucede con atributos de tipo objeto.

## 4. *Language bindings*

### Principios

1. Un **solo sistema de tipos** para el lenguaje y la BD.
2. La sintaxis del lenguaje se respeta: los objetos persistentes se manipulan como objetos normales.
3. La persistencia es (idealmente) **ortogonal** al tipo.

### Binding de Java (precursor de JDO)

```java
Implementation impl = new org.ejemplo.odmg.ImplementationImpl();
Database db = impl.newDatabase();
db.open("universidad", Database.OPEN_READ_WRITE);

Transaction tx = impl.newTransaction();
tx.begin();
Profesor p = new Profesor("CURP123", "Ada Lovelace", 50000f);
db.makePersistent(p);            // o: db.bind(p, "decana")
tx.commit();

tx.begin();
OQLQuery q = impl.newOQLQuery();
q.create("select p from profesores p where p.salario > $1");
q.bind(40000f);
DList resultado = (DList) q.execute();
tx.commit();
db.close();
```

### Operaciones de `Transaction` en ODMG

`begin()`, `commit()`, `abort()`, `checkpoint()` (confirma los cambios **sin liberar los bloqueos** ni terminar la transacción), `join()`, `leave()` (asociar o separar el hilo actual de una transacción).

## 5. OIF: intercambio de objetos

```text
Ada Profesor {
    curp "CURP123",
    nombre "Ada Lovelace",
    salario 50000.0,
    imparte { CursoBD }
}
CursoBD Curso { clave "BD-401", periodo "2026-1", titulo "Bases de datos de objetos" }
```

Los identificadores (`Ada`, `CursoBD`) son **etiquetas** dentro del archivo para expresar referencias; no son los OID reales.

## 6. Legado del ODMG

- JDO adoptó el *binding* de Java; JPA tomó ideas de JDO y de Hibernate.
- OQL inspiró **JPQL/HQL**, **EJB QL** y los lenguajes de consulta por rutas.
- La noción de relaciones con inversas gestionadas aparece en JPA (`mappedBy`) — aunque allí **la aplicación** debe mantener coherentes ambos lados en memoria.

## Errores comunes

- ❌ Declarar una `relationship` sin `inverse`.
- ❌ Modelar una relación ternaria directamente (ODMG solo tiene relaciones binarias).
- ❌ Pensar que `checkpoint()` termina la transacción.
- ❌ Usar `copy()` esperando conservar la identidad: `copy()` crea un objeto **nuevo**.

## Conexiones (intercalación)

- `extent` ↔ inclusión de *extents* ([Lección 02](02-modelo-de-objetos.md)).
- `relationship` ↔ `mappedBy` en JPA ([Lección 10](10-orm.md)).
- `checkpoint()` ↔ transacciones largas ([Lección 07](07-transacciones.md)).

## Preguntas de recuerdo activo

1. Nombra los cinco componentes del estándar ODMG.
2. ¿Qué hace el sistema cuando una `relationship` tiene `inverse`?
3. ¿Cómo modelas una relación M:N con atributos en ODL?
4. ¿Qué diferencia hay entre `EXTENDS` y `:` en ODL?
5. ¿Qué hace `checkpoint()`?

??? success "Respuestas"
    1. Object Model, ODL, OIF, OQL y *language bindings*.
    2. Mantiene automáticamente la integridad referencial en ambos lados.
    3. Reificándola como una clase intermedia con dos relaciones hacia las clases participantes.
    4. `EXTENDS` hereda estado y comportamiento de una sola clase; `:` hereda comportamiento (interfaces) y admite herencia múltiple.
    5. Hace permanentes los cambios hechos hasta ese momento sin terminar la transacción ni liberar bloqueos.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| OIF | *Object Interchange Format*: formato textual para volcar y cargar objetos |
| Clave compuesta en ODL | `key (clave, periodo)` |
| ¿Relaciones n-arias en ODMG? | No; solo binarias. Las n-arias se reifican como clase |
| `same_as()` | Prueba de identidad entre objetos |
| Colecciones ODMG | Set, Bag, List, Array, Dictionary |

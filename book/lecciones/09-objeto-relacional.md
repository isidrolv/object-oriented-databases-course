# Lección 09 · Bases de datos objeto-relacionales

## Objetivos

- Conocer las extensiones de objetos de **SQL:1999** y **SQL:2003**: tipos estructurados, métodos, tablas tipadas, `REF`, herencia de tipos y de tablas, `ARRAY` y `MULTISET`.
- Implementar un modelo objeto-relacional en **Oracle** y en **PostgreSQL**.
- Explicar las limitaciones de la herencia de tablas de PostgreSQL.
- Decidir cuándo un SGBD objeto-relacional (SGBDOR) es preferible a un OODBMS o a un ORM.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Una casa de ladrillos (el modelo relacional) funciona muy bien. En vez de tirarla para construir una casa nueva de madera (la BDOO), le agregamos **cuartos nuevos**: tipos propios, flechas entre cosas y familias de tablas. Sigue siendo la misma casa, pero ahora entiende un poco de objetos.

## 1. Extensiones del estándar SQL

| Característica | Estándar | Idea |
|---|---|---|
| Tipos estructurados de usuario (UDT) | SQL:1999 | `CREATE TYPE ... AS (...)` con atributos y **métodos** |
| Herencia de tipos | SQL:1999 | `CREATE TYPE b UNDER a`; `NOT FINAL`, `INSTANTIABLE` |
| Tablas tipadas | SQL:1999 | `CREATE TABLE t OF tipo` → cada fila es un objeto con identificador |
| Subtablas | SQL:1999 | `CREATE TABLE hija OF b UNDER madre` |
| Tipo `REF` | SQL:1999 | Referencia a una fila de una tabla tipada; desreferencia con `->` o `DEREF` |
| `ARRAY` | SQL:1999 | Colección ordenada acotada |
| `MULTISET` | SQL:2003 | *Bag* sin orden (colección anidada) |
| Funciones de tabla, `XML` | SQL:2003 | Integración con otros modelos |

### Sintaxis estándar (SQL:1999)

```sql
CREATE TYPE direccion_t AS (
    calle  VARCHAR(60),
    ciudad VARCHAR(40)
) NOT FINAL;

CREATE TYPE persona_t AS (
    nombre    VARCHAR(60),
    domicilio direccion_t
) NOT FINAL
  REF IS SYSTEM GENERATED
  METHOD descripcion() RETURNS VARCHAR(100);

CREATE TYPE profesor_t UNDER persona_t AS (
    salario DECIMAL(12,2)
) NOT FINAL
  OVERRIDING METHOD descripcion() RETURNS VARCHAR(100);

CREATE TABLE personas   OF persona_t  (REF IS oid SYSTEM GENERATED);
CREATE TABLE profesores OF profesor_t UNDER personas;

CREATE TABLE cursos (
    clave    VARCHAR(10) PRIMARY KEY,
    titulo   VARCHAR(80),
    profesor REF(profesor_t) SCOPE profesores
);

-- Desreferencia con el operador ->
SELECT c.titulo, c.profesor->nombre, c.profesor->descripcion()
FROM cursos c;
```

## 2. Oracle: tipos de objeto

```sql
CREATE TYPE direccion_t AS OBJECT (
    calle  VARCHAR2(60),
    ciudad VARCHAR2(40)
);
/
CREATE TYPE persona_t AS OBJECT (
    id        NUMBER,
    nombre    VARCHAR2(60),
    domicilio direccion_t,
    MEMBER FUNCTION descripcion RETURN VARCHAR2
) NOT FINAL;
/
CREATE TYPE BODY persona_t AS
    MEMBER FUNCTION descripcion RETURN VARCHAR2 IS
    BEGIN
        RETURN nombre || ' (' || domicilio.ciudad || ')';
    END;
END;
/
CREATE TYPE profesor_t UNDER persona_t (
    salario NUMBER(12,2),
    OVERRIDING MEMBER FUNCTION descripcion RETURN VARCHAR2
);
/
CREATE TYPE BODY profesor_t AS
    OVERRIDING MEMBER FUNCTION descripcion RETURN VARCHAR2 IS
    BEGIN
        RETURN 'Prof. ' || nombre || ' - $' || salario;
    END;
END;
/
-- Tabla de objetos: cada fila tiene un OID; acepta subtipos (sustituibilidad)
CREATE TABLE personas OF persona_t (PRIMARY KEY (id));

CREATE TYPE lista_texto_t AS TABLE OF VARCHAR2(40);
/
CREATE TYPE curso_t AS OBJECT (
    clave     VARCHAR2(10),
    titulo    VARCHAR2(80),
    profesor  REF persona_t,
    horarios  lista_texto_t    -- colección anidada (tabla anidada)
);
/
CREATE TABLE cursos OF curso_t (
    PRIMARY KEY (clave),
    profesor SCOPE IS personas
) NESTED TABLE horarios STORE AS cursos_horarios_nt;

INSERT INTO personas VALUES (persona_t(1, 'Ana', direccion_t('Reforma 10', 'CDMX')));
INSERT INTO personas VALUES (profesor_t(2, 'Ada', direccion_t('Juárez 5', 'Monterrey'), 55000));

INSERT INTO cursos
SELECT 'BD-401', 'Bases de datos de objetos', REF(p), lista_texto_t('Lun 9:00', 'Mié 9:00')
FROM personas p WHERE p.id = 2;

-- Navegación por REF (desreferencia implícita con punto) y ligadura tardía
SELECT c.titulo, c.profesor.nombre, c.profesor.descripcion() FROM cursos c;
--  Bases de datos de objetos | Ada | Prof. Ada - $55000

-- Polimorfismo: filtrar por subtipo y "bajar" de tipo
SELECT TREAT(VALUE(p) AS profesor_t).salario
FROM personas p
WHERE VALUE(p) IS OF (profesor_t);

-- Desanidar una colección
SELECT c.clave, h.COLUMN_VALUE AS horario
FROM cursos c, TABLE(c.horarios) h;
```

| Operador Oracle | Propósito |
|---|---|
| `REF(alias)` | Obtiene la referencia a una fila objeto |
| `DEREF(ref)` | Obtiene el objeto apuntado |
| `VALUE(alias)` | Devuelve la fila como instancia del tipo |
| `TREAT(expr AS tipo)` | *Downcast* |
| `IS OF (tipo)` | Prueba de tipo |
| `IS DANGLING` | Detecta referencias colgantes |
| `TABLE(col)` | Desanida una tabla anidada o un `VARRAY` |

## 3. PostgreSQL: tipos compuestos, arreglos y herencia de tablas

```sql
CREATE TYPE direccion AS (calle text, ciudad text, cp char(5));

CREATE TABLE persona (
    id        serial PRIMARY KEY,
    nombre    text NOT NULL,
    domicilio direccion,
    telefonos text[]
);

CREATE TABLE profesor (
    salario numeric(12,2)
) INHERITS (persona);

INSERT INTO persona (nombre, domicilio, telefonos)
VALUES ('Ana', ROW('Reforma 10', 'CDMX', '06600'), ARRAY['555-1000', '555-2000']);

INSERT INTO profesor (nombre, domicilio, salario)
VALUES ('Ada', ROW('Juárez 5', 'Monterrey', '64000'), 55000);

-- Consulta polimórfica: incluye las filas de profesor
SELECT nombre, (domicilio).ciudad, tableoid::regclass AS tabla_real
FROM persona;
--  Ana | CDMX      | persona
--  Ada | Monterrey | profesor

-- Solo la tabla madre
SELECT nombre FROM ONLY persona;

-- "Método" como función sobre el tipo fila; se puede invocar con notación de atributo
CREATE FUNCTION etiqueta(p persona) RETURNS text
LANGUAGE sql IMMUTABLE AS $$ SELECT p.nombre || ' (' || (p.domicilio).ciudad || ')' $$;

SELECT p.etiqueta FROM persona p;          -- equivalente a etiqueta(p)

-- Arreglos
SELECT nombre FROM persona WHERE '555-1000' = ANY (telefonos);
SELECT nombre, unnest(telefonos) FROM persona;
```

!!! warning "Limitaciones de `INHERITS` en PostgreSQL"
    - Las **claves primarias, restricciones `UNIQUE` y llaves foráneas no se heredan** a las tablas hijas: puede haber dos filas con el mismo `id` (una en `persona` y otra en `profesor`) y una FK hacia `persona` **no** ve las filas de `profesor`.
    - Los índices se crean **por tabla**.
    - No existe el tipo `REF` ni métodos con ligadura tardía; los «métodos» son funciones.
    - Hoy `INHERITS` se usa poco para modelar objetos; para particionar se prefiere el particionamiento declarativo, y para estructuras flexibles, `jsonb`.

## 4. Comparativa

| Criterio | OODBMS puro | SGBD objeto-relacional | ORM sobre relacional |
|---|---|---|---|
| Dónde vive el modelo | En el motor | En el SQL | En la aplicación |
| Lenguaje de consulta | OQL / API nativa | SQL extendido | JPQL / Criteria / LINQ + SQL |
| Métodos | En el lenguaje de la aplicación | En PL/SQL, SQL o Java dentro del motor | En la aplicación |
| Identidad | OID | OID de fila objeto (Oracle) o clave | Clave primaria + *identity map* |
| Herramientas de BI | Escasas | Completas | Completas (sobre las tablas) |
| Portabilidad | Baja | Media (cada proveedor difiere del estándar) | Alta |

## 5. ¿Cuándo usar un SGBDOR?

- Dominios con **tipos ricos** (geometría, series de tiempo, dinero, rangos) que conviene manipular en SQL: p. ej., **PostGIS** se construye sobre la extensibilidad de PostgreSQL (tipos, operadores e índices GiST).
- Necesidad de **SQL estándar + BI** con algo de modelado de objetos.
- Equipos con experiencia en SQL que no quieren un OODBMS de nicho.

## Errores comunes

- ❌ Esperar que una FK hacia una tabla madre en PostgreSQL vea las filas de las tablas hijas.
- ❌ Usar `REF` sin `SCOPE` en Oracle (referencias más grandes y sin restricción a una tabla).
- ❌ Creer que los tipos de Oracle y la sintaxis SQL:1999 son idénticos (Oracle usa `AS OBJECT`, `MEMBER FUNCTION`, `REF(p)`).
- ❌ Olvidar los paréntesis al acceder a un campo compuesto en PostgreSQL: `(domicilio).ciudad`.

## Conexiones (intercalación)

- `REF` ↔ OID ([Lección 02](02-modelo-de-objetos.md)).
- Herencia de tablas ↔ estrategias de herencia de JPA ([Lección 10](10-orm.md)).
- Índices GiST y tipos extensibles ↔ extensibilidad del Manifiesto ([Lección 01](01-fundamentos.md)).

## Preguntas de recuerdo activo

1. ¿Qué estándar introdujo `REF` y tablas tipadas? ¿Y `MULTISET`?
2. ¿Qué hace `TREAT` en Oracle?
3. ¿Qué devuelve `SELECT * FROM persona` si `profesor INHERITS (persona)`?
4. ¿Qué restricciones **no** se heredan en PostgreSQL?
5. ¿Cuál es el operador estándar para desreferenciar un `REF`?

??? success "Respuestas"
    1. SQL:1999; `MULTISET` llegó en SQL:2003.
    2. Convierte una expresión a un subtipo (*downcast*); devuelve `NULL` si el objeto no es de ese subtipo.
    3. Las filas de `persona` y las de `profesor` (solo con las columnas de `persona`); para excluir a las hijas se usa `ONLY`.
    4. `PRIMARY KEY`, `UNIQUE` y llaves foráneas (ni como origen ni como destino respecto a las hijas).
    5. `->` (por ejemplo, `c.profesor->nombre`), o `DEREF(...)`.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Tabla tipada | `CREATE TABLE t OF tipo`; cada fila es una instancia con identificador |
| `NOT FINAL` | Permite crear subtipos del tipo |
| `SCOPE IS` | Restringe un `REF` a una tabla de objetos concreta |
| `ONLY` en PostgreSQL | Consulta la tabla sin sus tablas hijas |
| Tabla anidada en Oracle | Colección sin límite almacenada en una tabla separada (`STORE AS`) |

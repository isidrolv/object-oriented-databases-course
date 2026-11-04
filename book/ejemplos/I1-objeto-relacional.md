# I1 · El mismo dominio en PostgreSQL y Oracle

**Nivel:** 🟡 Intermedio · **Lección:** [09](../lecciones/09-objeto-relacional.md) · **Tiempo:** 60 min · **Requiere:** PostgreSQL 14+ (Docker) y, opcionalmente, Oracle Free

## 1. Planteamiento del problema

Una aseguradora maneja **pólizas** de distintos tipos: `PolizaAuto` (placa, valor del vehículo) y `PolizaVida` (suma asegurada, beneficiarios). Toda póliza tiene folio, titular (con domicilio) y un método `prima()` cuyo cálculo **depende del tipo**:

- Auto: 4 % del valor del vehículo.
- Vida: 0.5 % de la suma asegurada + 200 por cada beneficiario.

Debes implementar el modelo con **tipos y herencia** en PostgreSQL y en Oracle, y escribir la consulta polimórfica «prima de todas las pólizas de titulares que viven en Puebla».

## 2. Escenario de ejecución

```bash
docker run --name pg-i1 -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
docker exec -it pg-i1 psql -U postgres
```

Datos iniciales:

| Folio | Tipo | Titular | Ciudad | Datos |
|---|---|---|---|---|
| A-1 | Auto | Luis | Puebla | valor 300 000 |
| A-2 | Auto | Marta | CDMX | valor 500 000 |
| V-1 | Vida | Luis | Puebla | suma 1 000 000; beneficiarios: Ana, Pepe |

## 3. Entradas y salidas

| Entrada | Salida esperada |
|---|---|
| Esquema y datos anteriores | `A-1 → 12000.00`, `V-1 → 5400.00` (solo Puebla) |
| `SELECT ... FROM ONLY poliza` (PostgreSQL) | 0 filas (todas las pólizas viven en tablas hijas) |
| Intento de insertar `A-1` duplicado en `poliza_vida` | **Se acepta** en PostgreSQL (explica por qué es un problema) |

## 4. Solución propuesta incompleta

### PostgreSQL

```sql
CREATE TYPE domicilio AS (calle text, ciudad text);

CREATE TABLE poliza (
    folio   text PRIMARY KEY,
    titular text NOT NULL,
    dom     ________
);

CREATE TABLE poliza_auto (placa text, valor numeric(12,2)) ________ (poliza);
CREATE TABLE poliza_vida (suma numeric(14,2), beneficiarios text[]) ________ (poliza);

INSERT INTO poliza_auto VALUES ('A-1', 'Luis',  ROW('5 de Mayo 1', 'Puebla'), 'PUE-123', 300000);
INSERT INTO poliza_auto VALUES ('A-2', 'Marta', ROW('Reforma 9', 'CDMX'),     'CDM-999', 500000);
INSERT INTO poliza_vida VALUES ('V-1', 'Luis',  ROW('5 de Mayo 1', 'Puebla'), 1000000, ARRAY['Ana','Pepe']);

-- "Método" polimórfico: completa el cálculo según la tabla real de la fila.
-- Ojo: un valor compuesto (fila) no transporta columnas de sistema como tableoid,
-- así que la tabla real se pasa como parámetro.
CREATE FUNCTION prima(t regclass, f text) RETURNS numeric LANGUAGE sql STABLE AS $$
    SELECT CASE t::text
             WHEN 'poliza_auto' THEN (SELECT ________ FROM poliza_auto a WHERE a.folio = f)
             WHEN 'poliza_vida' THEN (SELECT ________ FROM poliza_vida v WHERE v.folio = f)
           END
$$;

SELECT p.folio, ________ AS prima
FROM poliza p
WHERE ________ = 'Puebla';
```

### Oracle

```sql
CREATE TYPE domicilio_t AS OBJECT (calle VARCHAR2(60), ciudad VARCHAR2(40));
/
CREATE TYPE poliza_t AS OBJECT (
    folio   VARCHAR2(10),
    titular VARCHAR2(60),
    dom     domicilio_t,
    ________ FUNCTION prima RETURN NUMBER
) ________;
/
CREATE TYPE nombres_t AS VARRAY(10) OF VARCHAR2(60);
/
CREATE TYPE poliza_auto_t ________ poliza_t (
    placa VARCHAR2(10), valor NUMBER(12,2),
    ________ MEMBER FUNCTION prima RETURN NUMBER
);
/
-- ... poliza_vida_t, cuerpos de tipo, tabla de objetos y consulta
```

---

## 5. Respuesta correcta esperada

??? success "PostgreSQL"

    ```sql
    CREATE TYPE domicilio AS (calle text, ciudad text);

    CREATE TABLE poliza (
        folio   text PRIMARY KEY,
        titular text NOT NULL,
        dom     domicilio
    );

    CREATE TABLE poliza_auto (placa text, valor numeric(12,2)) INHERITS (poliza);
    CREATE TABLE poliza_vida (suma numeric(14,2), beneficiarios text[]) INHERITS (poliza);

    INSERT INTO poliza_auto VALUES ('A-1', 'Luis',  ROW('5 de Mayo 1', 'Puebla'), 'PUE-123', 300000);
    INSERT INTO poliza_auto VALUES ('A-2', 'Marta', ROW('Reforma 9', 'CDMX'),     'CDM-999', 500000);
    INSERT INTO poliza_vida VALUES ('V-1', 'Luis',  ROW('5 de Mayo 1', 'Puebla'), 1000000, ARRAY['Ana','Pepe']);

    CREATE FUNCTION prima(t regclass, f text) RETURNS numeric LANGUAGE sql STABLE AS $$
        SELECT CASE t::text
                 WHEN 'poliza_auto' THEN (SELECT a.valor * 0.04
                                          FROM poliza_auto a WHERE a.folio = f)
                 WHEN 'poliza_vida' THEN (SELECT v.suma * 0.005 + 200 * cardinality(v.beneficiarios)
                                          FROM poliza_vida v WHERE v.folio = f)
               END
    $$;

    SELECT p.folio, round(prima(p.tableoid, p.folio), 2) AS prima
    FROM poliza p
    WHERE (p.dom).ciudad = 'Puebla'
    ORDER BY p.folio;
    --  A-1 | 12000.00
    --  V-1 |  5400.00

    SELECT count(*) FROM ONLY poliza;     -- 0

    -- El duplicado se acepta: la PK de poliza NO se hereda como restricción global
    INSERT INTO poliza_vida VALUES ('A-1', 'X', ROW('-', 'Puebla'), 1, ARRAY[]::text[]);
    ```

    **Por qué es un problema:** la unicidad de `folio` solo se garantiza **dentro de cada tabla**. Hay dos pólizas `A-1` y una FK hacia `poliza(folio)` no vería ninguna de las dos. Soluciones: una secuencia común con un prefijo por tipo y un `CHECK`, una tabla de registro de folios con FK desde cada hija, o modelar con una sola tabla y `jsonb`.

    **Nota de diseño:** el `CASE` sobre `tableoid` (que se pasa explícitamente porque un valor de fila no incluye columnas de sistema) muestra que PostgreSQL **no tiene ligadura tardía**: el «polimorfismo» se simula a mano. Esa es la diferencia clave con Oracle.

??? success "Oracle"

    ```sql
    CREATE TYPE domicilio_t AS OBJECT (calle VARCHAR2(60), ciudad VARCHAR2(40));
    /
    CREATE TYPE poliza_t AS OBJECT (
        folio   VARCHAR2(10),
        titular VARCHAR2(60),
        dom     domicilio_t,
        NOT INSTANTIABLE MEMBER FUNCTION prima RETURN NUMBER   -- método abstracto
    ) NOT INSTANTIABLE NOT FINAL;
    /
    CREATE TYPE nombres_t AS VARRAY(10) OF VARCHAR2(60);
    /
    CREATE TYPE poliza_auto_t UNDER poliza_t (
        placa VARCHAR2(10), valor NUMBER(12,2),
        OVERRIDING MEMBER FUNCTION prima RETURN NUMBER
    );
    /
    CREATE TYPE poliza_vida_t UNDER poliza_t (
        suma NUMBER(14,2), beneficiarios nombres_t,
        OVERRIDING MEMBER FUNCTION prima RETURN NUMBER
    );
    /
    CREATE TYPE BODY poliza_auto_t AS
        OVERRIDING MEMBER FUNCTION prima RETURN NUMBER IS
        BEGIN RETURN valor * 0.04; END;
    END;
    /
    CREATE TYPE BODY poliza_vida_t AS
        OVERRIDING MEMBER FUNCTION prima RETURN NUMBER IS
        BEGIN RETURN suma * 0.005 + 200 * beneficiarios.COUNT; END;
    END;
    /
    CREATE TABLE polizas OF poliza_t (PRIMARY KEY (folio));   -- una PK real para toda la jerarquía

    INSERT INTO polizas VALUES (poliza_auto_t('A-1', 'Luis',  domicilio_t('5 de Mayo 1', 'Puebla'), 'PUE-123', 300000));
    INSERT INTO polizas VALUES (poliza_auto_t('A-2', 'Marta', domicilio_t('Reforma 9', 'CDMX'),     'CDM-999', 500000));
    INSERT INTO polizas VALUES (poliza_vida_t('V-1', 'Luis',  domicilio_t('5 de Mayo 1', 'Puebla'), 1000000, nombres_t('Ana', 'Pepe')));

    SELECT p.folio, p.prima() AS prima          -- ligadura tardía real
    FROM polizas p
    WHERE p.dom.ciudad = 'Puebla'
    ORDER BY p.folio;
    --  A-1 | 12000
    --  V-1 |  5400
    ```

    `poliza_t` es `NOT INSTANTIABLE` (abstracta) y su método, también `NOT INSTANTIABLE`, no tiene cuerpo: cada subtipo lo redefine con `OVERRIDING`. La tabla de objetos `polizas` es **sustituible**: guarda instancias de cualquier subtipo con **una sola PK**.

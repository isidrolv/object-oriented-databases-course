# Lección 01 · Fundamentos y motivación

## Objetivos

Al terminar podrás:

- Definir qué es una Base de Datos Orientada a Objetos (BDOO) y un OODBMS.
- Explicar el **desajuste de impedancia** (*impedance mismatch*) en sus siete dimensiones.
- Situar históricamente las BDOO: manifiestos, ODMG y sistemas pioneros.
- Enumerar las 13 características obligatorias del *Manifiesto de BDOO* de 1989.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Imagina que armas un robot de LEGO. En una base de datos relacional, para guardarlo tienes que **desarmarlo** pieza por pieza y meter cada pieza en una caja distinta según su color. Al día siguiente, para jugar, tienes que **volver a armarlo** leyendo un instructivo. Una base de datos orientada a objetos es una repisa donde **dejas el robot armado**: lo guardas tal como está y lo recoges tal como lo dejaste.

## 1. Definiciones

- **Objeto:** entidad con **identidad**, **estado** (atributos) y **comportamiento** (métodos).
- **Base de datos orientada a objetos (BDOO):** colección persistente de objetos que conserva identidad, estructura compleja, relaciones y comportamiento.
- **OODBMS (*Object-Oriented Database Management System*):** software que gestiona una BDOO y ofrece las capacidades de un SGBD (persistencia, concurrencia, recuperación, consultas *ad hoc*, gestión de almacenamiento secundario) **y** las de un lenguaje orientado a objetos (encapsulamiento, herencia, polimorfismo, extensibilidad).

Fórmula clásica (Atkinson et al., 1989):

```text
OODBMS = Sistema orientado a objetos + Sistema de base de datos
```

## 2. El desajuste de impedancia

El término viene de la electrónica: cuando dos circuitos tienen impedancias distintas, la señal se pierde en la frontera. En software, la «frontera» es la que hay entre el **modelo de objetos** de la aplicación y el **modelo relacional** del almacenamiento.

| Dimensión | Mundo de objetos | Mundo relacional |
|---|---|---|
| **Estructura** | Grafos de objetos anidados, colecciones, referencias | Tablas planas, valores atómicos (1FN) |
| **Identidad** | Identidad intrínseca (referencia / OID) | Identidad por valor de la clave primaria |
| **Encapsulamiento** | Estado privado tras métodos | Todo columna es pública para SQL |
| **Herencia** | Jerarquías de clases y polimorfismo | No existe en el modelo relacional puro |
| **Navegación** | Se recorren referencias: `pedido.cliente.direccion` | Se combinan conjuntos: `JOIN` |
| **Sistema de tipos** | Tipos del lenguaje (`String`, `BigDecimal`, `List<T>`) | Tipos SQL (`VARCHAR(n)`, `NUMERIC(p,s)`) |
| **Granularidad transaccional** | Objeto en memoria, ciclo de vida largo | Filas, sentencias, transacciones cortas |

### Ejemplo: el mismo pedido en ambos mundos

```java
// Mundo de objetos (Java)
class Cliente  { String nombre; Direccion direccion; List<Pedido> pedidos; }
class Pedido   { LocalDate fecha; Cliente cliente; List<Linea> lineas;
                 BigDecimal total() { return lineas.stream()
                     .map(Linea::subtotal).reduce(BigDecimal.ZERO, BigDecimal::add); } }
class Linea    { Producto producto; int cantidad;
                 BigDecimal subtotal() { return producto.precio.multiply(BigDecimal.valueOf(cantidad)); } }
```

```sql
-- Mundo relacional: el grafo se "aplana" en 4 tablas
CREATE TABLE cliente  (id BIGINT PRIMARY KEY, nombre VARCHAR(100), calle VARCHAR(100), ciudad VARCHAR(60));
CREATE TABLE pedido   (id BIGINT PRIMARY KEY, fecha DATE, cliente_id BIGINT REFERENCES cliente(id));
CREATE TABLE producto (id BIGINT PRIMARY KEY, nombre VARCHAR(100), precio NUMERIC(12,2));
CREATE TABLE linea    (pedido_id BIGINT REFERENCES pedido(id), producto_id BIGINT REFERENCES producto(id),
                       cantidad INT, PRIMARY KEY (pedido_id, producto_id));

-- Reconstruir un pedido exige joins y código de ensamblado; el método total() no vive en la BD.
SELECT p.id, p.fecha, c.nombre, SUM(pr.precio * l.cantidad) AS total
FROM pedido p JOIN cliente c ON c.id = p.cliente_id
              JOIN linea l ON l.pedido_id = p.id
              JOIN producto pr ON pr.id = l.producto_id
GROUP BY p.id, p.fecha, c.nombre;
```

En una BDOO, el pedido se guarda **tal cual** y se recupera navegando:

```python
# ZODB (Python): persistencia de objetos nativa
total = root['pedidos'][1001].total()      # el método viaja con el objeto
ciudad = root['pedidos'][1001].cliente.direccion.ciudad   # navegación directa
```

## 3. Línea del tiempo

| Año | Hito |
|---|---|
| 1967 | Simula 67 introduce clases y objetos |
| 1970 | Codd publica el modelo relacional |
| 1980 | Smalltalk-80 populariza la orientación a objetos |
| 1986–1988 | Primeros OODBMS comerciales: **GemStone** (Servio Logic, basado en Smalltalk), **Vbase/ONTOS**, **ObjectStore** (Object Design), **Versant**, **Objectivity/DB**; prototipos de investigación **ORION** (MCC, Won Kim) e **Iris** (HP) |
| 1989 | ***The Object-Oriented Database System Manifesto*** (Atkinson, Bancilhon, DeWitt, Dittrich, Maier, Zdonik) |
| 1990 | *Third-Generation Database System Manifesto* (Stonebraker y colegas): propone **extender** el modelo relacional en vez de sustituirlo |
| 1991 | Se funda el **ODMG** (*Object Data Management Group*), liderado por Rick Cattell |
| 1993 | ODMG-93 (versión 1.0) |
| 1995 | *The Third Manifesto* (Date y Darwen): modelo relacional con tipos ricos, crítico de los punteros |
| 1997 / 2000 | ODMG 2.0 y **ODMG 3.0** |
| 1999 | **SQL:1999** incorpora tipos estructurados de usuario, `REF` y herencia → SGBD objeto-relacionales |
| 2001 | El ODMG se disuelve; su *binding* de Java pasa a **JDO** (JSR 12) |
| 2006 | **JPA 1.0** (JSR 220) estandariza el ORM en Java |
| 2000s–hoy | db4o, ObjectDB, ZODB, Realm, InterSystems Caché/IRIS; el modelo de objetos influye en las BD de documentos y grafos |

## 4. El Manifiesto de 1989: las 13 reglas obligatorias

Agrupadas en dos bloques: **8 de orientación a objetos** y **5 de base de datos**.

| # | Característica | Bloque |
|---|---|---|
| 1 | Objetos complejos (constructores tuple, set, list, bag, array) | OO |
| 2 | Identidad de objetos | OO |
| 3 | Encapsulamiento | OO |
| 4 | Tipos o clases | OO |
| 5 | Jerarquías de tipos o clases (herencia) | OO |
| 6 | Sobrescritura, sobrecarga y ligadura tardía | OO |
| 7 | Completitud computacional | OO |
| 8 | Extensibilidad (tipos definidos por el usuario tratados igual que los del sistema) | OO |
| 9 | Persistencia | BD |
| 10 | Gestión de almacenamiento secundario (índices, *clustering*, *buffering*, optimización) | BD |
| 11 | Concurrencia | BD |
| 12 | Recuperación | BD |
| 13 | Facilidad de consultas *ad hoc* | BD |

**Características opcionales:** herencia múltiple, verificación e inferencia de tipos, distribución, transacciones de diseño, versiones.
**Opciones abiertas:** paradigma de programación, sistema de representación, sistema de tipos, uniformidad.

!!! example "Regla mnemotécnica"
    **«CICTH-SCE / PGCRC»** → *Complejos, Identidad, enCapsulamiento, Tipos, Herencia — Sobrescritura, Completitud, Extensibilidad / Persistencia, Gestión, Concurrencia, Recuperación, Consultas*.

## 5. Tres caminos para persistir objetos

```text
           ┌────────────────────────────┐
           │  Modelo de objetos de app  │
           └─────────────┬──────────────┘
      ┌──────────────────┼───────────────────┐
      ▼                  ▼                   ▼
 BDOO pura          Objeto-relacional      ORM sobre relacional
 (GemStone,         (PostgreSQL, Oracle    (Hibernate/JPA,
  ObjectStore,       tipos, REF, herencia   Entity Framework,
  ObjectDB, ZODB)    de tablas)             SQLAlchemy)
 El motor entiende  El SQL entiende         La aplicación traduce
 objetos            algunos objetos         objetos ↔ tablas
```

## 6. ¿Por qué la BDOO no reemplazó a la relacional?

Respuesta experta (pregunta frecuente en entrevistas):

1. **Inercia y ecosistema:** inversión enorme en SQL, herramientas de BI, DBAs, informes.
2. **Ausencia de una base formal tan sólida** como el álgebra relacional; OQL llegó tarde y se implementó parcialmente.
3. **Acoplamiento al lenguaje:** muchos OODBMS ataban la BD a C++ o Smalltalk; varias aplicaciones en distintos lenguajes compartían peor los datos.
4. **El relacional absorbió ideas:** SQL:1999 (objeto-relacional) y los ORM redujeron el dolor del desajuste.
5. **Consultas *ad hoc* y *reporting***: el modelo relacional es superior para consultas imprevistas sobre conjuntos.

Pero las BDOO **ganaron en nichos**: CAD/CAM, telecomunicaciones, simulación, física de altas energías (Objectivity/DB en el CERN y en SLAC/BaBar), sistemas financieros de baja latencia (GemStone), dispositivos móviles (db4o, Realm) y sistemas con dominios muy complejos y navegación intensiva.

## Errores comunes

- ❌ «Una BDOO es solo serializar objetos a un archivo.» → La serialización no ofrece concurrencia, transacciones, consultas ni carga parcial.
- ❌ «El OID es la clave primaria.» → El OID es independiente del valor y lo genera el sistema (lección 02).
- ❌ «ORM = BDOO.» → Un ORM es una capa de traducción sobre un SGBD relacional; el motor no conoce los objetos.
- ❌ «Las BDOO están muertas.» → Siguen vivas en nichos y sus ideas viven en ORM, BD de documentos y grafos.

## Conexiones (intercalación)

- Identidad → [Lección 02](02-modelo-de-objetos.md) y *identity map* en [Lección 10](10-orm.md).
- Consultas *ad hoc* → [OQL](04-oql.md) y [optimización](11-optimizacion.md).
- Alternativa relacional extendida → [Lección 09](09-objeto-relacional.md).

## Preguntas de recuerdo activo

1. Define OODBMS con la fórmula de Atkinson et al.
2. Menciona cuatro dimensiones del desajuste de impedancia.
3. ¿Qué diferencia hay entre el Manifiesto de 1989 y el de la tercera generación de 1990?
4. ¿Qué pasó con el *binding* de Java del ODMG?
5. Nombra cinco de las 13 características obligatorias.

??? success "Respuestas"
    1. OODBMS = sistema orientado a objetos + sistema de base de datos.
    2. Estructura, identidad, encapsulamiento, herencia, navegación vs conjuntos, tipos, granularidad transaccional (cualquiera de cuatro).
    3. El de 1989 propone un SGBD de objetos nuevo; el de 1990 propone extender el modelo relacional con capacidades de objetos manteniendo SQL.
    4. Se convirtió en la base de JDO (JSR 12) tras la disolución del ODMG en 2001.
    5. Objetos complejos, identidad, encapsulamiento, tipos/clases, herencia, sobrescritura/ligadura tardía, completitud computacional, extensibilidad, persistencia, almacenamiento secundario, concurrencia, recuperación, consultas *ad hoc*.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Desajuste de impedancia | Diferencias estructurales y semánticas entre el modelo de objetos de la aplicación y el modelo relacional de almacenamiento |
| Autores del Manifiesto de 1989 | Atkinson, Bancilhon, DeWitt, Dittrich, Maier y Zdonik |
| Año y versión final del ODMG | ODMG 3.0, año 2000; el grupo se disolvió en 2001 |
| 13 reglas: ¿cuántas son OO y cuántas BD? | 8 de orientación a objetos y 5 de base de datos |
| Nicho clásico de las BDOO | CAD/CAM, telecomunicaciones, física de altas energías, finanzas de baja latencia, móviles |

# Lección 12 · Sistemas reales y ecosistema

## Objetivos

- Describir la arquitectura y el nicho de los principales OODBMS: **GemStone/S, ObjectStore, Versant, Objectivity/DB, InterSystems IRIS, ObjectDB, db4o, ZODB, Realm y ObjectBox**.
- Comparar las BDOO con las bases de **documentos** y de **grafos**.
- Construir una **matriz de decisión** ponderada.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Hay muchas marcas de bicicletas: unas para montaña, otras para carreras, otras para niños. Todas tienen dos ruedas y pedales (identidad, objetos, persistencia), pero cada una está hecha para un camino distinto. Conocer las marcas te ayuda a elegir la bici adecuada para cada ruta.

## 1. Panorama de sistemas

| Sistema | Lenguajes | Arquitectura destacada | Nicho típico | Situación |
|---|---|---|---|---|
| **GemStone/S** | Smalltalk (y acceso desde otros lenguajes) | Servidor de objetos que **ejecuta métodos en el servidor**; caché compartida; GC persistente; *class history* | Finanzas, logística, sistemas de misión crítica | Activo (GemTalk Systems) |
| **ObjectStore** | C++, Java | **Servidor de páginas** con *swizzling* por memoria virtual (mapeo de páginas a direcciones del proceso) | CAD, telecomunicaciones, sistemas embebidos | Hoy en manos de Ignite Technologies |
| **Versant Object Database** | C++, Java | **Servidor de objetos**, OID lógicos, evolución perezosa de esquema, distribución | Telecomunicaciones, defensa, transporte | Línea de Actian |
| **Objectivity/DB** | C++, Java, Python | BD **federada y distribuida** (federación → BD → contenedor → página → objeto); OID estructurados | Física de altas energías (experimento BaBar en SLAC, escala de petabytes), inteligencia, telecomunicaciones | Activo (Objectivity Inc.) |
| **InterSystems Caché / IRIS** | ObjectScript, Java, .NET, Python | **Multimodelo** sobre *globals* (arreglos dispersos multidimensionales); cada clase se proyecta automáticamente como tabla SQL | Salud (historias clínicas), banca | Activo; IRIS sucede a Caché |
| **ObjectDB** | Java | BDOO que implementa **JPA y JDO** de forma nativa (sin traducción a tablas) | Aplicaciones Java embebidas o cliente-servidor | Activo |
| **db4o** | Java, .NET | Embebida; QBE, *Native Queries*, SODA; profundidad de activación | Móviles y embebidos (2000s) | Descontinuada; código abierto archivado |
| **ZODB** | Python | Persistencia por alcanzabilidad; MVCC; `FileStorage` *append-only*; **ZEO** (cliente-servidor) y **RelStorage** (guarda *pickles* en PostgreSQL/MySQL/Oracle) | Zope, Plone, aplicaciones Python | Activo (comunidad) |
| **Realm** | Swift, Kotlin, JS, .NET, Dart | Motor embebido orientado a objetos con objetos «vivos» (*live objects*) y vistas reactivas, MVCC con *zero-copy* | Aplicaciones móviles | Adquirido por MongoDB (2019); en 2024 MongoDB anunció la deprecación de Atlas Device Sync y los SDK; el núcleo sigue como código abierto |
| **ObjectBox** | Java/Kotlin, Swift, Dart, C/C++, Go, Python | Embebido, orientado a objetos, enfocado en *edge*/IoT; búsqueda vectorial | Móviles, IoT, IA en el dispositivo | Activo |

Sistemas históricos importantes: **O2** (Francia, influyó en ODMG/OQL), **ORION** (MCC, Won Kim; base de la investigación en evolución de esquema y bloqueo), **ONTOS**, **POET / FastObjects**, **Matisse**, **Jasmine**, **Iris** (HP), **EXODUS** y **SHORE** (Universidad de Wisconsin).

## 2. Mini-ejemplos de estilo

### GemStone/S (Smalltalk): el método se ejecuta en el servidor

```smalltalk
"Persistencia por alcanzabilidad desde UserGlobals"
UserGlobals at: #Clientes put: IdentitySet new.
(UserGlobals at: #Clientes) add: (Cliente nombre: 'Ana' ciudad: 'CDMX').
System commitTransaction.

"Consulta con bloque: se evalúa en el servidor, cerca de los datos"
(UserGlobals at: #Clientes) select: [:c | c ciudad = 'CDMX'].
```

### InterSystems IRIS: una clase que también es tabla

```objectscript
Class Tienda.Cliente Extends %Persistent
{
Property Nombre As %String;
Property Ciudad As %String;
Relationship Pedidos As Tienda.Pedido [ Cardinality = many, Inverse = Cliente ];
Index CiudadIdx On Ciudad;

Method Etiqueta() As %String [ SqlProc ]
{
    Quit ..Nombre _ " (" _ ..Ciudad _ ")"
}
}
```

```sql
-- La misma clase se consulta por SQL: proyección objeto → tabla automática
SELECT Nombre, Ciudad FROM Tienda.Cliente WHERE Ciudad = 'CDMX';
```

### Realm (Kotlin): objetos vivos

```kotlin
class Tarea : RealmObject {
    @PrimaryKey var id: ObjectId = ObjectId()
    var titulo: String = ""
    var hecha: Boolean = false
}

val realm = Realm.open(RealmConfiguration.create(schema = setOf(Tarea::class)))
realm.writeBlocking { copyToRealm(Tarea().apply { titulo = "Estudiar OQL" }) }
val pendientes = realm.query<Tarea>("hecha == false").find()   // resultados "vivos"
```

## 3. BDOO vs bases NoSQL modernas

| Aspecto | BDOO | Documentos (MongoDB) | Grafos (Neo4j) |
|---|---|---|---|
| Unidad | Objeto con OID y métodos | Documento JSON/BSON | Nodo y arista con propiedades |
| Referencias | Punteros/OID nativos, navegación transparente | Manuales (`_id`) o `$lookup` | Aristas de primera clase, *index-free adjacency* |
| Comportamiento | Métodos en el modelo | No (solo datos) | No (solo datos) |
| Esquema | Fuerte (clases) | Flexible (validación opcional) | Flexible |
| Consultas | OQL / API del lenguaje | MQL, *aggregation pipeline* | Cypher / GQL (ISO, 2024) |
| Acoplamiento al lenguaje | Alto | Bajo | Bajo |
| Herencia | Nativa | Polimorfismo por campo discriminador | Etiquetas múltiples |

**Idea clave:** las bases de documentos heredaron el **anidamiento** (objetos complejos) y las de grafos la **navegación** (recorrer referencias), pero ninguna adoptó la **identidad + comportamiento + herencia** dentro del motor. Por eso una BDOO sigue siendo distinta.

## 4. Matriz de decisión ponderada (plantilla)

| Criterio | Peso | GemStone/S | ObjectDB | ZODB | IRIS | PostgreSQL + ORM |
|---|---|---|---|---|---|---|
| Ajuste al lenguaje del equipo | 0.20 | | | | | |
| Navegación de grafos profundos | 0.15 | | | | | |
| Consultas *ad hoc* / BI | 0.15 | | | | | |
| Escalabilidad / distribución | 0.10 | | | | | |
| Evolución de esquema | 0.10 | | | | | |
| Ecosistema y talento disponible | 0.15 | | | | | |
| Licencia y costo | 0.10 | | | | | |
| Soporte y madurez | 0.05 | | | | | |
| **Total** | 1.00 | | | | | |

Puntúa de 1 a 5 y multiplica por el peso. El ejercicio [A2](../ejemplos/A2-proyecto-final.md) usa esta matriz.

## Errores comunes

- ❌ Elegir un OODBMS solo por rendimiento de recorridos sin evaluar el ecosistema ni el talento disponible.
- ❌ Creer que MongoDB es una BDOO porque guarda «objetos».
- ❌ Ignorar el riesgo de proveedor: varios OODBMS cambiaron de dueño o se descontinuaron (db4o, la sincronización de Realm).

## Conexiones (intercalación)

- Servidor de páginas (ObjectStore) vs de objetos (Versant) ↔ [Lección 06](06-almacenamiento.md).
- ObjectDB implementa JPA ↔ [Lección 10](10-orm.md).
- *Class history* de GemStone ↔ [Lección 08](08-evolucion-esquema.md).

## Preguntas de recuerdo activo

1. ¿Qué técnica de *swizzling* hizo famosa a ObjectStore?
2. ¿Qué tiene de especial la ejecución de métodos en GemStone/S?
3. ¿Sobre qué estructura de almacenamiento se construye InterSystems IRIS?
4. ¿Qué son ZEO y RelStorage en ZODB?
5. ¿Qué heredaron las BD de documentos y de grafos del mundo de objetos, y qué no?

??? success "Respuestas"
    1. *Swizzling* por memoria virtual, en el momento de la falla de página (*page-fault time*).
    2. Los métodos Smalltalk se ejecutan en el servidor, cerca de los datos, como en un procedimiento almacenado pero escritos en el mismo lenguaje de la aplicación.
    3. Sobre *globals*: arreglos dispersos multidimensionales persistentes.
    4. ZEO es el servidor que permite que varios procesos compartan un *storage*; RelStorage guarda los objetos de ZODB (como *pickles*) en un SGBD relacional.
    5. Heredaron el anidamiento (documentos) y la navegación (grafos); no adoptaron la identidad, el comportamiento ni la herencia dentro del motor.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Objectivity/DB | BD federada y distribuida; usada a escala de petabytes en física de altas energías |
| ObjectDB | BDOO Java que implementa JPA y JDO de forma nativa |
| IRIS | Multimodelo sobre *globals*; las clases se proyectan como tablas SQL |
| Realm | BD de objetos móvil con objetos vivos; adquirida por MongoDB en 2019 |
| ORION | Prototipo de MCC (Won Kim) clave en evolución de esquema y bloqueo |

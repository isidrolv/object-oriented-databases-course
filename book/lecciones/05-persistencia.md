# Lección 05 · Persistencia de objetos

## Objetivos

- Enunciar los **tres principios de la persistencia ortogonal** (Atkinson y Morrison).
- Comparar los modelos de persistencia: por alcanzabilidad, por herencia, explícita y por declaración.
- Explicar el ***pointer swizzling*** y sus variantes.
- Programar persistencia con **ZODB** (Python) y reconocer el estilo de **db4o**, **JDO** y **ObjectDB** (Java).
- Entender los **estados del ciclo de vida** de un objeto persistente (fantasmas, *hollow*, *dirty*).

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Imagina un árbol de Navidad colgado de un gancho en el techo. Todo lo que está **colgado** del árbol (esferas, luces, la estrella) se queda arriba aunque apagues la luz. Lo que está en el suelo se barre al día siguiente. La raíz persistente es el gancho: **todo lo que cuelga de ella, directa o indirectamente, se guarda**.

## 1. Persistencia ortogonal: tres principios

| Principio | Enunciado | Consecuencia |
|---|---|---|
| **Ortogonalidad de tipos** | Cualquier objeto, de cualquier tipo, puede ser persistente | No hay tipos «de BD» y tipos «de memoria» |
| **Persistencia por alcanzabilidad** (transitiva) | La vida de un objeto la determina su alcanzabilidad desde una raíz persistente | El programador no marca objeto por objeto |
| **Independencia de la persistencia** | El código es el mismo para datos de corta y de larga vida | Se reutilizan algoritmos sin cambios |

## 2. Modelos de persistencia

| Modelo | Cómo se decide | Ejemplos |
|---|---|---|
| **Por alcanzabilidad** | Lo alcanzable desde una raíz | ZODB, GemStone/S, PJama, ODMG Smalltalk |
| **Por herencia** | La clase hereda de una clase persistente | ZODB (`Persistent` para objetos de primer nivel), ODMG C++ (`d_Object`) |
| **Explícita** | Llamada a `store`/`makePersistent`/`persist` | db4o (`store`), JDO (`makePersistent`), JPA (`persist`) |
| **Por declaración / anotación** | Metadatos marcan las clases *persistence-capable* | JDO (XML o anotaciones + *enhancer*), JPA (`@Entity`) |

!!! note "En la práctica se combinan"
    JDO y JPA hacen `makePersistent` explícito **y** propagan por alcanzabilidad (JDO lo hace siempre; JPA solo si configuras `cascade = PERSIST`). ZODB exige heredar de `Persistent` para que un objeto tenga OID propio, pero el guardado ocurre por alcanzabilidad.

## 3. *Pointer swizzling*

En disco, un objeto referencia a otro por **OID**; en memoria, por **dirección virtual**. *Swizzling* = convertir OID → puntero en memoria; *unswizzling* = lo inverso al escribir.

| Dimensión | Opciones | Compromiso |
|---|---|---|
| **Cuándo** | *Eager* (al cargar el objeto, todas sus referencias) vs *lazy* (al primer uso) | *Eager* = costo inicial alto; *lazy* = verificación en cada desreferencia |
| **Dónde** | *In-place* (en el mismo búfer de página) vs *copy* (copia a otra área) | *In-place* complica escribir la página de vuelta |
| **Cómo** | Software (comprobar un bit «es OID o puntero») vs **hardware** (memoria virtual) | Hardware: sin costo de comprobación, pero dependiente del SO |
| **Dirección** | Directo (puntero al objeto) vs indirecto (puntero a una entrada de tabla de objetos residentes) | Indirecto facilita expulsar objetos de la caché |

**Ejemplo histórico:** ObjectStore usaba la memoria virtual (técnica de Wilson, *Pointer Swizzling at Page Fault Time*, 1991): las páginas se mapean protegidas; al tocarlas, la falla de página carga los datos y *swizzlea* sus punteros. Así los punteros de C++ funcionaban «sin cambios».

```text
Disco                           Memoria
┌──────────────┐  swizzling    ┌──────────────────┐
│ Pedido #77   │ ───────────▶  │ Pedido @0x7f10   │
│ cliente: OID │               │ cliente: 0x7f88 ─┼──▶ Cliente @0x7f88
│        = 42  │ ◀───────────  │                  │
└──────────────┘ unswizzling   └──────────────────┘
```

## 4. Ciclo de vida de un objeto persistente

Estados de JDO (los demás sistemas usan nombres parecidos):

```text
            makePersistent()                commit()
Transient ───────────────────▶ Persistent-New ─────────▶ Hollow
                                                           │ leer campo
                                                           ▼
     Persistent-Deleted ◀── deletePersistent() ── Persistent-Clean
                                                           │ modificar campo
                                                           ▼
                                                    Persistent-Dirty ── commit() ──▶ Hollow
```

- **Hollow / fantasma (*ghost*):** existe en memoria con su OID, pero sin estado cargado; se llena al primer acceso (carga diferida).
- **Dirty:** modificado en la transacción; se escribirá en `commit`.

## 5. ZODB: una BDOO nativa de Python

```python
# pip install ZODB
import ZODB, ZODB.FileStorage, transaction
from persistent import Persistent
from persistent.list import PersistentList
from BTrees.OOBTree import OOBTree


class Cliente(Persistent):
    def __init__(self, nombre, ciudad):
        self.nombre = nombre
        self.ciudad = ciudad
        self.pedidos = PersistentList()   # colección persistente: detecta cambios

    def agregar_pedido(self, pedido):
        self.pedidos.append(pedido)


class Pedido(Persistent):
    def __init__(self, folio, lineas):
        self.folio = folio
        self.lineas = lineas              # lista simple: se guarda junto al pedido

    def total(self):
        return sum(cant * precio for _, cant, precio in self.lineas)


storage = ZODB.FileStorage.FileStorage("tienda.fs")
db = ZODB.DB(storage)
conn = db.open()
root = conn.root()                         # raíz persistente (un mapping)

if "clientes" not in root:
    root["clientes"] = OOBTree()           # árbol B persistente, escalable

ana = Cliente("Ana", "CDMX")
ana.agregar_pedido(Pedido(1001, [("teclado", 2, 450.0), ("mouse", 1, 300.0)]))
root["clientes"]["ana"] = ana              # ana y su pedido se vuelven alcanzables
transaction.commit()                       # ← persistencia por alcanzabilidad

print(root["clientes"]["ana"].pedidos[0].total())   # 1200.0
print(ana._p_oid, ana._p_changed)                     # OID de 8 bytes, False
conn.close(); db.close()
```

### La trampa de la mutabilidad en ZODB

```python
class Carrito(Persistent):
    def __init__(self):
        self.items = []            # lista Python normal, NO persistente

    def agregar(self, item):
        self.items.append(item)    # ZODB no se entera: el atributo no se reasignó
        self._p_changed = True     # ← hay que avisar explícitamente
```

Alternativas: usar `PersistentList`/`PersistentMapping`/`BTrees`, o reasignar (`self.items = self.items + [item]`).

### Granularidad de almacenamiento

Solo los objetos que heredan de `Persistent` tienen **OID propio** y se cargan por separado. Los objetos «normales» (listas, tuplas, `dict`) se serializan **dentro** del registro de su dueño persistente. Decide con cuidado:

| Si el subobjeto… | Hazlo |
|---|---|
| Es pequeño y siempre se lee con el dueño | Atributo normal (literal) |
| Es grande, compartido o se modifica por separado | `Persistent` (objeto con OID) |
| Es una colección de miles de elementos | `BTrees` (OOBTree, IOBTree…) |

## 6. db4o (Java, embebida) — estilo histórico

```java
ObjectContainer db = Db4oEmbedded.openFile(Db4oEmbedded.newConfiguration(), "pilotos.db4o");
try {
    db.store(new Piloto("Checo Pérez", 99));                 // persistencia explícita

    // Query By Example (QBE): los campos nulos o en cero son comodines
    ObjectSet<Piloto> r = db.queryByExample(new Piloto("Checo Pérez", 0));

    // Native Query: la consulta es código Java tipado
    List<Piloto> top = db.query(new Predicate<Piloto>() {
        public boolean match(Piloto p) { return p.getPuntos() > 50; }
    });
} finally {
    db.close();
}
```

Conceptos clave de db4o:

- **Activation depth** (profundidad de activación, por defecto 5): cuántos niveles del grafo se cargan al recuperar un objeto; más allá, los objetos llegan **inactivos** (campos en `null`/0) salvo que se use *transparent activation*.
- **Update depth** (por defecto 1): `store()` sobre un objeto ya guardado solo actualiza sus campos directos; los cambios en objetos referenciados no se guardan si no se aumenta la profundidad o se usa *transparent persistence*.

## 7. JDO y ObjectDB

```java
// JDO
PersistenceManager pm = pmf.getPersistenceManager();
Transaction tx = pm.currentTransaction();
try {
    tx.begin();
    Cliente c = new Cliente("Ana");
    c.getPedidos().add(new Pedido(1001));
    pm.makePersistent(c);                 // el pedido se persiste por alcanzabilidad
    tx.commit();
} finally {
    if (tx.isActive()) tx.rollback();
    pm.close();
}
```

```java
// ObjectDB: una BDOO que expone la API de JPA
EntityManagerFactory emf = Persistence.createEntityManagerFactory("objectdb:tienda.odb");
EntityManager em = emf.createEntityManager();
em.getTransaction().begin();
em.persist(new Cliente("Ana"));
em.getTransaction().commit();
List<Cliente> l = em.createQuery("SELECT c FROM Cliente c WHERE c.nombre = 'Ana'", Cliente.class)
                    .getResultList();
```

JDO usa ***bytecode enhancement***: un proceso posterior a la compilación añade a cada clase *persistence-capable* el código que intercepta las lecturas y escrituras de campos (para cargar fantasmas y marcar *dirty*).

## 8. Recolección de basura persistente

Si la persistencia es por alcanzabilidad, un objeto inalcanzable debe borrarse. Opciones:

- **GC persistente** (GemStone/S, ZODB con `db.pack()` que elimina revisiones antiguas y objetos inalcanzables).
- **Borrado explícito** (ODMG `delete()`, JDO `deletePersistent`) con riesgo de **referencias colgantes**.

## Errores comunes

- ❌ Mutar una lista simple dentro de un `Persistent` sin `_p_changed = True`.
- ❌ Creer que `store()` en db4o guarda todo el grafo modificado (depende del *update depth*).
- ❌ Hacer de cada valor diminuto un objeto `Persistent` (explosión de OID y de idas al servidor).
- ❌ Confundir *lazy loading* (cargar estado al usarlo) con *lazy swizzling* (convertir OID → puntero al usarlo): están relacionados pero no son lo mismo.

## Conexiones (intercalación)

- Fantasmas ↔ *proxies* de carga diferida en Hibernate ([Lección 10](10-orm.md)).
- *Swizzling* ↔ servidor de páginas y caché cliente ([Lección 06](06-almacenamiento.md)).
- `commit` y conflictos en ZODB ↔ control optimista ([Lección 07](07-transacciones.md)).

## Preguntas de recuerdo activo

1. Enuncia los tres principios de la persistencia ortogonal.
2. ¿Qué es *swizzling* perezoso y qué costo tiene?
3. ¿Por qué hace falta `_p_changed = True` en ZODB?
4. ¿Qué es el *activation depth* de db4o?
5. ¿Qué estado tiene un objeto JDO justo después de `commit`?

??? success "Respuestas"
    1. Ortogonalidad de tipos, persistencia por alcanzabilidad, independencia de la persistencia.
    2. Convertir el OID en puntero en la primera desreferencia; cuesta una comprobación en cada acceso.
    3. Porque mutar un objeto no persistente dentro de un `Persistent` no se detecta: no hay asignación de atributo.
    4. Cuántos niveles del grafo de objetos se cargan (activan) al recuperar un objeto.
    5. *Hollow* (con `retainValues=false`, el valor por defecto).

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Raíz persistente | Punto de entrada nombrado desde el que se calcula la alcanzabilidad |
| *Swizzling* por hardware | Usa la protección de páginas de la memoria virtual para interceptar accesos |
| `db.pack()` en ZODB | Elimina revisiones antiguas y objetos inalcanzables del almacenamiento |
| *Bytecode enhancement* | Instrumentación de clases para interceptar accesos a campos (JDO) |
| Objeto fantasma | Objeto con OID cargado pero sin estado; se llena al primer acceso |

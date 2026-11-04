# Lección 10 · Mapeo objeto-relacional (ORM)

## Objetivos

- Conocer los **patrones de Fowler** (*PoEAA*, 2002) que sostienen a todo ORM: *Identity Map*, *Unit of Work*, *Lazy Load*, *Data Mapper*, *Active Record*.
- Elegir una **estrategia de herencia** en JPA: `SINGLE_TABLE`, `JOINED`, `TABLE_PER_CLASS`, `@MappedSuperclass`.
- Detectar y resolver el **problema N+1**.
- Comparar ORM con una BDOO nativa (lo que el ORM resuelve y lo que no).

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Un ORM es un **traductor simultáneo**: tú hablas «objetos» y la base de datos solo entiende «tablas». El traductor es muy bueno, pero si le pides una por una 100 frases cortas en vez de una frase completa, la conversación se vuelve lentísima: eso es el problema N+1.

## 1. Patrones de Fowler

| Patrón | Qué resuelve | Equivalente en BDOO |
|---|---|---|
| ***Identity Map*** | Garantiza que cada fila se cargue como **un único objeto** por sesión | La identidad por OID es nativa |
| ***Unit of Work*** | Registra los objetos nuevos, modificados y borrados, y los escribe juntos al confirmar | Seguimiento de objetos *dirty* en la caché del cliente |
| ***Lazy Load*** (*proxy*, *ghost*, *value holder*) | Carga datos solo al usarlos | Objetos fantasma y *swizzling* perezoso |
| ***Data Mapper*** | Separa el objeto de dominio de la lógica de persistencia | Persistencia transparente |
| ***Active Record*** | El objeto sabe guardarse (`user.save()`) | Persistencia por herencia |
| ***Identity Field*** | Guarda la clave primaria en el objeto | OID oculto |
| ***Foreign Key Mapping* / *Association Table Mapping*** | Mapea referencias y colecciones M:N | Referencias directas |
| ***Embedded Value*** | Mapea un objeto valor a columnas de la tabla del dueño | Literal estructurado (`struct`) |
| ***Serialized LOB*** | Guarda un subgrafo serializado en una columna | Objetos no persistentes dentro de un `Persistent` (ZODB) |

## 2. JPA: un modelo de dominio de ejemplo

```java
@Entity
@Table(name = "cliente")
public class Cliente {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nombre;

    @Embedded                                  // Embedded Value: sin identidad propia
    private Direccion direccion;

    @OneToMany(mappedBy = "cliente", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Pedido> pedidos = new ArrayList<>();

    @Version                                   // bloqueo optimista
    private long version;

    public void agregarPedido(Pedido p) {      // mantener AMBOS lados de la relación
        pedidos.add(p);
        p.setCliente(this);
    }
}

@Embeddable
public class Direccion { private String calle; private String ciudad; }

@Entity
public class Pedido {
    @Id @GeneratedValue private Long id;

    @ManyToOne(fetch = FetchType.LAZY)         // proxy perezoso
    @JoinColumn(name = "cliente_id")
    private Cliente cliente;

    @OneToMany(mappedBy = "pedido", cascade = CascadeType.ALL)
    private List<Linea> lineas = new ArrayList<>();

    public BigDecimal total() {
        return lineas.stream().map(Linea::subtotal).reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
```

!!! warning "Diferencia con ODMG"
    En ODMG, una `relationship` con `inverse` se mantiene **sola**. En JPA, `mappedBy` solo indica **qué lado es dueño** de la FK; mantener coherentes los dos lados en memoria es responsabilidad de la aplicación (de ahí `agregarPedido`).

## 3. Estrategias de herencia en JPA

Jerarquía: `Pago` (abstracta) ← `PagoTarjeta` (`numero`), `PagoTransferencia` (`clabe`).

| Estrategia | Tablas | Consulta polimórfica | Pros | Contras |
|---|---|---|---|---|
| `SINGLE_TABLE` | 1 tabla con columna discriminadora | Un `SELECT` sin *joins* | La más rápida | Columnas de subclases deben admitir `NULL`; tabla ancha |
| `JOINED` | 1 por clase (la de la superclase y una por cada subclase, unidas por PK) | *Joins* (o `LEFT JOIN` por cada subclase) | Normalizada; `NOT NULL` posible | *Joins* en cada carga |
| `TABLE_PER_CLASS` | 1 por clase concreta con **todas** las columnas | `UNION ALL` | Sin *joins* para consultas a una subclase | Consultas polimórficas costosas; generación de ID complicada |
| `@MappedSuperclass` | Ninguna para la superclase | **No** hay consultas polimórficas | Reutilizar atributos comunes | La superclase no es entidad |

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "tipo")
public abstract class Pago {
    @Id @GeneratedValue Long id;
    BigDecimal monto;
    public abstract String describir();
}

@Entity @DiscriminatorValue("TARJETA")
public class PagoTarjeta extends Pago {
    String numero;
    public String describir() { return "Tarjeta ****" + numero.substring(numero.length() - 4); }
}

@Entity @DiscriminatorValue("SPEI")
public class PagoTransferencia extends Pago {
    String clabe;
    public String describir() { return "SPEI " + clabe; }
}

// Consulta polimórfica: devuelve PagoTarjeta y PagoTransferencia; describir() usa ligadura tardía
List<Pago> pagos = em.createQuery("select p from Pago p where p.monto > 1000", Pago.class).getResultList();
```

## 4. El problema N+1

```java
// 1 consulta para los pedidos...
List<Pedido> pedidos = em.createQuery("select p from Pedido p", Pedido.class).getResultList();
for (Pedido p : pedidos) {
    System.out.println(p.getCliente().getNombre());   // ...y N consultas, una por cada proxy perezoso
}
```

SQL generado:

```sql
select p.id, p.cliente_id from pedido p;          -- 1
select c.* from cliente c where c.id = ?;         -- N veces (una por cliente distinto)
```

| Solución | Cómo | Cuándo |
|---|---|---|
| `JOIN FETCH` | `select p from Pedido p join fetch p.cliente` | Casos de uso concretos |
| `@EntityGraph` | `@EntityGraph(attributePaths = {"cliente"})` en el repositorio | Spring Data, grafos declarativos |
| *Batch fetching* | `@BatchSize(size = 50)` o `hibernate.default_batch_fetch_size` | Reduce N a N/50 consultas `IN (...)` |
| Proyección DTO | `select new dto.PedidoResumen(p.id, c.nombre) from Pedido p join p.cliente c` | Pantallas de solo lectura |
| `SUBSELECT` *fetch* | `@Fetch(FetchMode.SUBSELECT)` en colecciones | Cargar colecciones de todos los padres de una vez |

!!! tip "Cuidado con `JOIN FETCH` sobre dos colecciones"
    Hacer *fetch* de dos colecciones `List` a la vez produce `MultipleBagFetchException` en Hibernate o un **producto cartesiano**. Usa `Set`, varias consultas o *batch fetching*.

### ¿Y en una BDOO?

En una BDOO con servidor de páginas y buen *clustering*, recorrer `pedido.cliente` no cuesta una ida y vuelta por objeto: el cliente probablemente ya llegó en la misma página o está en la caché. El «N+1» se convierte en un problema de ***clustering*** y no de SQL ([Lección 06](06-almacenamiento.md)).

## 5. *Identity map* y *unit of work* en acción

```java
EntityManager em = emf.createEntityManager();
em.getTransaction().begin();

Cliente a = em.find(Cliente.class, 1L);
Cliente b = em.find(Cliente.class, 1L);
assert a == b;                         // Identity Map: mismo objeto, una sola consulta

a.setNombre("Ana María");              // Unit of Work: marcado como sucio (dirty checking)
em.persist(new Cliente("Luis"));       // registrado como nuevo

em.getTransaction().commit();          // flush: INSERT + UPDATE en una sola transacción
em.close();
```

## 6. Bloqueo optimista con `@Version`

```sql
UPDATE cliente SET nombre = ?, version = 8 WHERE id = ? AND version = 7;
-- 0 filas actualizadas → OptimisticLockException
```

Es la misma idea que el `ConflictError` de ZODB ([Lección 07](07-transacciones.md)), solo que implementada con una columna.

## 7. ORM vs BDOO nativa

| Problema | ORM | BDOO nativa |
|---|---|---|
| Identidad | *Identity map* por sesión (no global) | OID global |
| Herencia | 3 estrategias con compromisos | Nativa |
| Grafos profundos | Muchos *joins* o N+1 | Navegación directa |
| Consultas *ad hoc* y BI | Excelente (SQL) | Limitada |
| Evolución de esquema | Migraciones explícitas (Flyway, Liquibase) | Conversión perezosa o inmediata en el motor |
| Ecosistema | Enorme | Pequeño |

## Errores comunes

- ❌ `FetchType.EAGER` en todas partes «para evitar N+1»: cargas el mundo entero.
- ❌ Olvidar sincronizar los dos lados de una asociación bidireccional.
- ❌ Usar `TABLE_PER_CLASS` con muchas consultas polimórficas.
- ❌ Creer que el *identity map* es global entre sesiones (cada `EntityManager` tiene el suyo).
- ❌ Usar `CascadeType.ALL` en `@ManyToOne` (borrar un pedido borraría al cliente).

## Conexiones (intercalación)

- *Lazy load* ↔ objetos fantasma ([Lección 05](05-persistencia.md)).
- `@Version` ↔ control optimista ([Lección 07](07-transacciones.md)).
- Estrategias de herencia ↔ `INHERITS` de PostgreSQL ([Lección 09](09-objeto-relacional.md)).

## Preguntas de recuerdo activo

1. ¿Qué garantiza el *identity map*?
2. ¿Cuál es la estrategia de herencia más rápida para consultas polimórficas y cuál es su costo?
3. Describe el problema N+1 y tres soluciones.
4. ¿Quién mantiene coherente una asociación bidireccional en JPA?
5. ¿Cómo detecta JPA un conflicto optimista?

??? success "Respuestas"
    1. Que dentro de una sesión cada fila (cada identidad) corresponda a un único objeto en memoria.
    2. `SINGLE_TABLE`; las columnas de las subclases deben admitir `NULL` y la tabla es ancha.
    3. Una consulta trae N objetos y luego se lanza una consulta por cada asociación perezosa. Soluciones: `JOIN FETCH`, `@EntityGraph`, *batch fetching*, proyección a DTO, `SUBSELECT`.
    4. La aplicación (por ejemplo, con métodos auxiliares como `agregarPedido`).
    5. Con una columna `@Version`: el `UPDATE` incluye `WHERE version = ?`; si no actualiza ninguna fila, lanza `OptimisticLockException`.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| *Unit of Work* | Registra cambios (nuevos, sucios, borrados) y los escribe juntos |
| `mappedBy` | Marca el lado inverso (no dueño de la FK) de una asociación bidireccional |
| `@MappedSuperclass` | Comparte atributos sin crear entidad ni consultas polimórficas |
| `@BatchSize` | Carga perezosa en lotes con `IN (...)` |
| *Embedded Value* | Objeto valor mapeado a columnas de la tabla dueña |

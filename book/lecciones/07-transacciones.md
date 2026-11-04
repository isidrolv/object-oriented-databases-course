# Lección 07 · Transacciones y concurrencia

## Objetivos

- Aplicar **ACID** a grafos de objetos.
- Usar el **bloqueo jerárquico** (*multiple granularity locking*) con modos IS, IX, S, SIX y X, incluido el bloqueo sobre jerarquías de clases y objetos compuestos.
- Explicar las **transacciones largas** (diseño, *check-out/check-in*), **anidadas** (Moss) y las **sagas**.
- Comparar el control **pesimista**, **optimista**, **MVCC** y **semántico** (conmutatividad de métodos).
- Resolver conflictos en ZODB.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    En la biblioteca, si quieres leer un libro pones una **etiqueta verde** (lectura): otros también pueden leerlo. Si quieres escribir en él, pones una **etiqueta roja** (escritura): nadie más puede tocarlo. Si solo vas a usar una página, pones en la portada una etiqueta que dice «alguien está adentro» (intención), para que nadie se lleve el libro entero mientras tanto.

## 1. ¿Qué cambia respecto al modelo relacional?

| Aspecto | Relacional típico | BDOO / diseño |
|---|---|---|
| Duración | Milisegundos–segundos | Minutos, horas o **días** (CAD, ingeniería) |
| Unidad | Fila, tabla | Objeto, objeto compuesto, clase, jerarquía |
| Interacción | Corta, automática | Humana, iterativa, cooperativa |
| Abortar | Barato | Perder horas de trabajo es inaceptable |
| Operaciones | Lectura/escritura | Métodos con semántica (`depositar`, `incrementar`) |

## 2. Bloqueo jerárquico (*multiple granularity locking*)

Jerarquía típica de un OODBMS: **base de datos → segmento/contenedor → página → objeto**, o bien **clase → instancias**.

| Modo | Significado |
|---|---|
| **IS** | Intención de leer algo más abajo |
| **IX** | Intención de escribir algo más abajo |
| **S** | Lectura de todo el nodo y su subárbol |
| **SIX** | Lectura de todo + intención de escribir algunas partes |
| **X** | Escritura exclusiva de todo el nodo y su subárbol |

### Matriz de compatibilidad

| Solicitado \ Concedido | IS | IX | S | SIX | X |
|---|---|---|---|---|---|
| **IS** | ✓ | ✓ | ✓ | ✓ | ✗ |
| **IX** | ✓ | ✓ | ✗ | ✗ | ✗ |
| **S** | ✓ | ✗ | ✓ | ✗ | ✗ |
| **SIX** | ✓ | ✗ | ✗ | ✗ | ✗ |
| **X** | ✗ | ✗ | ✗ | ✗ | ✗ |

**Protocolo:** se bloquea de la raíz hacia abajo (para pedir S o IS en un nodo, se necesita IS o IX en el padre; para X, IX o SIX en el padre…) y se libera de abajo hacia arriba.

### Bloqueo de jerarquías de clases (ORION)

Una consulta sobre `Persona` (con subclases `Profesor` y `Estudiante`) debe evitar que alguien modifique instancias de las subclases en paralelo:

- Bloquear la clase en **S** bloquea implícitamente sus instancias **y las de sus subclases**, o
- Bloquear explícitamente cada subclase (más lento, pero más concurrente).
- Cambiar el **esquema** de una clase (agregar un atributo) exige **X** sobre la clase y sus subclases.

### Objetos compuestos

Bloquear un `Ensamble` en X bloquea implícitamente sus partes **exclusivas**. Las partes **compartidas** deben bloquearse por separado.

## 3. Transacciones largas: *check-out / check-in*

```text
┌──────────────────────┐   check-out (copia + bloqueo persistente)   ┌──────────────┐
│ BD pública           │ ──────────────────────────────────────────▶ │ BD privada   │
│ (versiones liberadas)│                                             │ (espacio de  │
│                      │ ◀────────────────────────────────────────── │  trabajo)    │
└──────────────────────┘     check-in (valida y publica)             └──────────────┘
            ▲                                                              │
            └──────────── BD de grupo (integración de equipo) ◀────────────┘
```

- El diseñador «saca» los objetos a su espacio privado y trabaja durante horas con **transacciones cortas locales**.
- Los bloqueos de *check-out* son **persistentes** (sobreviven a caídas y desconexiones).
- Al hacer *check-in* se crea una **nueva versión** (enlace con la [Lección 08](08-evolucion-esquema.md)).

## 4. Transacciones anidadas (Moss, 1981)

```text
T (raíz)
├── T1  reservar vuelo      ✓ commit (relativo a T)
├── T2  reservar hotel      ✗ abort  → T puede reintentar o elegir otro hotel
│   └── T2.1 cobrar depósito
└── T3  reservar auto       ✓ commit
→ Los efectos de T1 y T3 solo son DURABLES cuando T hace commit.
```

Reglas de las **anidadas cerradas** (*closed nested*):

1. Una subtransacción puede abortar sin abortar a su padre.
2. El *commit* de una hija es **condicional**: sus efectos y bloqueos se **heredan** al padre.
3. Solo el *commit* de la raíz hace durables los cambios.
4. Un padre no accede a los datos mientras sus hijas activas los tengan bloqueados.

Las **anidadas abiertas** (*open nested*) liberan bloqueos al confirmar la hija, lo que exige **compensación** si el padre aborta.

### Sagas (García-Molina y Salem, 1987)

Secuencia T1, T2, …, Tn de transacciones locales, cada una con su **compensación** C1, …, Cn. Si Tk falla, se ejecuta Ck−1, …, C1. Sacrifican el aislamiento a cambio de no mantener bloqueos largos.

## 5. Control de concurrencia pesimista vs optimista

| Enfoque | Cómo | Ideal cuando | Ejemplo |
|---|---|---|---|
| **Pesimista (2PL)** | Bloquear antes de acceder | Alta contención | Versant, ObjectStore |
| **Optimista** | Leer y escribir sin bloquear, **validar** al hacer *commit* | Baja contención, lecturas largas | ZODB, db4o |
| **MVCC** | Cada transacción lee una **instantánea** consistente; las escrituras crean versiones nuevas | Lectores que no deben bloquear a escritores | ZODB (instantánea al inicio de la transacción), GemStone/S |
| **Semántico** | Usa la **conmutatividad** de los métodos | Contadores, colas, saldos | `BTrees.Length` en ZODB, Weihl (1988) |

### Conmutatividad de métodos

| | `depositar(x)` | `retirar(y)` | `saldo()` |
|---|---|---|---|
| `depositar(x)` | ✓ conmutan | ✗ (si el retiro puede fallar por fondos) | ✗ |
| `retirar(y)` | ✗ | ✗ | ✗ |
| `saldo()` | ✗ | ✗ | ✓ |

Dos `depositar` concurrentes no deberían entrar en conflicto aunque **ambos escriban** el mismo objeto: el resultado es el mismo en cualquier orden.

## 6. Conflictos y su resolución en ZODB

```python
import transaction
from ZODB.POSException import ConflictError

def transferir(db, origen, destino, monto, intentos=5):
    for intento in range(intentos):
        conn = db.open()
        try:
            cuentas = conn.root()["cuentas"]
            cuentas[origen].retirar(monto)
            cuentas[destino].depositar(monto)
            transaction.commit()
            return True
        except ConflictError:
            transaction.abort()          # otro proceso escribió los mismos objetos
        finally:
            conn.close()
    raise RuntimeError("Demasiados conflictos")
```

Con el *transaction manager* moderno también puedes usar el patrón `for attempt in transaction.manager.attempts(): with attempt: ...`.

### Resolución de conflictos a nivel de aplicación

```python
from persistent import Persistent

class Contador(Persistent):
    def __init__(self):
        self.valor = 0

    def incrementar(self, n=1):
        self.valor += n

    def _p_resolveConflict(self, estado_antiguo, estado_guardado, estado_nuevo):
        # Fusión de tres vías: aplica los dos deltas sobre el estado común
        delta_otro = estado_guardado["valor"] - estado_antiguo["valor"]
        delta_mio = estado_nuevo["valor"] - estado_antiguo["valor"]
        return {"valor": estado_antiguo["valor"] + delta_otro + delta_mio}
```

Esta es una aplicación directa del control **semántico**: los incrementos conmutan, así que el conflicto se puede **fusionar** en lugar de abortar.

## 7. Recuperación

- **WAL** (*write-ahead logging*) con ARIES en motores con actualización *in-place* (Versant, ObjectStore usan bitácoras).
- ***Shadow paging*** / *append-only*: escribir nuevas versiones sin sobrescribir (`FileStorage` de ZODB). La recuperación consiste en truncar la última transacción incompleta.
- **Caché cliente:** al abortar se descartan los objetos modificados de la caché (en ZODB pasan a estado fantasma o se invalidan).

## Errores comunes

- ❌ Pedir S sobre un objeto sin IS en sus ancestros.
- ❌ Usar 2PL estricto en transacciones de diseño de horas (bloqueo eterno del equipo).
- ❌ Pensar que en las anidadas cerradas el *commit* de una hija es durable.
- ❌ Reintentar indefinidamente ante `ConflictError` sin límite ni *backoff*.
- ❌ Confundir conmutatividad de métodos con ausencia de escrituras.

## Conexiones (intercalación)

- *Check-in* ↔ versionado ([Lección 08](08-evolucion-esquema.md)).
- Bloqueo por página ↔ servidor de páginas ([Lección 06](06-almacenamiento.md)).
- Sagas ↔ microservicios y *unit of work* ([Lección 10](10-orm.md)).

## Preguntas de recuerdo activo

1. ¿Qué modos son compatibles con IX?
2. ¿Qué significa SIX y cuándo se usa?
3. ¿Qué ocurre con los bloqueos de una subtransacción cerrada al hacer *commit*?
4. ¿Por qué el control optimista conviene en ZODB?
5. ¿Qué hace `_p_resolveConflict`?

??? success "Respuestas"
    1. IS e IX.
    2. *Shared + Intention eXclusive*: leer todo el subárbol y modificar algunas partes, p. ej., recorrer un *extent* y actualizar unos pocos objetos.
    3. Se heredan al padre; no se liberan hasta que la raíz termine (o hasta que el padre los libere al confirmar).
    4. Porque la contención suele ser baja, las lecturas no bloquean y la caché cliente evita idas al servidor; los conflictos se detectan al hacer *commit*.
    5. Fusiona en tres vías el estado antiguo, el guardado por otra transacción y el propio, para evitar abortar en conflictos semánticamente compatibles.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Regla de bloqueo jerárquico | Bloquear de la raíz hacia abajo con intenciones; liberar de abajo hacia arriba |
| *Check-out* | Copiar objetos a una BD privada con bloqueo persistente |
| Saga | Secuencia de transacciones locales con compensaciones |
| MVCC en ZODB | Cada transacción ve una instantánea consistente tomada al empezar |
| Conmutatividad | Dos operaciones conmutan si el resultado no depende de su orden |

# A1 · Evolución de esquema perezosa con conflictos concurrentes

**Nivel:** 🔴 Avanzado · **Lecciones:** [07](../lecciones/07-transacciones.md), [08](../lecciones/08-evolucion-esquema.md) · **Tiempo:** 90 min · **Requiere:** `pip install ZODB`

## 1. Planteamiento del problema

Un banco guarda sus cuentas en ZODB. La versión 1 de `Cuenta` almacena el saldo como `float` (en pesos). La versión 2 debe guardarlo como **entero en centavos** (`saldo_centavos`) para evitar errores de redondeo. La migración debe hacerse **sin detener el sistema**:

- Las cuentas se convierten **perezosamente** al cargarse.
- Un proceso por lotes recorre las cuentas para **persistir** la nueva forma.
- Mientras tanto, la aplicación sigue recibiendo **depósitos concurrentes**.

Debes implementar `__setstate__` y `_p_resolveConflict` de modo que **ningún depósito se pierda** y la migración no aborte por conflictos evitables.

## 2. Escenario de ejecución

Estado guardado (versión 1) de la cuenta `"C-1"`:

```python
{"titular": "Ana", "saldo": 1500.10}
```

Línea de tiempo (dos conexiones de la misma BD, cada una con su propio `TransactionManager`):

```text
t0  Lote   (TM-A): carga C-1 → __setstate__ la convierte en memoria a v2
t1  App    (TM-B): carga C-1 → convertida en memoria a v2
t2  App    (TM-B): depositar(100.00) → commit OK        # guarda v2: 160010 centavos
t3  Lote   (TM-A): c._p_changed = True → commit         # ¡conflicto! su copia es de t0
```

En `t3`, ZODB llama a `_p_resolveConflict(old, committed, new)` con:

| Argumento | Contenido | Versión |
|---|---|---|
| `old` | Estado que leyó el lote en `t0` (tal como estaba **en disco**) | **v1**: `{"titular": "Ana", "saldo": 1500.10}` |
| `committed` | Lo que guardó la app en `t2` | v2: `{"titular": "Ana", "saldo_centavos": 160010, "version": 2}` |
| `new` | Lo que el lote quiere guardar | v2: `{"titular": "Ana", "saldo_centavos": 150010, "version": 2}` |

## 3. Entradas y salidas

| Entrada | Salida esperada |
|---|---|
| Estado v1 en disco + línea de tiempo | Saldo final `160010` centavos (1 600.10) y `version == 2` |
| `old` en formato v1 dentro de `_p_resolveConflict` | No debe lanzar `KeyError`; se normaliza a v2 |
| Dos depósitos concurrentes de 50 y 70 sobre una cuenta v2 | Ambos se conservan (+12 000 centavos) |

## 4. Solución propuesta incompleta

```python
# cuentas.py
from persistent import Persistent


def _a_v2(state):
    """Normaliza cualquier estado (v1 o v2) a la forma v2. Devuelve un dict NUEVO."""
    state = dict(state)
    if state.get("version", 1) < 2:
        pesos = state.pop("saldo", 0.0)
        state["saldo_centavos"] = ________          # ¡cuidado con el redondeo!
        state["version"] = 2
    return state


class Cuenta(Persistent):
    def __init__(self, titular, saldo_centavos=0):
        self.titular = titular
        self.saldo_centavos = saldo_centavos
        self.version = 2

    def __setstate__(self, state):
        ________                                     # conversión perezosa al cargar

    def depositar(self, pesos):
        self.saldo_centavos += ________

    @property
    def saldo(self):
        return self.saldo_centavos / 100

    def _p_resolveConflict(self, old, committed, new):
        old, committed, new = ________, ________, ________
        delta_otro = ________
        delta_mio = ________
        resultado = dict(committed)
        resultado["saldo_centavos"] = ________
        return resultado
```

Preguntas:

1. ¿Por qué `int(pesos * 100)` es un error para `1500.10`?
2. ¿Por qué el `old` llega en formato v1 aunque el lote ya «convirtió» la cuenta en `t0`?
3. ¿Qué pasaría si `_p_resolveConflict` no normalizara los estados?
4. ¿La resolución es segura si la operación fuera `retirar` con validación de fondos?

---

## 5. Respuesta correcta esperada

??? success "Ver solución"

    ```python
    # cuentas.py
    from persistent import Persistent


    def _a_v2(state):
        state = dict(state)
        if state.get("version", 1) < 2:
            pesos = state.pop("saldo", 0.0)
            state["saldo_centavos"] = round(pesos * 100)   # 1500.10*100 = 150009.99999… → 150010
            state["version"] = 2
        return state


    class Cuenta(Persistent):
        def __init__(self, titular, saldo_centavos=0):
            self.titular = titular
            self.saldo_centavos = saldo_centavos
            self.version = 2

        def __setstate__(self, state):
            super().__setstate__(_a_v2(state))

        def depositar(self, pesos):
            self.saldo_centavos += round(pesos * 100)

        @property
        def saldo(self):
            return self.saldo_centavos / 100

        def _p_resolveConflict(self, old, committed, new):
            old, committed, new = _a_v2(old), _a_v2(committed), _a_v2(new)
            delta_otro = committed["saldo_centavos"] - old["saldo_centavos"]
            delta_mio = new["saldo_centavos"] - old["saldo_centavos"]
            resultado = dict(committed)
            resultado["saldo_centavos"] = old["saldo_centavos"] + delta_otro + delta_mio
            return resultado
    ```

    **Traza de `t3`:** `old` normalizado = 150010; `delta_otro` = 160010 − 150010 = **+10000**; `delta_mio` = 150010 − 150010 = **0** (el lote solo migró la forma). Resultado: **160010** centavos con `version = 2`. No se pierde el depósito y el lote no aborta.

    **Respuestas:**

    1. `1500.10 * 100` en binario es `150009.99999999997`; `int()` trunca a `150009` y se pierde un centavo. `round()` da `150010`. (En producción usa `Decimal` para la conversión.)
    2. Porque `__setstate__` convierte **solo en memoria**: el registro en disco sigue en v1 hasta que alguien escribe el objeto. ZODB entrega a `_p_resolveConflict` los estados **serializados**, tal como están almacenados.
    3. `old["saldo_centavos"]` lanzaría `KeyError`; ZODB lo trata como un conflicto **no resuelto** y lanza `ConflictError`: el lote tendría que reintentar y, con mucho tráfico, podría no terminar nunca (*livelock*).
    4. **No.** Los depósitos conmutan, pero un `retirar` con validación de fondos no: dos retiros que por separado son válidos pueden dejar el saldo negativo al fusionarse. En ese caso, `_p_resolveConflict` debe **rechazar** la fusión (lanzar `ConflictError`) si el resultado viola el invariante, y dejar que la transacción se reintente con el saldo actualizado.

    **Prueba ejecutable** (guárdala junto a `cuentas.py`):

    ```python
    # prueba_a1.py
    import transaction, ZODB, ZODB.FileStorage
    from persistent.mapping import PersistentMapping
    from cuentas import Cuenta

    db = ZODB.DB(ZODB.FileStorage.FileStorage("banco.fs"))

    # Simular datos v1 en disco: escribir el estado antiguo directamente
    with db.transaction() as conn:
        c = Cuenta("Ana")
        c.__dict__.clear()
        c.__dict__.update({"titular": "Ana", "saldo": 1500.10})   # forma v1
        conn.root()["cuentas"] = PersistentMapping({"C-1": c})

    # Reabrir la BD para vaciar las cachés: la conexión del pool aún tiene en memoria el objeto v1
    db.close()
    db = ZODB.DB(ZODB.FileStorage.FileStorage("banco.fs"))

    tm_lote, tm_app = transaction.TransactionManager(), transaction.TransactionManager()
    lote, app = db.open(tm_lote), db.open(tm_app)

    c_lote = lote.root()["cuentas"]["C-1"]; c_lote.saldo_centavos       # t0: carga y convierte
    c_app = app.root()["cuentas"]["C-1"];  c_app.depositar(100.00)       # t1-t2
    tm_app.commit()
    c_lote._p_changed = True                                              # t3
    tm_lote.commit()                                                      # resuelto por _p_resolveConflict

    with db.transaction() as conn:
        final = conn.root()["cuentas"]["C-1"]
        print(final.saldo_centavos, final.version)                        # 160010 2
    db.close()
    ```

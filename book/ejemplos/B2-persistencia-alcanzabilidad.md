# B2 · Persistencia por alcanzabilidad en ZODB

**Nivel:** 🟢 Básico · **Lección:** [05](../lecciones/05-persistencia.md) · **Tiempo:** 45 min · **Requiere:** `pip install ZODB`

## 1. Planteamiento del problema

Un equipo escribió un pequeño gestor de tareas sobre ZODB. Al reiniciar el programa, **algunos cambios se pierden** y otros no. Debes **predecir la salida** del segundo arranque, explicar cada pérdida y corregir el código.

## 2. Escenario de ejecución

- Python 3.10+ y ZODB 6.x, en un solo proceso.
- El programa se ejecuta dos veces: primero `escribir()`, luego (en otro proceso) `leer()`.
- El archivo `tareas.fs` no existe antes de la primera ejecución.

```python
# tareas.py
import sys
import ZODB, ZODB.FileStorage, transaction
from persistent import Persistent


class Proyecto(Persistent):
    def __init__(self, nombre):
        self.nombre = nombre
        self.tareas = []                 # lista Python normal

    def agregar(self, tarea):
        self.tareas.append(tarea)


class Tarea(Persistent):
    def __init__(self, titulo):
        self.titulo = titulo
        self.hecha = False


def abrir():
    db = ZODB.DB(ZODB.FileStorage.FileStorage("tareas.fs"))
    return db, db.open()


def escribir():
    db, conn = abrir()
    root = conn.root()

    p = Proyecto("Curso BDOO")
    root["proyecto"] = p
    p.agregar(Tarea("Leer lección 05"))
    transaction.commit()                              # (1)

    p.agregar(Tarea("Hacer ejercicio B2"))            # (2)
    p.tareas[0].hecha = True                          # (3)
    transaction.commit()

    huerfana = Tarea("Tarea que nadie referencia")    # (4)
    huerfana.hecha = True
    transaction.commit()

    p.nombre = "Curso BDOO 90 días"                   # (5)
    transaction.abort()

    conn.close(); db.close()


def leer():
    db, conn = abrir()
    p = conn.root()["proyecto"]
    print(p.nombre)
    print(len(p.tareas))
    for t in p.tareas:
        print(t.titulo, t.hecha)
    conn.close(); db.close()


if __name__ == "__main__":
    escribir() if sys.argv[1] == "w" else leer()
```

```bash
python tareas.py w
python tareas.py r
```

## 3. Entradas y salidas

| Entrada | Salida que debes producir |
|---|---|
| El código anterior | La salida exacta de `python tareas.py r` |
| — | Explicación de qué pasa en (1), (2), (3), (4) y (5) |
| — | Una versión corregida en la que `leer()` muestre ambas tareas |

## 4. Solución propuesta incompleta

```text
Salida predicha:
  línea 1: ____________________
  línea 2: ____
  línea 3: ____________________ ____
  ¿hay línea 4?: ____

(1) Se guardan p y su lista con la primera tarea porque ____________________.
(2) La segunda tarea ____ se guarda porque self.tareas es ____ y append() ____.
(3) El cambio de hecha=True en tareas[0] ____ se guarda porque Tarea ____ Persistent
    y la asignación de atributo ____ el objeto como modificado.
(4) La tarea huérfana ____ se guarda porque ____________________.
(5) El cambio de nombre se pierde porque ____________________.
```

Corrección (complétala):

```python
from persistent.list import ____

class Proyecto(Persistent):
    def __init__(self, nombre):
        self.nombre = nombre
        self.tareas = ____()

    def agregar(self, tarea):
        self.tareas.append(tarea)
        # alternativa si se conserva la lista normal: ____________
```

---

## 5. Respuesta correcta esperada

??? success "Ver solución"

    **Salida de `python tareas.py r`:**

    ```text
    Curso BDOO
    1
    Leer lección 05 True
    ```

    | Paso | Qué ocurre | Por qué |
    |---|---|---|
    | (1) | Se guardan `p`, su lista y la Tarea 1 | `p` es alcanzable desde la raíz (`root["proyecto"] = p` modifica la raíz, que es persistente). La lista simple se serializa **dentro** del registro de `p`; la Tarea 1, al ser `Persistent`, recibe su propio OID |
    | (2) | La Tarea 2 **no** se guarda | `self.tareas` es una `list` normal; `append()` la muta sin reasignar el atributo, así que `p._p_changed` sigue en `False` y `p` no se reescribe |
    | (3) | `hecha = True` **sí** se guarda | `Tarea` hereda de `Persistent`; asignar un atributo marca el objeto como modificado y se escribe su propio registro |
    | (4) | La huérfana **no** se guarda | No es alcanzable desde ninguna raíz persistente: nunca se le asigna `_p_jar` ni OID |
    | (5) | El nombre se pierde | `transaction.abort()` descarta los cambios no confirmados; `p` vuelve a su último estado confirmado |

    **Versión corregida:**

    ```python
    from persistent.list import PersistentList

    class Proyecto(Persistent):
        def __init__(self, nombre):
            self.nombre = nombre
            self.tareas = PersistentList()

        def agregar(self, tarea):
            self.tareas.append(tarea)
            # alternativa con lista normal: self._p_changed = True
    ```

    Con la corrección, la salida es:

    ```text
    Curso BDOO
    2
    Leer lección 05 True
    Hacer ejercicio B2 False
    ```

    **Para profundizar:** imprime `p._p_oid`, `p.tareas[0]._p_oid` y `p._p_changed` después de cada paso, y ejecuta `db.pack()` para ver cómo se compacta `tareas.fs`.

# Lección 08 · Evolución de esquema y versionado

## Objetivos

- Clasificar los cambios de esquema con la **taxonomía de ORION**.
- Comparar la **conversión inmediata**, la **perezosa (*lazy*)**, el ***screening*** y la **emulación por vistas**.
- Implementar migraciones en ZODB con `__setstate__`.
- Diseñar **versiones de objetos** (grafos de derivación, referencias genéricas y específicas, configuraciones) y **versiones de esquema**.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Imagina que tu colección de cromos cambia de formato: ahora cada cromo debe tener la estatura del jugador. Puedes **reimprimir todos de golpe** un domingo (inmediata), o **arreglar cada cromo la próxima vez que lo saques** del álbum (perezosa). Y si guardas las fotos de cómo era tu álbum cada año, tienes **versiones**.

## 1. El problema

En una BDOO, el esquema está **atado a las clases del programa** y hay millones de objetos ya almacenados con la forma antigua. Cambiar una clase exige decidir **qué pasa con las instancias existentes** y con el código que las usa.

## 2. Taxonomía de ORION (Banerjee, Kim, Kim y Korth, SIGMOD 1987)

| Categoría | Cambios |
|---|---|
| **1. Contenido de una clase** | 1.1 Atributos: agregar, eliminar, renombrar, cambiar dominio, cambiar valor por defecto, cambiar la clase de la que se hereda. 1.2 Métodos: agregar, eliminar, renombrar, cambiar código, cambiar la clase de la que se hereda |
| **2. Relaciones de herencia** | Agregar superclase, eliminar superclase, cambiar el orden de las superclases |
| **3. Clases** | Agregar clase, eliminar clase, renombrar clase |

### Invariantes del esquema (deben preservarse tras cada cambio)

1. **Invariante del retículo de clases:** la jerarquía es un grafo dirigido acíclico con una raíz (`OBJECT`).
2. **Nombres distintos:** atributos y métodos con nombre único dentro de cada clase.
3. **Origen de identidad distinto:** no hay dos propiedades con el mismo origen en una clase.
4. **Herencia completa:** una clase hereda todas las propiedades de sus superclases salvo que se violen 2 o 3.
5. **Compatibilidad de dominios:** si un atributo se redefine en una subclase, su dominio debe ser el mismo o una especialización.

Más **reglas** para resolver conflictos (p. ej., cuando dos superclases aportan un atributo con el mismo nombre, gana la primera en el orden de superclases).

## 3. Estrategias de conversión de instancias

| Estrategia | Cuándo se paga | Pros | Contras |
|---|---|---|---|
| **Inmediata (*eager*)** | Al aplicar el cambio: se reescriben todas las instancias | Esquema único y simple; consultas sin sobrecosto | Tiempo de inactividad o una transacción enorme |
| **Perezosa (*deferred / lazy*)** | Al acceder a cada objeto por primera vez | Sin inactividad; el costo se reparte | Varias formas conviven; cada acceso comprueba la versión |
| ***Screening*** (ORION) | Nunca se reescriben: en cada lectura se «filtran» los atributos borrados y se rellenan valores por defecto | Cero reescrituras | Sobrecosto permanente en cada lectura |
| **Emulación / vistas** | — | Programas antiguos y nuevos coexisten | Complejidad; actualizaciones a través de vistas |
| **Versionado de esquema** | — | Cada instancia sigue ligada a su versión de clase | Hay que traducir entre versiones (*handlers*) |

!!! example "Ejemplos reales"
    - **GemStone/S:** *class history* — cada clase tiene una historia de versiones; las instancias se migran con `migrateInstancesTo:` cuando conviene.
    - **Versant:** *lazy schema evolution* — las instancias se convierten al escribirlas.
    - **Encore** (Skarra y Zdonik, 1986): *version sets* de tipos con *exception handlers* que traducen entre versiones.
    - **ZODB:** no hay esquema explícito; la migración se programa en `__setstate__` o con herramientas como `zodbupdate` (renombres de módulos y clases).

## 4. Migración perezosa en ZODB

Versión 1 de la clase:

```python
class Cliente(Persistent):
    def __init__(self, nombre):
        self.nombre = nombre          # "Ana López"
```

Versión 2: se separa nombre y apellido y se agrega `correo`.

```python
from persistent import Persistent

class Cliente(Persistent):
    VERSION = 2

    def __init__(self, nombre, apellido, correo=None):
        self.version = self.VERSION
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo

    def __setstate__(self, state):
        # Se ejecuta al cargar el objeto desde la BD: conversión perezosa
        version = state.get("version", 1)
        if version < 2:
            completo = state.pop("nombre", "")
            nombre, _, apellido = completo.partition(" ")
            state.update(nombre=nombre, apellido=apellido, correo=None, version=2)
        super().__setstate__(state)
        # Nota: el objeto convertido NO se marca como modificado; si quieres que la
        # nueva forma se guarde, márcalo (self._p_changed = True) dentro de una transacción.
```

Migración inmediata equivalente (un *script* de mantenimiento):

```python
import transaction
for i, cliente in enumerate(root["clientes"].values()):
    cliente._p_changed = True        # al cargarse ya pasó por __setstate__; forzar escritura
    if i % 1000 == 0:
        transaction.savepoint(True)  # liberar memoria en lotes grandes
transaction.commit()
```

## 5. Versionado de objetos

Indispensable en CAD, CASE, gestión documental e ingeniería.

```text
Grafo de derivación de la pieza "Engrane-12"

      v1 ──▶ v2 ──▶ v3 (liberada)
              │
              └──▶ v2.1 ──▶ v2.2 (experimental)

Objeto genérico: Engrane-12  → apunta a la versión por defecto (v3)
```

| Concepto | Significado |
|---|---|
| **Objeto genérico** (*generic object*) | Representa a todas las versiones de un objeto |
| **Versión por defecto** | La que se devuelve si no se especifica otra |
| **Referencia específica (estática)** | Apunta a **una** versión concreta (`Engrane-12@v2`) |
| **Referencia genérica (dinámica)** | Apunta al objeto genérico y se resuelve en tiempo de ejecución a la versión por defecto |
| **Estados de versión** | *Transitoria* (editable), *de trabajo* (no editable, pero se puede derivar), *liberada* (inmutable) |
| **Configuración** | Conjunto coherente de versiones de varios objetos (p. ej., el ensamble «Motor 2.0» = Engrane-12@v3 + Pistón-4@v7) |

### Propagación de cambios

Si sale `Engrane-12@v4`, ¿cambia automáticamente el `Motor` que lo contiene? Depende de si la referencia es **genérica** (sí, se actualiza la configuración) o **específica** (no, el motor queda «congelado»). Las políticas de propagación (*change notification* y *change propagation*) son una decisión de diseño.

## 6. Versionado de esquema

- **Versión de clase:** cada instancia recuerda con qué versión fue creada.
- **Versión de esquema completo:** un programa se liga a una versión del esquema (p. ej., `Esquema-2026-1`).
- **Compatibilidad hacia atrás y hacia delante:** con *handlers* o vistas se permite que programas viejos lean objetos nuevos y viceversa.

## Errores comunes

- ❌ Renombrar una clase en ZODB sin dejar un alias: los objetos antiguos guardan la ruta `modulo.Clase` y fallan al cargarse (usa `zodbupdate` o un alias en el módulo antiguo).
- ❌ Hacer una migración inmediata de millones de objetos en una sola transacción sin *savepoints*.
- ❌ Confundir versión de objeto con versión de esquema.
- ❌ Usar referencias genéricas en piezas que deben quedar certificadas (deberían ser específicas).

## Conexiones (intercalación)

- *Check-in* crea versiones ↔ [Lección 07](07-transacciones.md).
- Migraciones con Flyway/Liquibase en relacional ↔ [Lección 10](10-orm.md).
- Dominios CAD ↔ [Lección 13](13-diseno-avanzado.md).

## Preguntas de recuerdo activo

1. Nombra las tres categorías de cambios de la taxonomía de ORION.
2. ¿Qué es el *screening*?
3. ¿Qué ventaja y qué costo tiene la conversión perezosa?
4. Diferencia entre referencia genérica y específica.
5. ¿Qué es una configuración?

??? success "Respuestas"
    1. Cambios al contenido de una clase (atributos y métodos), a las relaciones de herencia y a las clases (agregar, eliminar, renombrar).
    2. Una técnica de ORION que no reescribe instancias: al leerlas, filtra los atributos eliminados y añade valores por defecto.
    3. Evita la inactividad y reparte el costo; a cambio conviven varias formas del objeto y cada acceso debe comprobar la versión.
    4. La específica apunta a una versión fija; la genérica apunta al objeto genérico y se resuelve dinámicamente a la versión por defecto.
    5. Un conjunto coherente de versiones de varios objetos que forman un todo.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Invariante de compatibilidad de dominios | Un atributo redefinido en una subclase debe tener el mismo dominio o una especialización |
| `__setstate__` en ZODB | Gancho de carga donde se programa la conversión perezosa |
| *Class history* (GemStone) | Historia de versiones de una clase con migración de instancias |
| Versión liberada | Inmutable; solo se pueden derivar versiones nuevas |
| Grafo de derivación | Árbol o DAG de versiones de un objeto |

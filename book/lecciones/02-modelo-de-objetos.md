# Lección 02 · El modelo de objetos

## Objetivos

- Distinguir **identidad**, **igualdad superficial** e **igualdad profunda**.
- Explicar cómo se generan y usan los **OID** (*Object Identifiers*).
- Modelar **objetos complejos** con constructores de tipo.
- Razonar sobre **tipos vs clases**, *extents*, herencia simple y múltiple, sobrescritura, sobrecarga y ligadura tardía.
- Entender el **encapsulamiento** y su tensión con las consultas *ad hoc*.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Dos gemelos idénticos tienen la misma cara, la misma ropa y la misma altura: son **iguales**, pero no son **la misma persona**. Si uno se corta el pelo, sigue siendo él. El OID es como el alma del objeto: no depende de cómo se ve (sus valores) y nunca cambia mientras el objeto exista.

## 1. Identidad de objetos (OID)

Un **OID** es un identificador **único**, **inmutable**, **generado por el sistema** e **independiente del valor** del objeto. Se usa para referenciar objetos desde otros objetos.

| Propiedad | OID | Clave primaria relacional |
|---|---|---|
| Quién la genera | El sistema | El diseñador (natural o subrogada) |
| ¿Visible para el usuario? | Normalmente no | Sí |
| ¿Cambia si cambian los datos? | Nunca | Una clave natural puede cambiar |
| ¿Se reutiliza? | No (ni tras borrar) | Depende |
| Alcance | Toda la BD (o federación) | Una tabla |

### Tres nociones de igualdad

| Noción | Definición | Ejemplo Python |
|---|---|---|
| **Identidad** (`o1 == o2` por OID) | Son el *mismo* objeto | `a is b` |
| **Igualdad superficial** (*shallow*) | Mismos valores atómicos y **mismas referencias** (mismos OID) | `a.__dict__ == b.__dict__` con referencias idénticas |
| **Igualdad profunda** (*deep*) | Grafos de objetos isomorfos con mismos valores hoja, aunque las referencias apunten a objetos distintos | comparación recursiva |

```python
class Direccion:
    def __init__(self, calle, ciudad):
        self.calle, self.ciudad = calle, ciudad

class Persona:
    def __init__(self, nombre, direccion):
        self.nombre, self.direccion = nombre, direccion

d1 = Direccion("Reforma 10", "CDMX")
d2 = Direccion("Reforma 10", "CDMX")       # mismo valor, otro objeto

p1 = Persona("Ana", d1)
p2 = Persona("Ana", d1)                   # comparte la MISMA dirección
p3 = Persona("Ana", d2)                   # dirección distinta pero igual en valor

def superficial(a, b):
    return all(getattr(a, k) is getattr(b, k) or getattr(a, k) == getattr(b, k)
               and not hasattr(getattr(a, k), '__dict__')
               for k in vars(a))

def profunda(a, b):
    if not hasattr(a, '__dict__'):
        return a == b
    return type(a) is type(b) and all(profunda(getattr(a, k), getattr(b, k)) for k in vars(a))

print(p1 is p2)             # False → identidades distintas
print(superficial(p1, p2))  # True  → mismo nombre y misma referencia a d1
print(superficial(p1, p3))  # False → d1 y d2 son objetos distintos
print(profunda(p1, p3))     # True  → los grafos son iguales en valor
```

!!! tip "Implicación"
    Identidad ⇒ igualdad superficial ⇒ igualdad profunda. La inversa **no** se cumple.

### ¿Cómo se implementa un OID?

- **Físico:** codifica la dirección (volumen, página, ranura). Rápido, pero mover el objeto exige dejar un *forwarding pointer*.
- **Lógico:** número único que se resuelve por una tabla de mapeo OID → dirección. Más flexible, un acceso extra.
- **Híbrido/estructurado:** p. ej. *número de clase + número de serie*; en Objectivity/DB, `base.contenedor.página.ranura`.
- En ZODB el OID es un entero de 8 bytes asignado al primer `commit`; la ubicación física la resuelve el *storage* (`FileStorage` mantiene un índice OID → posición en archivo).

## 2. Objetos complejos y constructores de tipo

Los constructores ortogonales permiten construir cualquier estructura:

| Constructor | Semántica | Duplicados | Orden |
|---|---|---|---|
| `tuple` / `struct` | Conjunto fijo de atributos con nombre | — | — |
| `set` | Conjunto | No | No |
| `bag` | Multiconjunto | Sí | No |
| `list` | Secuencia | Sí | Sí |
| `array` | Secuencia indexada de tamaño (normalmente) fijo | Sí | Sí |
| `dictionary` | Mapa clave → valor | Claves únicas | No |

**Ortogonalidad:** cualquier constructor puede aplicarse a cualquier tipo, incluidos otros constructores: `set<list<tuple<...>>>`.

Distingue también:

- **Objeto compuesto (*composite* / agregación fuerte):** las partes dependen del todo (borrar el coche borra su motor). ORION lo llamaba *composite object* con referencias *dependientes exclusivas*.
- **Asociación:** referencias entre objetos independientes (el coche *referencia* a su dueño, que existe por sí mismo).

## 3. Literales vs objetos

En el modelo ODMG:

- **Objeto:** tiene OID, es mutable, puede ser compartido.
- **Literal:** **no** tiene OID, es un valor; se incrusta en el objeto que lo contiene (`long`, `string`, `date`, `struct Direccion {...}`).

Elegir entre literal y objeto es una decisión de diseño: ¿esa cosa tiene **vida propia** y se **comparte**? Entonces es un objeto.

## 4. Encapsulamiento

Un objeto expone una **interfaz** (firmas de métodos) y oculta su **implementación** (estructura y código). Beneficio: independencia lógica de datos a nivel de objeto.

**Tensión:** las consultas *ad hoc* quieren leer atributos directamente. Soluciones históricas:

- Exponer atributos de solo lectura a las consultas (ODMG lo permite: los atributos forman parte de la interfaz).
- Permitir consultas solo vía métodos (*accessors*), lo que dificulta la optimización.
- Encapsulamiento «relajado» para el optimizador y estricto para las aplicaciones.

## 5. Tipos, clases y *extents*

| Concepto | Significado |
|---|---|
| **Tipo** | Especificación (interfaz): qué operaciones y propiedades tiene. Noción de **tiempo de compilación** |
| **Clase** | Implementación del tipo + fábrica de objetos (operación `new`) + a veces su *extent*. Noción de **tiempo de ejecución** |
| ***Extent*** | El conjunto de todas las instancias persistentes de un tipo en la BD |

En ODMG: `interface` define solo comportamiento (no instanciable); `class` define estado + comportamiento (instanciable) y puede declarar un `extent` y claves (`key`).

**Herencia de *extents*:** el *extent* de una superclase **incluye** las instancias de sus subclases (inclusión de *extents*: `Empleados ⊆ Personas`).

## 6. Herencia, sobrescritura, sobrecarga y ligadura tardía

ODMG distingue:

- **Herencia de comportamiento (ISA, `:`):** una interfaz o clase hereda la interfaz de otra. Se permite **herencia múltiple** de interfaces.
- **Herencia de estado (`EXTENDS`):** una clase hereda estado y comportamiento de **una sola** clase.

```text
interface Imprimible { void imprimir(); };
class Persona { attribute string nombre; };
class Empleado extends Persona : Imprimible { attribute float salario; };
```

- **Sobrescritura (*overriding*):** la subclase redefine un método heredado.
- **Sobrecarga (*overloading*):** el mismo nombre de operación en tipos distintos (`area()` en `Circulo` y en `Cuadrado`).
- **Ligadura tardía (*late binding*):** la implementación concreta se elige **en tiempo de ejecución** según el tipo real del objeto.

```python
class Figura:
    def area(self): raise NotImplementedError

class Circulo(Figura):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2

class Rectangulo(Figura):
    def __init__(self, b, h): self.b, self.h = b, h
    def area(self): return self.b * self.h

figuras = [Circulo(1), Rectangulo(2, 3)]
print(sum(f.area() for f in figuras))   # ligadura tardía: cada objeto usa su area()
```

En una BDOO, la consulta `select f.area() from Figuras f` aplica ligadura tardía **dentro del motor**: el *extent* `Figuras` contiene círculos y rectángulos, y cada uno ejecuta su propio método. En relacional necesitarías `CASE tipo WHEN ...`.

### Conflictos en herencia múltiple

Si `C` hereda de `A` y `B` y ambos definen `m()`:

- Prohibirlo (error de compilación).
- Resolverlo por orden de declaración (Python usa **MRO C3**).
- Obligar a renombrar o a redefinir `m()` en `C`.

## 7. Completitud computacional y extensibilidad

- **Completitud computacional:** se puede expresar cualquier función computable (el lenguaje de métodos es Turing-completo). SQL-92 no lo era; por eso se añadieron *stored procedures* y luego SQL/PSM.
- **Extensibilidad:** los tipos definidos por el usuario se usan **igual** que los predefinidos (en atributos, consultas, índices).

## Errores comunes

- ❌ Confundir igualdad profunda con identidad al deduplicar objetos.
- ❌ Modelar como objeto lo que es un valor (p. ej., `Dinero`, `Fecha`, `Direccion` no compartida) → más OID, más indirección, peor rendimiento.
- ❌ Pensar que el *extent* de `Persona` excluye a los empleados.
- ❌ Creer que encapsulamiento total es compatible sin costo con consultas *ad hoc* optimizadas.

## Conexiones (intercalación)

- OID físicos vs lógicos ↔ [almacenamiento](06-almacenamiento.md) y *pointer swizzling* en [persistencia](05-persistencia.md).
- *Extents* ↔ `extent` de ODL en [ODMG](03-odmg.md) y consultas sobre jerarquías en [OQL](04-oql.md).
- Identidad ↔ *identity map* en [ORM](10-orm.md).

## Preguntas de recuerdo activo

1. ¿Qué cuatro propiedades tiene un OID?
2. Ordena por fuerza: igualdad profunda, identidad, igualdad superficial.
3. ¿Qué diferencia hay entre un objeto y un literal en ODMG?
4. ¿Qué es la inclusión de *extents*?
5. ¿Qué es la ligadura tardía y por qué importa en consultas?

??? success "Respuestas"
    1. Único, inmutable, generado por el sistema, independiente del valor (y normalmente no reutilizable).
    2. Identidad (más fuerte) ⇒ superficial ⇒ profunda (más débil).
    3. El objeto tiene OID, es mutable y compartible; el literal es un valor sin OID incrustado en otro objeto.
    4. El *extent* de una superclase contiene también las instancias de sus subclases.
    5. Elegir en tiempo de ejecución la implementación del método según el tipo real; permite consultas polimórficas sobre *extents* heterogéneos.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| OID físico vs lógico | Físico codifica la dirección (rápido, frágil al mover); lógico requiere tabla de mapeo (flexible) |
| Igualdad superficial | Mismos valores y mismas referencias (mismos OID) |
| Igualdad profunda | Grafos isomorfos con valores hoja iguales |
| `EXTENDS` vs `:` en ODMG | `EXTENDS`: herencia de estado, simple; `:` herencia de comportamiento, múltiple |
| Extensibilidad | Los tipos de usuario se tratan igual que los predefinidos |

# Lección 06 · Arquitectura física y almacenamiento

## Objetivos

- Comparar las arquitecturas **servidor de páginas**, **servidor de objetos** y **servidor de consultas**.
- Diseñar el ***clustering*** de objetos según los patrones de acceso.
- Elegir entre **índices de una clase**, **índices de jerarquía de clases** e **índices de ruta** (multi-índice, índice anidado, índice de ruta, *access support relations*).
- Entender la caché cliente, la coherencia de caché y la gestión de objetos grandes.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Si guardas los calcetines en el cajón de arriba, los zapatos en el sótano y los pantalones en el ático, vestirte te tomará una hora. *Clustering* es poner juntas en el mismo cajón las cosas que **usas juntas**. Un índice de ruta es como una nota en la puerta que dice «los zapatos rojos son de Ana», para no tener que revisar cada cuarto.

## 1. Arquitecturas cliente-servidor

DeWitt, Futtersack, Maier y Vélez (VLDB 1990) compararon tres diseños:

| Arquitectura | Qué viaja por la red | Dónde se ejecutan los métodos | Ventajas | Desventajas | Ejemplos |
|---|---|---|---|---|---|
| **Servidor de páginas** (*page server*) | Páginas completas | Cliente | Servidor simple; aprovecha el *clustering*: una página trae muchos objetos relacionados | Bloqueo a nivel de página (conflictos falsos); el servidor no entiende objetos | ObjectStore, O2 |
| **Servidor de objetos** (*object server*) | Objetos individuales | Cliente y/o servidor | Bloqueo fino; el servidor puede evaluar consultas y métodos | Muchos mensajes si el *clustering* es malo; servidor más complejo | Versant, ORION, GemStone/S (ejecuta métodos en el servidor) |
| **Servidor de consultas / archivos** | Resultados de consultas o bloques de archivo | Servidor | Poco tráfico para consultas selectivas | Navegación interactiva lenta | Diseños tipo NFS, SGBDR clásicos |

**Conclusión del estudio:** con buen *clustering*, el servidor de páginas suele ganar en cargas navegacionales; con mal *clustering* o mucha contención, el servidor de objetos tiene ventaja.

### Caché del cliente y coherencia

- Los OODBMS mantienen una **caché de objetos o páginas en el cliente entre transacciones** (*inter-transaction caching*).
- Para que sea coherente se usan protocolos como **bloqueo con *callback*** (*callback locking*): el cliente conserva el bloqueo cacheado y el servidor le pide liberarlo cuando otro lo necesita. También existen la **evitación optimista** (validar al hacer `commit`) y las **notificaciones de invalidación**.
- ZODB: cada conexión tiene su caché de objetos; al iniciar la transacción se **invalidan** los objetos que otros modificaron (con ZEO el servidor envía invalidaciones a los clientes).

## 2. *Clustering*

Colocar en la misma página (o en páginas contiguas) los objetos que se acceden juntos.

| Estrategia | Criterio | Ejemplo |
|---|---|---|
| **Por clase** | Todas las instancias de una clase juntas | Recorridos completos de *extent* |
| **Por composición** | Un objeto con sus partes | Un `Ensamble` CAD con sus `Piezas` |
| **Por relación** | Objetos ligados por una referencia frecuente | `Pedido` con sus `Lineas` |
| **Por pista del usuario** (*placement hints*) | `new(cerca_de=obj)` | ObjectStore *segments*, Objectivity *containers* |
| **Dinámico / adaptativo** | Reorganización según estadísticas de acceso | Investigación: DSTC, DRO |

El *clustering* es un problema **NP-difícil** en general (equivale a particionar un grafo ponderado); en la práctica se usan heurísticas.

```text
Patrón de acceso: "mostrar pedido con sus líneas y productos"

Mal clustering (por clase)            Buen clustering (por relación)
Página 1: Pedido1 Pedido2 Pedido3     Página 1: Pedido1 Linea1.1 Linea1.2
Página 2: Linea1.1 Linea2.1 ...       Página 2: Pedido2 Linea2.1 Linea2.2
Página 3: Linea1.2 Linea3.1 ...
→ 3 lecturas para Pedido1             → 1 lectura para Pedido1
```

!!! warning "Un solo *clustering* físico"
    Un objeto vive en **una** ubicación física; si dos patrones de acceso compiten (por clase vs por composición) debes elegir el dominante o replicar/indexar para el otro.

## 3. Índices en BDOO

### 3.1 Índices sobre la jerarquía de herencia

Consulta: `select x from personas x where x.edad > 30` (incluye profesores y estudiantes).

| Tipo | Estructura | Bueno para | Malo para |
|---|---|---|---|
| **Índice de una sola clase** (SC, *single-class*) | Un árbol B por clase | Consultas sobre una sola clase | Consultas sobre toda la jerarquía (hay que revisar varios índices) |
| **Índice de jerarquía de clases** (CH, *class-hierarchy index*) | Un solo árbol B para toda la jerarquía; cada entrada guarda listas de OID por clase | Consultas sobre la jerarquía | Consultas sobre una sola clase profunda (entradas más grandes) |
| ***H-tree* / CG-tree** | Árboles por clase anidados o enlazados | Ambos casos | Complejidad de mantenimiento |

### 3.2 Índices de ruta

Consulta: `select v from vehiculos v where v.fabricante.empresa.ciudad = "Monterrey"` (ruta `Vehiculo.fabricante.empresa.ciudad`).

| Índice | Mapea | Consultas que acelera | Costo de actualización |
|---|---|---|---|
| **Multi-índice** (Maier y Stein) | Un índice por cada paso: `ciudad → Empresa`, `empresa → Fabricante`, `fabricante → Vehiculo` | Cualquier subruta | Bajo (cada índice es independiente), pero la consulta recorre *n* índices |
| **Índice anidado** (*nested index*, Bertino y Kim, 1989) | Valor final → objetos **iniciales** de la ruta: `"Monterrey" → {Vehiculo3, Vehiculo9}` | La ruta completa, muy rápido | Alto: un cambio intermedio exige recorrer hacia atrás (se necesitan referencias inversas) |
| **Índice de ruta** (*path index*) | Valor final → **instanciaciones** completas de la ruta: `"Monterrey" → {(V3, F1, E2), (V9, F4, E2)}` | La ruta y sus prefijos | Medio-alto; ocupa más espacio |
| ***Access Support Relations*** (Kemper y Moerkotte) | Relaciones materializadas que guardan rutas (total o parcialmente) y se pueden partir | Rutas largas con estrategias de descomposición | Configurable |

```text
Ruta: Vehiculo ──fabricante──▶ Fabricante ──empresa──▶ Empresa ──ciudad──▶ string

Índice anidado:  "Monterrey" ↦ {V3, V9}
Índice de ruta:  "Monterrey" ↦ {⟨V3,F1,E2⟩, ⟨V9,F4,E2⟩}
Multi-índice:    I3: "Monterrey" ↦ {E2}
                 I2: E2 ↦ {F1, F4}
                 I1: F1 ↦ {V3}, F4 ↦ {V9}
```

### 3.3 Otros índices

- **Índices de función / de método:** sobre el resultado precalculado de un método (exige que sea determinista y que se invalide cuando cambian sus dependencias).
- **Índices sobre elementos de colecciones:** `select c from cursos c where "BD" in c.etiquetas`.
- **Índices de texto, espaciales y multidimensionales**, cruciales en CAD/GIS.

## 4. Representación de objetos en disco

- **Registro de longitud variable** con cabecera: OID, identificador de clase o versión de esquema, longitud y campos.
- **Desbordamiento y *forwarding*:** si un objeto crece y no cabe en su página, se mueve y se deja un apuntador (con OID físico).
- **Objetos grandes (BLOB, colecciones enormes):** se fragmentan en árboles de segmentos (p. ej., el gestor de objetos grandes de EXODUS, basado en un árbol B+ sobre posiciones de bytes) o en estructuras como los `BTrees` de ZODB.
- **Almacenamiento estructurado en registro (*log-structured*):** `FileStorage` de ZODB **añade** cada nueva revisión al final del archivo y mantiene un índice OID → posición; `pack()` compacta.

## 5. Gestión del búfer

- **Reemplazo** (LRU, CLOCK) a nivel de página u objeto.
- **Doble caché:** búfer de páginas del servidor + caché de objetos del cliente.
- **Prefetching** guiado por el *clustering* o por la estructura del grafo (cargar referencias probables).

## Errores comunes

- ❌ Indexar cada paso de una ruta larga y creer que equivale a un índice anidado.
- ❌ Ignorar el costo de mantenimiento de un índice anidado en dominios con muchas actualizaciones intermedias.
- ❌ Suponer que un servidor de páginas puede bloquear objetos individuales sin protocolos adicionales.
- ❌ Agrupar físicamente por clase cuando el acceso dominante es por composición.

## Conexiones (intercalación)

- Bloqueo por página vs por objeto ↔ [Lección 07](07-transacciones.md).
- Índices de ruta ↔ reescritura de consultas en [Lección 11](11-optimizacion.md).
- `FileStorage` *append-only* ↔ MVCC en [Lección 07](07-transacciones.md).

## Preguntas de recuerdo activo

1. ¿Qué viaja por la red en un servidor de páginas y en uno de objetos?
2. ¿Por qué el *clustering* óptimo es difícil?
3. ¿Qué mapea un índice anidado y por qué cuesta mantenerlo?
4. ¿Cuándo conviene un índice de jerarquía de clases sobre índices por clase?
5. ¿Qué es el bloqueo con *callback*?

??? success "Respuestas"
    1. Páginas completas en el servidor de páginas; objetos individuales en el de objetos.
    2. Porque equivale a particionar un grafo ponderado (NP-difícil) y los patrones de acceso compiten.
    3. Valor final de la ruta → objetos iniciales; un cambio en un objeto intermedio exige recalcular qué objetos iniciales se ven afectados, para lo que hacen falta referencias inversas.
    4. Cuando las consultas suelen abarcar toda la jerarquía (la superclase y sus subclases).
    5. Un protocolo en el que el cliente conserva bloqueos en caché entre transacciones y el servidor le pide liberarlos cuando otro cliente los necesita.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Ventaja del servidor de páginas | Simplicidad y aprovechamiento del *clustering* |
| Desventaja del servidor de páginas | Bloqueo de grano grueso y conflictos falsos |
| Índice de ruta | Valor final → instanciaciones completas de la ruta |
| Multi-índice | Un índice por paso de la ruta; se encadenan al consultar |
| *Placement hint* | Pista del programador para colocar un objeto cerca de otro |

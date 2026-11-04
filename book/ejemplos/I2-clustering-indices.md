# I2 · *Clustering* e índices a partir de una carga de trabajo

**Nivel:** 🟡 Intermedio · **Lecciones:** [06](../lecciones/06-almacenamiento.md), [11](../lecciones/11-optimizacion.md) · **Tiempo:** 60 min · **Herramientas:** papel, calculadora

## 1. Planteamiento del problema

Una tienda en línea usa un OODBMS con **servidor de páginas**. Debes elegir la estrategia de ***clustering*** y los **índices** que minimicen las páginas leídas para la carga de trabajo, **justificándolo con números**.

## 2. Escenario de ejecución

Esquema:

```text
Cliente(nombre, direccion: struct{calle, ciudad}, pedidos: set<Pedido>)
Pedido(folio, fecha, cliente: Cliente, lineas: list<Linea>)
Linea(producto: Producto, cantidad, precio)
```

| Clase | Instancias | Tamaño por objeto |
|---|---|---|
| Cliente | 20 000 | 400 B |
| Pedido | 100 000 | 200 B |
| Linea | 500 000 (5 por pedido) | 100 B |

- Página de 8 KB; usa como capacidad útil **8 000 B** para simplificar.
- Los clientes están repartidos uniformemente en **50 ciudades**; los pedidos, uniformemente en **12 meses**.
- Un índice de árbol B cuesta **3 páginas** por búsqueda.
- La caché está fría (cuenta todas las lecturas).

Carga de trabajo:

| Operación | Frecuencia | Descripción |
|---|---|---|
| **W1** | 80 % | Mostrar un pedido por folio con todas sus líneas |
| **W2** | 15 % | Pedidos del último mes de los clientes de una ciudad |
| **W3** | 5 % | Reporte mensual: recorrer **todas** las líneas |

## 3. Entradas y salidas

| Entrada | Salida esperada |
|---|---|
| Datos anteriores | Páginas leídas por W1, W2 y W3 con *clustering* **por clase** y **por composición** (pedido + líneas) |
| — | Costo ponderado por operación promedio en ambos casos |
| — | Índice(s) recomendados para W2 y su costo de mantenimiento |

## 4. Solución propuesta incompleta

```text
Capacidad por página
  Por clase:       pedidos/página = 8000/200 = ____    líneas/página = 8000/100 = ____
                   páginas de pedidos = ____           páginas de líneas = ____
  Por composición: tamaño de pedido+5 líneas = ____ B  → grupos/página = ____
                   páginas totales = ____

W1 (por folio, índice sobre folio = 3 páginas)
  Por clase:       3 + 1 (pedido) + ____ (líneas dispersas) = ____
  Por composición: 3 + ____ = ____

W3 (todas las líneas)
  Por clase:       ____ páginas
  Por composición: ____ páginas (hay que leer también los pedidos)

W2 (ciudad X, último mes)
  Clientes en X = 20000/50 = ____   Pedidos de esos clientes = ____   Del último mes ≈ ____
  Sin índice: recorrer todos los pedidos (____ páginas por clase) + desreferenciar clientes
  Con índice anidado (ciudad, mes) → OID de pedidos: 3 + ____ páginas (un pedido por página, peor caso)

Costo ponderado = 0.80·W1 + 0.15·W2 + 0.05·W3
```

---

## 5. Respuesta correcta esperada

??? success "Ver solución"

    **Capacidad por página**

    | Estrategia | Cálculo | Resultado |
    |---|---|---|
    | Por clase: pedidos | 8000 / 200 = 40 por página → 100 000 / 40 | **2 500** páginas |
    | Por clase: líneas | 8000 / 100 = 80 por página → 500 000 / 80 | **6 250** páginas |
    | Por composición | 200 + 5·100 = 700 B → ⌊8000/700⌋ = 11 grupos por página → 100 000 / 11 | **9 091** páginas |

    **W1 — pedido con sus líneas**

    | Estrategia | Cálculo | Páginas |
    |---|---|---|
    | Por clase | 3 (índice) + 1 (pedido) + 5 (cada línea en una página distinta, peor caso) | **9** |
    | Por composición | 3 (índice) + 1 (pedido y líneas juntos) | **4** |

    **W3 — recorrer todas las líneas**

    | Estrategia | Páginas |
    |---|---|
    | Por clase | **6 250** |
    | Por composición | **9 091** (las líneas están mezcladas con los pedidos) |

    **W2 — pedidos del último mes de una ciudad**

    - Clientes en la ciudad: 20 000 / 50 = **400**; pedidos de esos clientes: 100 000 / 50 = **2 000**; del último mes: 2 000 / 12 ≈ **167**.
    - **Sin índice:** recorrer los 100 000 pedidos (2 500 páginas por clase o 9 091 por composición) y desreferenciar sus clientes: miles de páginas.
    - **Con un índice anidado** sobre `Pedido.cliente.direccion.ciudad` combinado con `fecha` (clave compuesta `(ciudad, mes)` → OID de pedidos): 3 + 167 ≈ **170** páginas en el peor caso. Si el *clustering* por composición coloca juntos los pedidos de un mismo cliente o de una misma fecha, son menos.

    **Costo ponderado (con índice para W2)**

    | Estrategia | 0.80·W1 | 0.15·W2 | 0.05·W3 | **Total** |
    |---|---|---|---|---|
    | Por clase | 0.80·9 = 7.2 | 0.15·170 = 25.5 | 0.05·6 250 = 312.5 | **345.2** |
    | Por composición | 0.80·4 = 3.2 | 0.15·170 = 25.5 | 0.05·9 091 = 454.6 | **483.3** |

    !!! warning "Interpretación experta"
        El promedio ponderado favorece el *clustering* por clase **solo por W3**, que es un reporte por lotes. Pero W1 es la operación **interactiva** (80 % de las peticiones, con latencia visible para el usuario) y por composición cuesta **menos de la mitad** (4 frente a 9 páginas). La decisión correcta es:

        1. ***Clustering* por composición** (pedido + líneas) para optimizar la latencia de W1.
        2. **Índice anidado `(ciudad, mes)` → Pedido** para W2. Su costo de mantenimiento es bajo porque los clientes rara vez cambian de ciudad; cuando cambian, se usa la referencia inversa `cliente.pedidos` (≈ 5 pedidos) para actualizar las entradas.
        3. **W3 fuera de línea:** ejecutarlo de noche, sobre una réplica, o mantener un **agregado materializado** de ventas mensuales que se actualiza en cada *commit* de pedido, lo que lo reduce a unas cuantas páginas.

        Lección: el promedio de páginas no basta; **pondera por el tipo de operación** (interactiva o por lotes) y por su **acuerdo de nivel de servicio**.

# A2 · Proyecto final: plataforma de diseño CAD con versiones

**Nivel:** 🔴 Avanzado · **Lecciones:** todas · **Tiempo:** semana 13 (6–8 horas en total)

## 1. Planteamiento del problema

Una empresa de manufactura necesita una plataforma donde **40 ingenieros** diseñan **ensambles mecánicos** (motores, cajas de cambio). Cada ensamble contiene subensambles y piezas en una **jerarquía de hasta 12 niveles**, y cada pieza tiene geometría (malla de 10 KB a 5 MB), material y propiedades calculadas (masa, centro de gravedad). Los diseños pasan por **versiones** y **liberaciones**. Debes entregar la **arquitectura de persistencia** completa y defenderla.

## 2. Escenario de ejecución

Requisitos funcionales:

| Id | Requisito |
|---|---|
| RF1 | Abrir un ensamble y recorrer su árbol completo (≈ 5 000 piezas) en menos de 1 s |
| RF2 | Calcular la masa total del ensamble (método recursivo polimórfico: `Pieza.masa()` y `Ensamble.masa()`) |
| RF3 | Un ingeniero trabaja horas sobre un subensamble sin bloquear a los demás |
| RF4 | Cada *check-in* crea una nueva versión; las liberadas son inmutables |
| RF5 | Una «configuración» de producto fija qué versión de cada pieza se fabrica |
| RF6 | Buscar «todas las piezas de aluminio con masa > 2 kg en ensambles liberados» |
| RF7 | Agregar el atributo `proveedor` a `Pieza` sin detener el sistema |
| RF8 | Reportes mensuales de costos para el área financiera, que usa una herramienta de BI con SQL |

Restricciones: el equipo programa en **Java**; 2 sedes (Querétaro y Monterrey); presupuesto moderado.

## 3. Entradas y salidas

| Entrada | Entregable |
|---|---|
| Requisitos anteriores | **D1.** Matriz de decisión ponderada (L12) con al menos 4 alternativas |
| — | **D2.** Esquema ODL con herencia, relaciones inversas y versionado |
| — | **D3.** Estrategia de *clustering* e índices justificada para RF1 y RF6 |
| — | **D4.** Modelo transaccional para RF3–RF5 |
| — | **D5.** Plan de evolución de esquema para RF7 |
| — | **D6.** Estrategia para RF8 (BI) |
| — | **D7.** Consulta OQL de RF6 |
| — | **D8.** Presentación Feynman de 5 minutos: «¿por qué esta arquitectura y no una relacional con ORM?» |

## 4. Solución propuesta incompleta

```text
D1. Alternativas: (1) ________  (2) ________  (3) ObjectDB  (4) PostgreSQL + JPA
    Criterio decisivo: ________ (RF1) frente a ________ (RF8)

D2. interface Componente { float masa(); ... };
    class Pieza ____ Componente ( extent piezas ) { attribute string material; ... };
    class Ensamble ____ Componente ( extent ensambles ) {
        relationship list<Uso> usos inverse ____; ... };
    class Uso { attribute Matriz4x4 transformacion; relationship Componente ____ ...; };
    // ¿Dónde va la versión? ________________________________

D3. Clustering: ________ para RF1. La geometría pesada se guarda ________.
    Índices: ________ sobre (material, masa) restringido a ________.

D4. Transacciones: ________ (check-out/check-in) con BD privada por ingeniero,
    bloqueos ________ sobre el subensamble, versiones en estado ________ → ________ → liberada.

D5. RF7: conversión ________, valor por defecto ________.

D6. RF8: ________________________________

D7. select p from ____ p where ____ and ____ and exists e in ____: ____
```

---

## 5. Respuesta correcta esperada

??? success "Ver una solución de referencia (hay otras válidas si se justifican)"

    **D1. Matriz de decisión**

    | Criterio | Peso | Objectivity/DB | Versant | ObjectDB | PostgreSQL + JPA |
    |---|---|---|---|---|---|
    | Recorrido de grafos profundos (RF1, RF2) | 0.25 | 5 | 5 | 4 | 2 |
    | Versiones y transacciones largas (RF3–RF5) | 0.20 | 4 | 4 | 2 | 2 |
    | Ajuste a Java | 0.15 | 4 | 5 | 5 | 5 |
    | BI con SQL (RF8) | 0.10 | 2 | 2 | 3 | 5 |
    | Distribución en 2 sedes | 0.10 | 5 | 4 | 2 | 3 |
    | Talento y ecosistema | 0.10 | 2 | 2 | 3 | 5 |
    | Costo | 0.10 | 2 | 2 | 4 | 5 |
    | **Total** | 1.00 | **3.75** | **3.80** | **3.35** | **3.45** |

    Comprobación (siempre muestra las cuentas: el panel las revisa):

    | Alternativa | Suma ponderada |
    |---|---|
    | Objectivity/DB | 1.25 + 0.80 + 0.60 + 0.20 + 0.50 + 0.20 + 0.20 = **3.75** |
    | Versant | 1.25 + 0.80 + 0.75 + 0.20 + 0.40 + 0.20 + 0.20 = **3.80** |
    | ObjectDB | 1.00 + 0.40 + 0.75 + 0.30 + 0.20 + 0.30 + 0.40 = **3.35** |
    | PostgreSQL + JPA | 0.50 + 0.40 + 0.75 + 0.50 + 0.30 + 0.50 + 0.50 = **3.45** |

    Decisión: **un OODBMS con soporte de versiones y Java nativo (Versant u Objectivity/DB, prácticamente empatados)**, más una **réplica relacional** para BI (D6). Si el riesgo de proveedor o el costo pesaran más, la alternativa sería PostgreSQL + JPA, aceptando un RF1 más difícil (vistas materializadas, consultas recursivas `WITH RECURSIVE`).

    **D2. Esquema ODL**

    ```text
    module CAD {
      struct Matriz4x4 { array<double, 16> m; };
      enum EstadoVersion { TRANSITORIA, TRABAJO, LIBERADA };

      interface Componente {
        string codigo();
        double masa();                                  // polimórfica
      };

      class ObjetoGenerico ( extent genericos key codigo ) {   // identidad estable de la pieza
        attribute string codigo;
        relationship set<Version> versiones inverse Version::generico;
        relationship Version por_defecto inverse Version::es_defecto_de;
      };

      class Version ( extent versiones ) {
        attribute short numero;
        attribute EstadoVersion estado;
        attribute timestamp creada;
        relationship ObjetoGenerico generico inverse ObjetoGenerico::versiones;
        relationship set<ObjetoGenerico> es_defecto_de inverse ObjetoGenerico::por_defecto;
        relationship Version deriva_de inverse Version::derivadas;
        relationship set<Version> derivadas inverse Version::deriva_de;
      };

      class Pieza extends Version : Componente ( extent piezas ) {
        attribute string material;
        attribute double densidad;
        attribute Geometria geometria;                  // objeto propio, cargado bajo demanda
        attribute double masa_cache;                    // materialización de masa()
      };

      class Ensamble extends Version : Componente ( extent ensambles ) {
        relationship list<Uso> usos inverse Uso::padre;
      };

      class Uso ( extent usos ) {                       // reifica "el ensamble usa el componente con una transformación"
        attribute Matriz4x4 transformacion;
        attribute short cantidad;
        relationship Ensamble padre inverse Ensamble::usos;
        attribute ObjetoGenerico hijo_generico;         // referencia genérica (dinámica)
        attribute Version hijo_especifico;              // referencia específica (en liberaciones)
      };

      class Configuracion ( extent configuraciones key nombre ) {
        attribute string nombre;                        // "Motor-2.0-2026"
        attribute dictionary<string, Version> seleccion;   // codigo → versión fijada
      };
    };
    ```

    **D3. *Clustering* e índices**

    - ***Clustering* por composición**: cada `Ensamble` con sus `Uso` y las versiones de piezas pequeñas en el mismo contenedor (los *containers* de Objectivity/DB o los *placement hints* de Versant). RF1 se resuelve con pocas lecturas de páginas y la caché cliente.
    - **Geometría separada** en objetos o segmentos grandes que se cargan solo al visualizar (activación perezosa): recorrer 5 000 piezas no debe arrastrar gigabytes de mallas.
    - **`masa()` materializada** en `masa_cache`, invalidada cuando cambia la geometría, la densidad o un hijo (dependencias registradas).
    - **Índices:** índice compuesto `(material, masa_cache)` sobre `piezas`; índice sobre `estado` de las versiones, o mejor, un **índice parcial / contenedor separado** para versiones `LIBERADA`.

    **D4. Modelo transaccional**

    - **Transacciones largas** con *check-out* del subensamble a una **BD privada** del ingeniero, con un **bloqueo persistente** (X sobre el objeto genérico del subensamble; IX en los ancestros, siguiendo el protocolo jerárquico).
    - Dentro de su BD privada, el ingeniero usa **transacciones cortas** (cada guardado), así no pierde trabajo ante fallas.
    - ***Check-in*** = crear una nueva `Version` (`TRANSITORIA` → `TRABAJO`); un comité la pasa a `LIBERADA` (inmutable: los métodos de escritura lanzan una excepción).
    - Las configuraciones de RF5 usan **referencias específicas**; los ensambles en desarrollo usan **genéricas**.
    - Entre sedes: **replicación** de las versiones liberadas (solo lectura) y propiedad del *check-out* por sede para evitar el 2PC en el camino crítico.

    **D5. Evolución de esquema (RF7)**

    - Agregar `proveedor` a `Pieza` con **conversión perezosa** y valor por defecto `"POR_ASIGNAR"`; las versiones **liberadas no se reescriben** (son inmutables): se leen con *screening* (valor por defecto al vuelo).
    - Programa la migración inmediata solo para las versiones `TRABAJO` en una ventana nocturna, por lotes con *savepoints*.

    **D6. BI (RF8)**

    - Un proceso de **CDC / exportación nocturna** que proyecta las configuraciones liberadas a un **almacén relacional** (tablas `pieza`, `uso`, `configuracion`, `costo`). Finanzas consulta SQL sin tocar el OODBMS.
    - Alternativa con un motor multimodelo (por ejemplo, InterSystems IRIS) que proyecte las clases como tablas automáticamente.

    **D7. OQL de RF6**

    ```sql
    select p
    from piezas p
    where p.material = "Aluminio"
      and p.masa_cache > 2.0
      and exists u in usos:
            u.hijo_especifico = p and u.padre.estado = LIBERADA
    ```

    (Con referencias inversas de `Pieza` a sus `Uso`, el `exists` se evalúa sin recorrer el *extent* de `usos`; justificar esa referencia inversa es parte de la defensa.)

    **D8. Guion Feynman (5 min)**

    1. *El problema:* un motor es un árbol de miles de piezas que los ingenieros recorren y modifican durante horas.
    2. *Por qué no tablas:* reconstruir el árbol exige consultas recursivas y miles de *joins* o N+1; las versiones y los *check-out* no existen en el modelo relacional.
    3. *Qué hace el OODBMS:* guarda el árbol tal cual, agrupado físicamente; los métodos polimórficos calculan la masa; las versiones y las transacciones largas son nativas.
    4. *El precio:* BI y talento → réplica relacional y capacitación.
    5. *Cuándo cambiaría de opinión:* si el 80 % de la carga fueran reportes o si el proveedor fuera inviable.

    **Rúbrica (100 pts):** D1 15 · D2 20 · D3 15 · D4 15 · D5 10 · D6 5 · D7 10 · D8 10. **Aprobado ≥ 85.**

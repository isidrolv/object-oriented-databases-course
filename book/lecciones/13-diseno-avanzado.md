# Lección 13 · Diseño avanzado, casos y frontera de investigación

## Objetivos

- Aplicar un **marco de decisión** para elegir entre BDOO, SGBDOR, ORM, documentos o grafos.
- Modelar dominios complejos (CAD, telecomunicaciones, salud) con patrones de BDOO.
- Razonar sobre **distribución**, **seguridad** y **multimodelo**.
- Identificar los **temas abiertos** de investigación.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Un buen carpintero no usa el martillo para todo. Sabe cuándo usar martillo, cuándo serrucho y cuándo pegamento. Ser experto en bases de datos de objetos es saber **cuándo sí** y, sobre todo, **cuándo no** usarlas.

## 1. Marco de decisión

```text
¿El dominio es un grafo profundo de objetos con mucha navegación
 y comportamiento rico (CAD, simulación, telecomunicaciones)?
 ├── No → ¿Se necesitan consultas ad hoc, BI y muchos lenguajes?
 │        ├── Sí → Relacional (+ ORM si la app es OO)
 │        └── No → ¿Estructura flexible y anidada? → Documentos
 │                 ¿Relaciones como ciudadanas de primera clase? → Grafos
 └── Sí → ¿Un solo lenguaje dominante y equipo que acepta un motor de nicho?
          ├── Sí → OODBMS (GemStone/S, ObjectDB, ZODB, Objectivity/DB…)
          └── No → Objeto-relacional (tipos y extensiones) o multimodelo (IRIS)
```

### Señales a favor de una BDOO

- Grafos con **recorridos de muchos niveles** en caliente (cientos o miles de desreferencias por operación).
- **Comportamiento** que conviene ejecutar cerca de los datos.
- **Versiones** y **transacciones largas** (diseño de ingeniería).
- Un **único lenguaje** dominante en todo el sistema.
- Tipos de datos complejos que no encajan en tablas (geometrías, árboles, redes).

### Señales en contra

- Reportes *ad hoc*, BI y analítica en SQL como requisito central.
- Muchos sistemas en distintos lenguajes comparten los datos.
- Poco talento disponible o riesgo de proveedor inaceptable.
- Cargas mayormente orientadas a conjuntos (agregaciones masivas).

## 2. Patrones de modelado para dominios complejos

| Patrón | Uso | Ejemplo |
|---|---|---|
| **Objeto compuesto con partes exclusivas** | Borrado, bloqueo y *clustering* en cascada | `Ensamble` → `Pieza` |
| **Lista de materiales** (*Bill of Materials*) recursiva | Estructuras parte-de | `Componente.subcomponentes: set<Componente>` |
| **Objeto genérico + versiones** | Diseño de ingeniería | `Plano` con `v1…vn` y configuraciones |
| **Raíces por agregado** | Puntos de entrada pequeños y estables | `root["clientes"]`, `root["catalogo"]` (similar a los agregados de DDD) |
| **Índices como objetos** | Colecciones grandes navegables | `OOBTree` de ZODB para `clientes_por_correo` |
| **Objetos valor inmutables** | Evitar OID innecesarios | `Dinero`, `Coordenada`, `RangoFechas` |
| **Referencias inversas mantenidas** | Recorrido hacia atrás sin escanear | `Curso.inscritos` ↔ `Estudiante.inscripciones` |

### Caso: red de telecomunicaciones

```text
Red ─┬─▶ Nodo (Router, Switch, Antena)  ← herencia + polimorfismo: nodo.capacidad()
     ├─▶ Enlace(origen: Nodo, destino: Nodo, ancho_banda)
     └─▶ Servicio ─▶ Ruta: list<Enlace>
Operación típica: "¿qué servicios se caen si falla el nodo N?"
→ recorrer Enlaces incidentes a N → Rutas que los usan → Servicios
→ exige referencias inversas (Nodo.enlaces, Enlace.rutas) y clustering por región
```

### Caso: historia clínica

```text
Paciente ─▶ Episodio ─▶ Encuentro ─▶ Observación (polimórfica: Signo, Laboratorio, Imagen)
• Versiones: cada corrección crea una versión; nunca se borra (requisito legal).
• Consultas poblacionales (BI) → proyección SQL (estilo IRIS) o réplica a un almacén analítico.
```

## 3. Distribución

| Técnica | Idea | Ejemplo |
|---|---|---|
| **Federación** | Varias BD con un catálogo común y OID globales | Objectivity/DB |
| **Replicación** | Copias de objetos para lectura o disponibilidad | Versant, ZEO con réplicas (ZRS) |
| **Particionamiento por agregado** | Cada partición contiene raíces completas | Agregados DDD por nodo |
| **Commit distribuido** | 2PC entre servidores | Versant, Objectivity/DB |

Problemas específicos: **referencias entre particiones** (OID globales y desreferencias remotas), **GC distribuido** y **coherencia de cachés** entre varios servidores.

## 4. Seguridad

- **Autorización sobre objetos, clases y métodos:** conceder `ejecutar(aumentar_salario)` en lugar de `UPDATE salario`.
- **Autorización implícita** (Rabitti, Bertino, Kim y Woelk, 1991): derivar permisos a lo largo de la jerarquía de clases, de objetos compuestos y del esquema (p. ej., leer una clase implica leer sus instancias), con autorizaciones **positivas y negativas**, **fuertes y débiles**.
- **Encapsulamiento como mecanismo de seguridad:** si solo se accede por métodos, los métodos aplican las reglas.
- **Riesgos:** código del método ejecutado en el servidor (inyección o métodos maliciosos), deserialización insegura (p. ej., *pickles* de Python: nunca cargar un `FileStorage` de origen no confiable).

## 5. Multimodelo y convergencia

- **InterSystems IRIS:** objetos, SQL, documentos y *globals* sobre el mismo almacenamiento.
- **PostgreSQL:** tipos compuestos, `jsonb`, extensiones (PostGIS, `pgvector`).
- **Oracle:** tipos de objeto, JSON, grafos (SQL/PGQ) y documentos.
- **SQL:2023** añadió **SQL/PGQ** (consultas de grafos de propiedades sobre tablas) y mejoró el soporte de JSON; **GQL** se publicó como ISO/IEC 39075 en 2024.

La tendencia: el **modelo de objetos** vive en la aplicación y en los lenguajes de consulta, mientras los motores se vuelven **multimodelo**.

## 6. Frontera de investigación y temas abiertos

1. **Optimización de consultas con métodos opacos** y aprendizaje automático (estimación de costo y selectividad aprendida).
2. ***Clustering* adaptativo** basado en trazas de acceso.
3. **Memoria persistente** (NVM): persistencia ortogonal a nivel de lenguaje sobre memoria direccionable por bytes; reaparece el problema del *swizzling* y la consistencia ante fallas.
4. **Evolución de esquema** continua en sistemas sin interrupciones (*zero-downtime*).
5. **Integración con lenguajes** (*language-integrated query*: LINQ, Kotlin/Exposed, ORM con tipos verificados).
6. **Objetos en la frontera (*edge*)** con sincronización y resolución de conflictos (CRDT).
7. **Vectores y objetos:** BD orientadas a objetos con búsqueda vectorial para IA en el dispositivo (ObjectBox).

## 7. Cómo demostrar dominio del 1 % superior

- Explica **por qué** las BDOO no dominaron el mercado y **dónde** siguen ganando.
- Traduce un mismo modelo a **ODL, SQL:1999, Oracle, PostgreSQL, JPA y ZODB**.
- Diseña *clustering* e índices **a partir de la carga de trabajo**.
- Argumenta compromisos con números: desreferencias, páginas leídas, conflictos por segundo.
- Cita fuentes primarias: el Manifiesto de 1989, ODMG 3.0, ORION, OO7, Shekita y Carey, Bertino y Kim.

## Lecturas recomendadas

| Fuente | Por qué |
|---|---|
| Atkinson et al., *The Object-Oriented Database System Manifesto* (1989) | Definición canónica |
| Cattell et al., *The Object Data Standard: ODMG 3.0* (2000) | Estándar completo |
| Kim, *Introduction to Object-Oriented Databases* (MIT Press, 1990) | Fundamentos de ORION |
| Bertino y Martino, *Object-Oriented Database Systems: Concepts and Architectures* (1993) | Índices, consultas y arquitectura |
| Elmasri y Navathe, *Fundamentals of Database Systems*, capítulos de BD de objetos y objeto-relacionales | Visión de libro de texto |
| Fowler, *Patterns of Enterprise Application Architecture* (2002) | Patrones de ORM |
| Carey, DeWitt y Naughton, *The OO7 Benchmark* (SIGMOD 1993) | Rendimiento |
| Documentación de ZODB, ObjectDB, GemStone/S e InterSystems IRIS | Práctica actual |

## Errores comunes

- ❌ Defender la BDOO como una solución universal.
- ❌ Ignorar la seguridad del código que se ejecuta en el servidor o de la deserialización.
- ❌ Diseñar sin una carga de trabajo explícita.

## Conexiones (intercalación)

Esta lección **integra todo**: el ejercicio [A2](../ejemplos/A2-proyecto-final.md) exige combinar ODL (L03), OQL (L04), persistencia (L05), *clustering* (L06), transacciones (L07), evolución (L08) y selección de tecnología (L12).

## Preguntas de recuerdo activo

1. Nombra tres señales a favor y tres en contra de usar una BDOO.
2. ¿Qué es la autorización implícita en BDOO?
3. ¿Qué problemas específicos trae la distribución de objetos?
4. ¿Por qué la memoria persistente reabre el problema del *swizzling*?
5. ¿Qué añadió SQL:2023 relacionado con grafos?

??? success "Respuestas"
    1. A favor: grafos profundos navegados en caliente, comportamiento cerca de los datos, versiones y transacciones largas, un solo lenguaje. En contra: BI y consultas *ad hoc*, muchos lenguajes, poco talento o riesgo de proveedor, cargas orientadas a conjuntos.
    2. Derivar permisos a lo largo de las jerarquías de clases, de objetos compuestos y del esquema, combinando autorizaciones positivas y negativas, fuertes y débiles.
    3. Referencias entre particiones con OID globales, GC distribuido, coherencia de cachés y *commit* distribuido (2PC).
    4. Porque los punteros persistentes en memoria direccionable por bytes deben seguir siendo válidos entre ejecuciones con direcciones distintas, y hay que garantizar consistencia ante fallas sin bitácora tradicional.
    5. SQL/PGQ, que permite definir grafos de propiedades sobre tablas y consultarlos con patrones.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| Raíz por agregado | Punto de entrada pequeño y estable por agregado de dominio |
| Federación (Objectivity/DB) | Varias BD con catálogo común y OID globales |
| Riesgo de *pickles* | Deserializar datos no confiables puede ejecutar código |
| GQL | Lenguaje estándar ISO de consultas de grafos (ISO/IEC 39075, 2024) |
| Señal clave de experto | Saber cuándo NO usar una BDOO |

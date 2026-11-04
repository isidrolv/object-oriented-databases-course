# Glosario

| Término | Definición | Lección |
|---|---|---|
| **Access Support Relation** | Relación materializada que guarda (total o parcialmente) las instanciaciones de una ruta para acelerar consultas | 06 |
| **Activation depth** | En db4o, número de niveles del grafo que se cargan al recuperar un objeto | 05 |
| **Bag** | Multiconjunto: colección sin orden que admite duplicados | 02, 04 |
| **Bytecode enhancement** | Instrumentación de clases compiladas para interceptar accesos a campos (JDO) | 05 |
| **Callback locking** | Protocolo de coherencia de caché: el cliente conserva bloqueos y el servidor le pide liberarlos | 06 |
| **Check-out / check-in** | Copiar objetos a una BD privada con bloqueo persistente y devolverlos creando una nueva versión | 07 |
| **Class hierarchy index** | Un solo índice para todas las clases de una jerarquía | 06 |
| **Clustering** | Colocar juntos físicamente los objetos que se acceden juntos | 06 |
| **Configuración** | Conjunto coherente de versiones de varios objetos | 08 |
| **Desajuste de impedancia** | Diferencias entre el modelo de objetos de la aplicación y el modelo relacional | 01 |
| **Extent** | Conjunto de todas las instancias persistentes de un tipo (incluye las de sus subtipos) | 02, 03 |
| **Fantasma (ghost / hollow)** | Objeto en memoria con OID pero sin estado cargado | 05 |
| **Identity map** | Patrón que garantiza un único objeto en memoria por identidad dentro de una sesión | 10 |
| **Igualdad profunda** | Grafos de objetos isomorfos con valores hoja iguales | 02 |
| **Igualdad superficial** | Mismos valores y mismas referencias | 02 |
| **Índice anidado** | Mapea el valor final de una ruta a los objetos iniciales | 06 |
| **Índice de ruta** | Mapea el valor final de una ruta a sus instanciaciones completas | 06 |
| **Late binding** | Elección de la implementación de un método en tiempo de ejecución según el tipo real | 02 |
| **Literal** | Valor sin OID (ODMG): atómico, estructurado o colección | 02, 03 |
| **Materialización de métodos** | Precalcular y almacenar el resultado de un método con invalidación por dependencias | 11 |
| **MVCC** | Control de concurrencia multiversión: cada transacción lee una instantánea | 07 |
| **N+1** | Patrón de rendimiento en el que una consulta inicial desencadena N consultas adicionales | 10 |
| **ODL** | *Object Definition Language* del ODMG | 03 |
| **ODMG** | *Object Data Management Group*; estándar 3.0 (2000) | 03 |
| **OID** | Identificador de objeto: único, inmutable, generado por el sistema e independiente del valor | 02 |
| **OIF** | *Object Interchange Format*: formato de volcado y carga de objetos | 03 |
| **OQL** | *Object Query Language*: lenguaje declarativo, funcional y ortogonal | 04 |
| **Page server / object server** | Arquitecturas cliente-servidor que transfieren páginas u objetos | 06 |
| **Partition** | En OQL, la colección de miembros de cada grupo de un `group by` | 04 |
| **Persistencia ortogonal** | Ortogonalidad de tipos + persistencia por alcanzabilidad + independencia de la persistencia | 05 |
| **Persistencia por alcanzabilidad** | Todo objeto alcanzable desde una raíz persistente se vuelve persistente | 05 |
| **Pointer swizzling** | Convertir OID en punteros de memoria (y al revés al escribir) | 05 |
| **REF** | Tipo de referencia de SQL:1999 a una fila de una tabla tipada | 09 |
| **Referencia genérica / específica** | Apunta al objeto genérico (versión por defecto) o a una versión fija | 08 |
| **Saga** | Secuencia de transacciones locales con compensaciones | 07 |
| **Screening** | Técnica de ORION que adapta las instancias antiguas al leerlas, sin reescribirlas | 08 |
| **SIX** | Modo de bloqueo *Shared + Intention eXclusive* | 07 |
| **Tabla tipada** | `CREATE TABLE t OF tipo`; cada fila es una instancia | 09 |
| **Transacción anidada** | Árbol de subtransacciones que pueden abortar de forma independiente; los efectos se heredan al padre | 07 |
| **Unit of work** | Patrón que registra cambios y los escribe juntos al confirmar | 10 |

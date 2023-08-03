# Construir un "Lake House" en la Arquitectura de AWS

### **[Link](https://docs.aws.amazon.com/es_es/prescriptive-guidance/latest/defining-bucket-names-data-lakes/welcome.html)**

Las organizaciones pueden obtener conocimientos más profundos y ricos cuando reúnen todos sus datos relevantes de todas las estructuras y tipos y de todas las fuentes para analizarlos. Para analizar estas enormes cantidades de datos, toman todos sus datos de varios silos y los agregan en una ubicación, lo que muchos llaman un lago de datos, para realizar análisis y ML directamente sobre esos datos. En otras ocasiones, almacenan otros datos en almacenes de datos específicos, como un almacén de datos para obtener resultados rápidos de consultas complejas sobre datos estructurados, o en un servicio de búsqueda para buscar y analizar rápidamente datos de registro para supervisar el estado de los sistemas de producción. Para obtener la mejor información de todos sus datos, estas organizaciones necesitan mover los datos entre sus lagos de datos y estos almacenes específicos con facilidad. A medida que los datos de estos sistemas crecen, se hace más difícil moverlos. Para superar este problema de gravedad de los datos y moverlos fácilmente para sacar el máximo partido de todos ellos, se introdujo un enfoque de Lake House en AWS.

En este post, presentamos cómo crear este enfoque de Lake House en AWS que le permite obtener información de volúmenes de datos que crecen exponencialmente y le ayuda a tomar decisiones con velocidad y agilidad. Este enfoque de Lake House proporciona las capacidades que necesita para adoptar la gravedad de los datos mediante el uso de un lago de datos central, un anillo de servicios de datos creados específicamente en torno a ese lago de datos y la capacidad de mover fácilmente los datos que necesita entre estos almacenes de datos.

## Enfoque Lake House

Como arquitectura de datos moderna, el enfoque Lake House no consiste únicamente en integrar el lago de datos y el almacén de datos, sino en conectar el lago de datos, el almacén de datos y todos los demás servicios creados específicamente para formar un todo coherente. El lago de datos le permite disponer de un único lugar en el que ejecutar análisis de la mayor parte de sus datos, mientras que los servicios de análisis específicos proporcionan la velocidad que necesita para casos de uso concretos, como cuadros de mando en tiempo real y análisis de registros.

Este enfoque de Lake House consta de los siguientes elementos clave:

- Lagos de datos escalables
- Servicios de datos específicos
- Movimiento de datos sin fisuras
- Gobernanza unificada
- Rendimiento y rentabilidad

Una arquitectura de análisis de datos por capas y componentes le permite utilizar la herramienta adecuada para cada tarea y le proporciona la agilidad necesaria para desarrollar la arquitectura de forma iterativa e incremental. Obtendrá la flexibilidad de hacer evolucionar su Lake House por componentes para satisfacer las necesidades actuales y futuras a medida que añada nuevas fuentes de datos, descubra nuevos casos de uso y sus requisitos, y desarrolle nuevos métodos de análisis.

Para esta arquitectura de Lake House, puede organizarla como una pila de cinco capas lógicas, en la que cada capa se compone de múltiples componentes creados a propósito que abordan requisitos específicos.

En esta sección describimos estas cinco capas, pero hablemos primero de las fuentes que alimentan la arquitectura de Lake House.

### Fuentes de datos

La arquitectura de Lake House le permite ingerir y analizar datos de diversas fuentes. Muchas de estas fuentes, como las aplicaciones de línea de negocio (LOB), las aplicaciones ERP y las aplicaciones CRM, generan lotes de datos altamente estructurados a intervalos fijos. Además de las fuentes estructuradas internas, puede recibir datos de fuentes modernas como aplicaciones web, dispositivos móviles, sensores, flujos de vídeo y redes sociales. Estas fuentes modernas suelen generar datos semiestructurados y no estructurados, a menudo como flujos continuos.

### Capa de ingestión de datos

La capa de ingestión de la arquitectura de Lake House es responsable de la ingestión de datos en la capa de almacenamiento de Lake House. Proporciona la capacidad de conectarse a fuentes de datos internas y externas a través de una variedad de protocolos. Puede ingerir y entregar datos por lotes y en tiempo real a un almacén de datos, así como a los componentes del lago de datos de la capa de almacenamiento de Lake House.

### Capa de almacenamiento de datos

La capa de almacenamiento de datos de la arquitectura Lake House es responsable de proporcionar componentes duraderos, escalables y rentables para almacenar y gestionar grandes cantidades de datos. En una arquitectura Lake House, el almacén de datos y el lago de datos se integran de forma nativa para proporcionar una capa de almacenamiento rentable integrada que admite datos no estructurados, así como datos altamente estructurados y modelados. La capa de almacenamiento puede almacenar datos en diferentes estados de preparación para el consumo, incluidos datos sin procesar, conformados de confianza, enriquecidos y modelados.

### Almacenamiento de datos estructurados en el almacén de datos

El almacén de datos almacena datos conformados y altamente fiables, estructurados en esquemas tradicionales de estrella, copo de nieve, bóveda de datos o altamente desnormalizados. Los datos almacenados en un almacén suelen proceder de fuentes internas y externas altamente estructuradas, como sistemas transaccionales, bases de datos relacionales y otras fuentes operativas estructuradas, normalmente con una cadencia regular. Los almacenes de datos modernos nativos de la nube pueden almacenar normalmente datos a escala de petabytes en volúmenes de almacenamiento integrados de alto rendimiento en un formato columnar comprimido. Gracias a los motores MPP y al rápido almacenamiento conectado, un almacén de datos moderno nativo de la nube proporciona una baja latencia en las consultas SQL complejas.

Para proporcionar datos altamente curados, conformes y fiables, antes de almacenar los datos en un almacén, es necesario someter los datos de origen a una cantidad significativa de preprocesamiento, validación y transformación mediante canalizaciones de extracción, transformación y carga (ETL) o de extracción, carga y transformación (ELT). Todos los cambios en los datos y esquemas del almacén de datos están estrictamente controlados y validados para proporcionar una fuente de datos de gran confianza en todos los dominios empresariales.

#### Almacenamiento de datos estructurados y no estructurados en una arquitectura de lago de datos

Un lago de datos es el repositorio de datos centralizado que almacena todos los datos de una organización. Admite el almacenamiento de datos en formatos estructurados, semiestructurados y no estructurados. Proporciona un almacenamiento por niveles de coste muy optimizado y puede escalarse automáticamente para almacenar exabytes de datos. Normalmente, un lago de datos se segmenta en zonas de aterrizaje, sin procesar, de confianza y curadas para almacenar datos en función de su preparación para el consumo. Normalmente, los datos se ingieren y almacenan tal cual en el lago de datos (sin tener que definir primero el esquema) para acelerar la ingestión y reducir el tiempo necesario para la preparación antes de que los datos puedan ser explorados. El lago de datos permite el análisis de diversos conjuntos de datos utilizando diversos métodos, incluido el procesamiento de big data y ML. La integración nativa entre un lago de datos y un almacén de datos también reduce los costes de almacenamiento al permitir descargar una gran cantidad de datos históricos más fríos del almacenamiento del almacén.

### Capa de catálogo

La capa de catálogo se encarga de almacenar metadatos empresariales y técnicos sobre los conjuntos de datos alojados en la capa de almacenamiento de Lake House. En una arquitectura Lake House, el catálogo es compartido tanto por el lago de datos como por el almacén de datos, y permite escribir consultas que incorporan datos almacenados en el lago de datos así como en el almacén de datos en el mismo SQL. Permite realizar un seguimiento de los esquemas versionados y de la información granular de partición de los conjuntos de datos. A medida que crece el número de conjuntos de datos, esta capa hace que los conjuntos de datos de Lake House sean localizables proporcionando capacidades de búsqueda.

### Interfaz de Lake House

En la arquitectura de Lake House, el almacén de datos y el lago de datos se integran de forma nativa en las capas de almacenamiento y de catálogo común para presentar una interfaz unificada de Lake House a las capas de procesamiento y consumo. De este modo, los componentes de las capas de procesamiento y consumo de Lake House pueden consumir todos los datos almacenados en la capa de almacenamiento de Lake House (almacenados tanto en el almacén de datos como en el lago de datos) a través de una única interfaz unificada de Lake House, como SQL o Spark. No es necesario mover datos entre el almacén de datos y el lago de datos en ninguna dirección para permitir el acceso a todos los datos del almacenamiento de Lake House.

La integración nativa entre el almacén de datos y el lago de datos le ofrece la flexibilidad de hacer lo siguiente:

- Almacenar exabytes de datos estructurados y no estructurados en un almacenamiento de data lake altamente rentable como datos estructurados altamente curados, modelados y conformados en un almacenamiento de data warehouse en caliente.
- Aprovechar un único marco de procesamiento, como Spark, que puede combinar y analizar todos los datos en una única canalización, tanto si se trata de datos no estructurados en el lago de datos como de datos estructurados en el almacén de datos.
- Construir una canalización ETL o ELT nativa del almacén de datos basada en SQL que pueda combinar datos relacionales planos en el almacén con datos estructurados jerárquicos complejos en el lago de datos.

### Capa de procesamiento de datos

Los componentes de la capa de procesamiento de datos de la arquitectura del lago de datos se encargan de transformar los datos en un estado consumible mediante la validación, limpieza, normalización, transformación y enriquecimiento de los datos. La capa de procesamiento proporciona componentes creados específicamente para realizar diversas transformaciones, como SQL al estilo de los almacenes de datos, procesamiento de big data y ETL casi en tiempo real.

La capa de procesamiento proporciona el tiempo de comercialización más rápido al proporcionar componentes creados específicamente que coinciden con las características adecuadas del conjunto de datos (tamaño, formato, esquema, velocidad), la tarea de procesamiento en cuestión y los conjuntos de habilidades disponibles (SQL, Spark). La capa de procesamiento puede escalar de forma rentable para gestionar grandes volúmenes de datos y proporcionar componentes que admitan esquemas en escritura, esquemas en lectura, conjuntos de datos particionados y diversos formatos de datos. La capa de procesamiento puede acceder a las interfaces de almacenamiento unificadas de Lake House y al catálogo común, accediendo así a todos los datos y metadatos de Lake House. Esto tiene las siguientes ventajas

- Evita las redundancias de datos, el movimiento innecesario de datos y la duplicación del código ETL que puede producirse al tratar un lago de datos y un almacén de datos por separado.
- Reduce el tiempo de comercialización

### Capa de consumo de datos

La capa de consumo de datos de la arquitectura de Lake House se encarga de proporcionar componentes escalables y de alto rendimiento que utilizan interfaces unificadas de Lake House para acceder a todos los datos almacenados en el almacén de Lake House y a todos los metadatos almacenados en el catálogo de Lake House. Democratiza el análisis para permitir a todas las personas de una organización proporcionando componentes creados específicamente que permiten métodos de análisis, incluidas consultas SQL interactivas, análisis de estilo de almacén, paneles de BI y ML.

Los componentes de la capa de consumo admiten lo siguiente:

- Escritura de consultas, así como trabajos de análisis y ML que acceden y combinan datos de esquemas dimensionales tradicionales de almacén de datos, así como tablas alojadas en data lake (que requieren schema-on-read).
- Manejar conjuntos de datos alojados en data lake que se almacenan utilizando una variedad de formatos de archivo abiertos como Avro, Parquet u ORC.
- Optimización del rendimiento y los costes mediante la poda de particiones al leer grandes conjuntos de datos particionados alojados en el lago de datos.

En el resto de este artículo, presentamos una arquitectura de referencia que utiliza los servicios de AWS para componer cada capa descrita en nuestra arquitectura lógica de Lake House. En este enfoque, los servicios de AWS se encargan del trabajo pesado de lo siguiente

- Proporcionar y administrar componentes de infraestructura escalables, resistentes, seguros y rentables
- Garantizar que los componentes de infraestructura se integren de forma nativa entre sí

Este enfoque le permite dedicar más tiempo a las siguientes tareas:

- Construir rápidamente canalizaciones de datos y análisis
- Acelerar significativamente la incorporación de nuevos datos y la obtención de información a partir de los mismos.
- Dar soporte a múltiples usuarios

## Arquitectura de referencia de Lake House en AWS

El siguiente diagrama ilustra nuestra arquitectura de referencia de Lake House en AWS.

![](https://docs.aws.amazon.com/images/prescriptive-guidance/latest/defining-bucket-names-data-lakes/images/data-lake-naming-diag-2.png)

En las siguientes secciones, ofrecemos más información sobre cada capa.

#### Capa de ingestión de datos

La capa de ingesta de nuestra arquitectura de referencia de Lake House se compone de un conjunto de servicios de AWS creados específicamente para permitir la ingesta de datos de diversas fuentes en la capa de almacenamiento de Lake House. La mayoría de los servicios de ingestión pueden entregar datos directamente al lago de datos y al almacenamiento del almacén de datos. Los servicios de AWS creados específicamente cumplen los requisitos únicos de conectividad, formato de datos, estructura de datos y velocidad de datos de las siguientes fuentes:

- Fuentes de bases de datos operativas
- Aplicaciones de software como servicio (SaaS)
- Archivos compartidos
- Fuentes de datos de streaming

#### Fuentes de bases de datos operativas (OLTP, ERP, CRM)

El componente AWS Data Migration Service (AWS DMS) de la capa de ingestión puede conectarse a varias bases de datos RDBMS y NoSQL operativas e ingestar sus datos en buckets de Amazon Simple Storage Service (Amazon S3) en el lago de datos o directamente en tablas de preparación en un almacén de datos de Amazon Redshift. Con AWS DMS, puede realizar una importación única de los datos de origen y, a continuación, replicar los cambios continuos que se produzcan en la base de datos de origen.

#### Aplicaciones SaaS

La capa de ingesta utiliza Amazon AppFlow para ingerir fácilmente datos de aplicaciones SaaS en su lago de datos. Con unos pocos clics, puede configurar flujos de ingesta de datos sin servidor en Amazon AppFlow. Sus flujos pueden conectarse a aplicaciones SaaS como Salesforce, Marketo y Google Analytics, ingerir datos y entregarlos a la capa de almacenamiento de Lake House, ya sea en buckets de S3 en el lago de datos o directamente en tablas de preparación en el almacén de datos de Amazon Redshift. Puede programar los flujos de ingesta de datos de Amazon AppFlow o activarlos mediante eventos en la aplicación SaaS. Los datos ingestados se pueden validar, filtrar, asignar y enmascarar antes de entregarlos al almacenamiento de Lake House.

#### Archivos compartidos

Muchas aplicaciones almacenan datos estructurados y no estructurados en archivos alojados en matrices de almacenamiento conectado a red (NAS). AWS DataSync puede ingerir cientos de terabytes y millones de archivos de dispositivos NAS habilitados para NFS y SMB en la zona de aterrizaje del lago de datos. DataSync gestiona automáticamente la creación de scripts de los trabajos de copia, la programación y la monitorización de las transferencias, la validación de la integridad de los datos y la optimización de la utilización de la red. DataSync puede realizar una única transferencia de archivos y, a continuación, supervisar y sincronizar los archivos modificados en Lake House. DataSync está totalmente gestionado y puede configurarse en cuestión de minutos.

#### Fuentes de datos en streaming

La capa de ingestión utiliza Amazon Kinesis Data Firehose para recibir datos de streaming de fuentes internas o externas y entregarlos a la capa de almacenamiento de Lake House. Con unos pocos clics, puede configurar un punto de enlace API de Kinesis Data Firehose donde las fuentes pueden enviar datos de streaming como secuencias de clics, logs de aplicaciones e infraestructura y métricas de monitorización, y datos de IoT como telemetría de dispositivos y lecturas de sensores. Kinesis Data Firehose realiza las siguientes acciones:

- Almacena en búfer los flujos entrantes
- Agrupa, comprime, transforma, particiona y cifra los datos
- Entrega los datos como objetos S3 al lago de datos o como filas en tablas de preparación en el almacén de datos de Amazon Redshift.

Kinesis Data Firehose no tiene servidor, no requiere administración y tiene un modelo de costos en el que solo paga por el volumen de datos que transmite y procesa a través del servicio. Kinesis Data Firehose se escala automáticamente para ajustarse al volumen y rendimiento de los datos entrantes. Para crear canalizaciones de análisis de streaming en tiempo real, la capa de ingestión proporciona Amazon Kinesis Data Streams.

#### Capa de almacenamiento Lake House

Amazon Redshift y Amazon S3 proporcionan una capa de almacenamiento unificada e integrada de forma nativa en nuestra arquitectura de referencia de Lake House. Normalmente, Amazon Redshift almacena datos altamente curados, conformados y de confianza que están estructurados en esquemas dimensionales estándar, mientras que Amazon S3 proporciona almacenamiento de lago de datos a escala de exabytes para datos estructurados, semiestructurados y no estructurados. Gracias a la compatibilidad con datos semiestructurados de Amazon Redshift, también puede ingerir y almacenar datos semiestructurados en sus almacenes de datos de Amazon Redshift. Amazon S3 ofrece escalabilidad, disponibilidad de datos, seguridad y desempeño líderes del sector. Las organizaciones suelen almacenar datos en Amazon S3 utilizando formatos de archivo abiertos. Los formatos de archivo abiertos permiten analizar los mismos datos de Amazon S3 utilizando varios componentes de capas de procesamiento y consumo. La capa de catálogo común almacena los esquemas de conjuntos de datos estructurados o semiestructurados en Amazon S3. Los componentes que consumen el conjunto de datos de S3 suelen aplicar este esquema al conjunto de datos a medida que lo leen (también conocido como esquema en lectura).

Amazon Redshift Spectrum es una de las piezas centrales de la capa de almacenamiento del lago de datos integrada de forma nativa. Redshift Spectrum permite a Amazon Redshift presentar una interfaz SQL unificada que puede aceptar y procesar sentencias SQL en las que la misma consulta puede hacer referencia y combinar conjuntos de datos alojados en el lago de datos, así como en el almacenamiento del almacén de datos. Amazon Redshift puede consultar petabytes de datos almacenados en Amazon S3 utilizando una capa de hasta miles de nodos transitorios de Redshift Spectrum y aplicando las sofisticadas optimizaciones de consultas de Amazon Redshift. Redshift Spectrum puede consultar datos particionados en el lago de datos de S3. Puede leer datos comprimidos mediante un códec de código abierto y almacenados en formatos de filas o columnas de código abierto, incluidos JSON, CSV, Avro, Parquet, ORC y Apache Hudi. Para obtener más información, consulte Creación de archivos de datos para consultas en Amazon Redshift Spectrum.

A medida que Redshift Spectrum lee conjuntos de datos almacenados en Amazon S3, aplica el esquema correspondiente del catálogo común de AWS Lake Formation a los datos (schema-on-read). Con Redshift Spectrum, puede crear canalizaciones nativas de Amazon Redshift que realicen las siguientes acciones:

- Mantener grandes volúmenes de datos históricos en el lago de datos e ingerir unos meses de datos en caliente en el almacén de datos mediante Redshift Spectrum.
- Producir conjuntos de datos enriquecidos procesando tanto los datos calientes en el almacenamiento adjunto como los datos históricos en el lago de datos, todo ello sin mover los datos en ninguna dirección
- Inserte filas de conjuntos de datos enriquecidos en una tabla almacenada en el almacenamiento adjunto o directamente en la tabla externa alojada en el lago de datos.
- Descargar fácilmente volúmenes de grandes datos históricos más fríos del almacén de datos en un almacenamiento del lago de datos más económico y seguir consultándolos fácilmente como parte de las consultas de Amazon Redshift

Los datos altamente estructurados en Amazon Redshift suelen impulsar consultas interactivas y paneles de BI rápidos y de gran confianza, mientras que los datos estructurados, no estructurados y semiestructurados en Amazon S3 suelen impulsar casos de uso de ML, ciencia de datos y procesamiento de big data.

AWS DMS y Amazon AppFlow en la capa de ingestión pueden entregar datos de fuentes estructuradas directamente al lago de datos de S3 o al almacén de datos de Amazon Redshift para satisfacer los requisitos de los casos de uso. En el caso de la ingestión de archivos de datos, DataSync lleva los datos a Amazon S3. Los componentes de la capa de procesamiento pueden acceder a los datos de la capa unificada de almacenamiento del lago de datos a través de una única interfaz unificada, como Amazon Redshift SQL, que puede combinar los datos almacenados en el clúster de Amazon Redshift con los datos de Amazon S3 mediante Redshift Spectrum.

En el lago de datos S3, los datos estructurados y no estructurados se almacenan como objetos S3. Los objetos de S3 en el lago de datos se organizan en buckets o prefijos que representan zonas de aterrizaje, sin procesar, de confianza y curadas. Para las canalizaciones que almacenan datos en el lago de datos de S3, los datos se ingieren desde la fuente en la zona de aterrizaje tal cual. A continuación, la capa de procesamiento valida los datos de la zona de destino y los almacena en el bucket o prefijo de la zona sin procesar para su almacenamiento permanente. A continuación, la capa de procesamiento aplica el esquema, la partición y otras transformaciones a los datos de la zona sin procesar para llevarlos a un estado conforme y los almacena en la zona de confianza. Como último paso, la capa de procesamiento cura un conjunto de datos de la zona de confianza modelándolo y uniéndolo con otros conjuntos de datos, y lo almacena en la capa curada. Normalmente, los conjuntos de datos de la capa curada se ingieren parcial o totalmente en el almacenamiento del almacén de datos de Amazon Redshift para atender casos de uso que requieren acceso de latencia muy baja o que necesitan ejecutar consultas SQL complejas.

El conjunto de datos de cada zona suele estar dividido en función de una clave que coincide con un patrón de consumo específico de la zona correspondiente (sin procesar, de confianza o curado). Los objetos S3 correspondientes a los conjuntos de datos se comprimen, utilizando códecs de código abierto como GZIP, BZIP y Snappy, para reducir los costes de almacenamiento y el tiempo de lectura de los componentes en las capas de procesamiento y consumo. Los conjuntos de datos suelen almacenarse en formatos columnares de código abierto, como Parquet y ORC, para reducir aún más la cantidad de datos leídos cuando los componentes de las capas de procesamiento y consumo consultan solo un subconjunto de columnas. Amazon S3 ofrece una gama de clases de almacenamiento diseñadas para diferentes casos de uso. La clase de almacenamiento de nivelación inteligente de Amazon S3 está diseñada para optimizar los costos moviendo automáticamente los datos al nivel de acceso más rentable, sin impacto en el desempeño ni sobrecarga operativa.

Amazon Redshift proporciona almacenamiento de almacén de datos a escala de petabytes para datos altamente estructurados que suelen modelarse en esquemas dimensionales o desnormalizados. En Amazon Redshift, los datos se almacenan en formato columnar altamente comprimido y de forma distribuida en un clúster de nodos de alto desempeño. Cada nodo proporciona hasta 64 TB de almacenamiento administrado de alto desempeño. Amazon Redshift permite una alta calidad y coherencia de los datos al aplicar el esquema en escritura, las transacciones ACID y el aislamiento de la carga de trabajo. Las organizaciones suelen almacenar en Amazon Redshift conjuntos de datos estructurados altamente conformados, armonizados, de confianza y gobernados para atender casos de uso que requieren un desempeño muy alto, una latencia muy baja y una alta concurrencia. También puede utilizar las vistas materializadas de actualización incremental en Amazon Redshift para aumentar significativamente el desempeño y el rendimiento de consultas complejas generadas por paneles de BI.

A medida que construye su Lake House mediante la ingesta de datos de diversas fuentes, normalmente puede comenzar a hospedar cientos o miles de conjuntos de datos en su lago de datos y almacén de datos. Un catálogo de datos central que proporcione metadatos para todos los conjuntos de datos almacenados en Lake House (tanto en el almacén de datos como en el lago de datos) en un único lugar y que facilite las búsquedas es crucial para el descubrimiento autoservicio de datos en Lake House. Además, separar los metadatos de los datos alojados en el lago de datos en un esquema central permite la lectura del esquema para los componentes de la capa de procesamiento y consumo, así como Redshift Spectrum.

En nuestra arquitectura de referencia de Lake House, Lake Formation proporciona el catálogo central para almacenar los metadatos de todos los conjuntos de datos alojados en Lake House (ya estén almacenados en Amazon S3 o Amazon Redshift). Las organizaciones almacenan tanto metadatos técnicos (como esquemas de tablas versionados, información de partición, ubicación física de los datos y marcas de tiempo de actualización) como atributos empresariales (como propietario de los datos, administrador de los datos, definición empresarial de la columna y sensibilidad de la información de la columna) de todos sus conjuntos de datos en Lake Formation.

Muchos conjuntos de datos alojados en lagos de datos suelen tener esquemas en constante evolución y cada vez más particiones de datos, mientras que los esquemas de los conjuntos de datos alojados en almacenes de datos evolucionan de forma regulada. Los rastreadores de AWS Glue rastrean los esquemas en evolución y las particiones recién añadidas de datos alojados en conjuntos de datos alojados en lagos de datos, así como en conjuntos de datos alojados en almacenes de datos, y añade nuevas versiones de los esquemas correspondientes en el catálogo de Lake Formation. Además, Lake Formation proporciona API para permitir el registro y la gestión de metadatos mediante scripts personalizados y productos de terceros.

Lake Formation proporciona al administrador del lago de datos un lugar central para configurar permisos granulares a nivel de tabla y columna para bases de datos y tablas alojadas en el lago de datos. Una vez configurados los permisos de Lake Formation, los usuarios y grupos solo pueden acceder a las tablas y columnas autorizadas utilizando varios servicios de la capa de procesamiento y consumo, como AWS Glue, Amazon EMR, Amazon Athena y Redshift Spectrum.

#### Capa de procesamiento de datos

La capa de procesamiento de nuestra arquitectura Lake House proporciona múltiples componentes creados específicamente para permitir una variedad de casos de uso de procesamiento de datos. Para que coincida con la estructura única (tabular plana, jerárquica o no estructurada) y la velocidad (por lotes o streaming) de un conjunto de datos en Lake House, podemos elegir un componente de procesamiento específico que coincida. Cada componente puede leer y escribir datos tanto en Amazon S3 como en Amazon Redshift (colectivamente, el almacenamiento de Lake House).

Podemos utilizar componentes de la capa de procesamiento para crear trabajos de procesamiento de datos que puedan leer y escribir datos almacenados tanto en el almacén de datos como en el almacenamiento del lago de datos mediante las siguientes interfaces:

- Amazon Redshift SQL (con Redshift Spectrum). Para obtener más información, consulte Amazon Redshift Spectrum Extends Data Warehousing Out to Exabytes-No Loading Required.
- Trabajos de Apache Spark que ejecutan Amazon EMR. Para obtener más información, consulte lo siguiente:
  - Entradas de documentación de Spark para DataFrameReader y DataFrameWriter.
  - Performant Redshift Data Source para Apache Spark - Community Edition en GitHub

- Trabajos de Apache Spark ejecutados en AWS Glue. Para obtener más información, consulte lo siguiente:
  - Clase DynamicFrameReader
  - Clase DynamicFrameWriter
  - Mover datos hacia y desde Amazon Redshift

Puede añadir metadatos de los conjuntos de datos resultantes al catálogo central de Lake Formation mediante rastreadores de AWS Glue o API de Lake Formation.

Puede utilizar componentes creados específicamente para crear canalizaciones de transformación de datos que implementen lo siguiente:

- ELT basado en SQL utilizando Amazon Redshift (con Redshift Spectrum)
- Procesamiento de big data con AWS Glue o Amazon EMR
- Procesamiento de datos de streaming casi en tiempo real con Amazon Kinesis. Para obtener más información, consulte lo siguiente:
  - Escritura de SQL en datos de streaming con Amazon Kinesis Analytics - Parte 1
  - Escritura de SQL en datos de streaming con Amazon Kinesis Analytics - Parte 2
  - Procesamiento basado en streaming sin servidor para obtener información en tiempo real
  - ETL de streaming con Apache Flink y Amazon Kinesis Data Analytics

- Procesamiento de datos de streaming casi en tiempo real con Spark streaming en AWS Glue. Para obtener más información, consulte Nuevo - ETL de streaming sin servidor con AWS Glue.
- Procesamiento de datos de streaming en tiempo casi real mediante streaming de Spark en Amazon EMR. Para obtener más información, consulte
  - Optimizar Spark-Streaming para procesar de forma eficiente Amazon Kinesis Streams.
  - Análisis en tiempo real con Spark Streaming
  - Consulta de Amazon Kinesis Streams directamente con SQL y Spark Streaming
  - Procesamiento de flujos en tiempo real con Apache Spark Streaming y Apache Kafka en AWS

#### ELT basado en SQL

Para transformar datos estructurados en la capa de almacenamiento de Lake House, puede crear potentes canalizaciones ELT utilizando la semántica SQL conocida. Estas canalizaciones de ELT pueden utilizar la capacidad de procesamiento paralelo masivo (MPP) de Amazon Redshift y la capacidad de Redshift Spectrum de activar miles de nodos transitorios para escalar el procesamiento a petabytes de datos. Las mismas canalizaciones ELT basadas en procedimientos almacenados en Amazon Redshift pueden transformar lo siguiente:

- Datos planos estructurados entregados por AWS DMS o Amazon AppFlow directamente en tablas de preparación de Amazon Redshift.
- Datos alojados en el lago de datos mediante formatos de archivo de código abierto como JSON, Avro, Parquet y ORC.

Para los pasos de enriquecimiento de datos, estas canalizaciones pueden incluir sentencias SQL que unan tablas de dimensiones internas con grandes tablas de hechos alojadas en el lago de datos de S3 (utilizando la capa Spectrum de Redshift). Como paso final, las canalizaciones de procesamiento de datos pueden insertar datos curados, enriquecidos y modelados en una tabla interna de Amazon Redshift o en una tabla externa almacenada en Amazon S3.

### Procesamiento de big data

Para el procesamiento integrado de grandes volúmenes de datos semiestructurados, no estructurados o altamente estructurados alojados en la capa de almacenamiento de Lake House (Amazon S3 y Amazon Redshift), puede crear trabajos de procesamiento de big data con Apache Spark y ejecutarlos en AWS Glue o Amazon EMR. Estos trabajos pueden utilizar conectores nativos de Spark y de código abierto para obtener acceso y combinar datos relacionales almacenados en Amazon Redshift con datos estructurados jerárquicos o planos complejos almacenados en Amazon S3. Estos mismos trabajos pueden volver a almacenar conjuntos de datos procesados en el lago de datos de S3, el almacén de datos de Amazon Redshift o ambos en la capa de almacenamiento Lake House.

AWS Glue proporciona capacidades ETL sin servidor, de pago por uso, para habilitar canalizaciones ETL que pueden procesar decenas de terabytes de datos, todo ello sin tener que montar y administrar servidores o clústeres. Para acelerar el desarrollo de ETL, AWS Glue genera automáticamente código ETL y proporciona estructuras de datos de uso común, así como transformaciones ETL (para validar, limpiar, transformar y aplanar datos). AWS Glue ofrece la capacidad integrada de procesar datos almacenados en Amazon Redshift y en un lago de datos de S3. En el mismo trabajo, AWS Glue puede cargar y procesar datos de Amazon Redshift almacenados en formato de tabla plana, así como conjuntos de datos alojados en un lago de datos de S3 almacenados en formatos comunes de código abierto, como CSV, JSON, Parquet y Avro. Los trabajos de AWS Glue ETL pueden hacer referencia a tablas alojadas en Amazon Redshift y Amazon S3 de manera unificada accediendo a ellas a través del catálogo común de formación de lagos (que los rastreadores de AWS Glue rellenan rastreando Amazon S3 y Amazon Redshift). AWS Glue ETL proporciona capacidades para procesar datos particionados de manera incremental. Además, AWS Glue proporciona desencadenadores y capacidades de flujo de trabajo que puede utilizar para crear canalizaciones de procesamiento de datos de extremo a extremo de varios pasos que incluyan dependencias de trabajo y ejecuten pasos paralelos.

Puede escalar automáticamente clústeres de EMR para satisfacer las demandas variables de recursos de canalizaciones de procesamiento de big data que pueden procesar hasta petabytes de datos. Estas canalizaciones pueden utilizar flotas de diferentes instancias puntuales de Amazon Elastic Compute Cloud (Amazon EC2) para escalar de forma altamente optimizada en cuanto a costes. Para obtener más información sobre las instancias, consulte Tipos de instancias compatibles.

Las canalizaciones de procesamiento de datos basadas en Spark que se ejecutan en Amazon EMR pueden utilizar lo siguiente:

- Los lectores y escritores incorporados de Spark para manejar conjuntos de datos alojados en lagos de datos en una variedad de formatos de código abierto.
- El conector de código abierto Spark-Amazon Redshift para leer y escribir directamente datos en el almacén de datos de Amazon Redshift.

Para leer el esquema de los conjuntos de datos estructurados complejos alojados en el lago de datos, los trabajos ETL de Spark en Amazon EMR pueden conectarse al catálogo Lake Formation. Esto se configura con la compatibilidad de AWS Glue y las políticas de AWS Identity and Access Management (IAM) configuradas para autorizar por separado el acceso a las tablas de AWS Glue y los objetos de S3 subyacentes. Los mismos trabajos de Spark pueden utilizar el conector Spark-Amazon Redshift para leer tanto los datos como los esquemas de los conjuntos de datos alojados en Amazon Redshift. Puede utilizar Spark y Apache Hudi para crear pipelines de procesamiento de datos incrementales de alto rendimiento Amazon EMR.

#### ETL casi en tiempo real

Para habilitar varios casos de uso de análisis modernos, necesita realizar las siguientes acciones, todas en tiempo casi real:

- Ingerir grandes volúmenes de datos de alta frecuencia o de streaming.
- Validarlos, limpiarlos y enriquecerlos
- Ponerlos a disposición para su consumo en el almacenamiento de Lake House

Puede crear canalizaciones que se puedan escalar fácilmente para procesar grandes volúmenes de datos en tiempo casi real mediante una de las siguientes opciones:

- Análisis de datos de Amazon Kinesis para SQL/Flink
- Spark streaming en AWS Glue o Amazon EMR
- Kinesis Data Firehose integrado con AWS Lambda

Kinesis Data Analytics, AWS Glue y Kinesis Data Firehose le permiten crear canalizaciones de procesamiento de datos casi en tiempo real sin tener que crear o administrar infraestructura informática. Las canalizaciones de Kinesis Data Firehose y Kinesis Data Analytics se escalan elásticamente para adaptarse al rendimiento de la fuente, mientras que los trabajos de streaming de Spark basados en Amazon EMR y AWS Glue se pueden escalar en cuestión de minutos con solo especificar los parámetros de escalado.

Las canalizaciones de streaming basadas en Kinesis Data Analytics for Flink/SQL suelen leer registros de Amazon Kinesis Data Streams (en la capa de ingestión de nuestra arquitectura Lake House), aplicarles transformaciones y escribir los datos procesados en Kinesis Data Firehose. Las canalizaciones de streaming de Spark suelen leer registros de Kinesis Data Streams (en la capa de ingestión de nuestra arquitectura Lake House), aplicarles transformaciones y escribir los datos procesados en otra transmisión de datos de Kinesis, que se encadena a una transmisión de entrega de Kinesis Data Firehose. El flujo de entrega Firehose puede entregar datos procesados a Amazon S3 o Amazon Redshift en la capa de almacenamiento de Lake House. Para crear canalizaciones en tiempo casi real más sencillas que requieran transformaciones simples y sin estado, puede ingerir datos directamente en Kinesis Data Firehose y transformar microlotes de registros entrantes mediante la función Lambda invocada por Kinesis Data Firehose. Kinesis Data Firehose entrega los microlotes de registros transformados a Amazon S3 o Amazon Redshift en la capa de almacenamiento Lake House.

Gracias a su capacidad para entregar datos a Amazon S3 y Amazon Redshift, Kinesis Data Firehose proporciona una interfaz unificada de escritor de almacenamiento de Lake House a canalizaciones ETL casi en tiempo real en la capa de procesamiento. En Amazon S3, Kinesis Data Firehose puede almacenar datos en archivos Parquet u ORC eficientes que se comprimen mediante códecs de código abierto como ZIP, GZIP y Snappy.

## Capa de consumo de datos

Nuestra arquitectura de referencia de Lake House democratiza el consumo de datos en diferentes tipos de personas al proporcionar servicios de AWS creados específicamente que permiten una variedad de casos de uso de análisis, como consultas SQL interactivas, BI y ML. Estos servicios utilizan interfaces unificadas de Lake House para obtener acceso a todos los datos y metadatos almacenados en Amazon S3, Amazon Redshift y el catálogo de Lake Formation. Pueden consumir datos relacionales planos almacenados en tablas de Amazon Redshift, así como datos planos o complejos estructurados o no estructurados almacenados en objetos de S3 utilizando formatos de archivo abiertos como JSON, Avro, Parquet y ORC.

### SQL interactivo

Para explorar todos los datos almacenados en Lake House mediante SQL interactivo, los analistas empresariales y los científicos de datos pueden utilizar Amazon Redshift (con Redshift Spectrum) o Athena. Puede ejecutar consultas SQL que unan datos de dimensiones planos, relacionales y estructurados, alojados en un clúster de Amazon Redshift, con terabytes de datos de hechos históricos planos o estructurados complejos en Amazon S3, almacenados mediante formatos de archivo abiertos como JSON, Avro, Parquet y ORC. Cuando se consulta un conjunto de datos en Amazon S3, tanto Athena como Redshift Spectrum obtienen el esquema almacenado en el catálogo de Lake Formation y lo aplican en la lectura (schema-on-read). Puede ejecutar consultas de Athena o Amazon Redshift en sus respectivas consolas o enviarlas a puntos finales JDBC u ODBC. Para obtener más información, consulte Conexión a Amazon Athena con controladores ODBC y JDBC y Configuración de conexiones en Amazon Redshift.

Athena puede ejecutar SQL ANSI complejo contra terabytes de datos almacenados en Amazon S3 sin necesidad de cargarlos primero en una base de datos. Athena no tiene servidor, por lo que no hay que configurar ni administrar ninguna infraestructura, y solo paga por la cantidad de datos analizados por las consultas que ejecuta. La capacidad de consulta federada de Athena permite realizar consultas SQL que pueden unir datos de hechos alojados en Amazon S3 con tablas de dimensiones alojadas en un clúster de Amazon Redshift, sin tener que mover datos en ambas direcciones. También puede incluir datos activos en bases de datos operativas en la misma sentencia SQL mediante consultas federadas de Athena. Athena proporciona resultados más rápidos y menores costos al reducir la cantidad de datos que escanea aprovechando la información de partición de conjuntos de datos almacenada en el catálogo de Lake Formation. Puede reducir aún más los costos almacenando los resultados de una consulta repetida mediante declaraciones Athena CTAS.

Amazon Redshift proporciona una potente capacidad SQL diseñada para el procesamiento analítico en línea (OLAP) ultrarrápido de conjuntos de datos muy grandes que se almacenan en Lake House (en el clúster MPP de Amazon Redshift y en el lago de datos S3). El potente optimizador de consultas de Amazon Redshift puede tomar consultas de usuario complejas escritas en sintaxis similar a PostgreSQL y generar planes de consultas de alto desempeño que se ejecutan en el clúster MPP de Amazon Redshift, así como en una flota de nodos Redshift Spectrum (para consultar datos en Amazon S3). Amazon Redshift proporciona capacidades de almacenamiento en caché de resultados para reducir el tiempo de ejecución de consultas para ejecuciones repetidas de la misma consulta en órdenes de magnitud. Con las vistas materializadas de Amazon Redshift, puede precomputar uniones complejas una vez (y actualizarlas de forma incremental) para simplificar y acelerar significativamente las consultas posteriores que los usuarios tienen que escribir. Amazon Redshift proporciona escalado de concurrencia, que pone en marcha clústeres transitorios adicionales en cuestión de segundos, para soportar un número prácticamente ilimitado de consultas concurrentes. Puede escribir los resultados de sus consultas en tablas nativas de Amazon Redshift o en tablas externas alojadas en el lago de datos de S3 (mediante Redshift Spectrum).

#### Aprendizaje automático

Por lo general, los científicos de datos necesitan explorar, gestionar y diseñar características de una variedad de conjuntos de datos estructurados y no estructurados para preparar el entrenamiento de modelos de ML. Las interfaces de Lake House (una interfaz SQL interactiva que utiliza Amazon Redshift con una interfaz de Athena y Spark) simplifican y aceleran significativamente estos pasos de preparación de datos al proporcionar a los científicos de datos lo siguiente:

- Un catálogo unificado de Lake Formation para buscar y descubrir todos los datos alojados en el almacenamiento de Lake House.
- Capacidad SQL interactiva basada en Amazon Redshift SQL y Athena para acceder, explorar y transformar todos los datos en el almacenamiento de Lake House
- Acceso unificado basado en Spark para gestionar y transformar todos los conjuntos de datos alojados en el almacenamiento de Lake House (estructurados y no estructurados) y convertirlos en conjuntos de características.

A continuación, los científicos de datos desarrollan, entrenan e implementan modelos ML conectando Amazon SageMaker a la capa de almacenamiento de Lake House y accediendo a los conjuntos de características de entrenamiento.

SageMaker es un servicio totalmente administrado que proporciona componentes para crear, entrenar e implementar modelos de ML mediante un entorno de desarrollo interactivo (IDE) llamado SageMaker Studio. En Studio, puede cargar datos, crear nuevos cuadernos, entrenar y ajustar modelos, avanzar y retroceder entre pasos para ajustar experimentos, comparar resultados e implementar modelos en producción, todo en un solo lugar mediante una interfaz visual unificada. Para obtener más información, consulte Amazon SageMaker Studio: El primer entorno de desarrollo totalmente integrado para el aprendizaje automático.

SageMaker también proporciona cuadernos Jupyter administrados que puede crear con unos pocos clics. Los cuadernos de SageMaker proporcionan recursos informáticos elásticos, integración con git, uso compartido sencillo, algoritmos de ML preconfigurados, docenas de ejemplos de ML listos para usar e integración con AWS Marketplace que permite una implementación sencilla de cientos de algoritmos preentrenados. Los cuadernos de SageMaker están preconfigurados con los principales marcos de aprendizaje profundo, incluidos TensorFlow, PyTorch, Apache MXNet, Chainer, Keras, Gluon, Horovod, Scikit-learn y Deep Graph Library.

Los modelos ML se entrenan en instancias de cómputo administradas por SageMaker, incluyendo instancias EC2 Spot altamente rentables. Puede organizar múltiples trabajos de entrenamiento usando SageMaker Experiments. Puede crear trabajos de capacitación con algoritmos integrados en SageMaker, algoritmos personalizados o cientos de algoritmos que puede implementar desde AWS Marketplace. SageMaker Debugger proporciona una visibilidad completa de los trabajos de entrenamiento de modelos. SageMaker también proporciona un ajuste automático de hiperparámetros para los trabajos de entrenamiento de ML.

Puede implementar modelos entrenados por SageMaker en producción con unos pocos clics y escalarlos fácilmente en una flota de instancias EC2 totalmente administradas. Puede elegir entre varios tipos de instancias EC2 y adjuntar una aceleración de inferencia rentable potenciada por GPU. Después de desplegar los modelos, SageMaker puede supervisar las métricas clave del modelo para la precisión de la inferencia y detectar cualquier desviación del concepto.

#### Inteligencia empresarial

Amazon QuickSight proporciona capacidad sin servidor para crear y publicar fácilmente paneles de BI interactivos enriquecidos. Los analistas empresariales pueden utilizar la interfaz SQL interactiva de Athena o Amazon Redshift para potenciar los paneles de QuickSight con datos en el almacenamiento de Lake House. Además, puede obtener datos conectando QuickSight directamente a bases de datos operativas como MS SQL, Postgres y aplicaciones SaaS como Salesforce, Square y ServiceNow. Para lograr un rendimiento ultrarrápido de los cuadros de mando, QuickSight proporciona un motor de cálculo y almacenamiento en caché en memoria denominado SPICE. SPICE replica automáticamente los datos para lograr una alta disponibilidad y permite que miles de usuarios realicen simultáneamente análisis rápidos e interactivos a la vez que protege su infraestructura de datos subyacente.

QuickSight enriquece los cuadros de mando y los visuales con perspectivas de ML generadas automáticamente y listas para usar, como la previsión, la detección de anomalías y los aspectos destacados narrativos. QuickSight se integra de forma nativa con SageMaker para permitir perspectivas adicionales basadas en modelos ML personalizados para sus cuadros de mando de BI. Puede acceder a los cuadros de mando QuickSight desde cualquier dispositivo utilizando una aplicación QuickSight o incrustar los cuadros de mando en aplicaciones web, portales y sitios web. QuickSight se amplía automáticamente a decenas de miles de usuarios y ofrece un rentable modelo de precios de pago por sesión.

## Conclusión

Una arquitectura Lake House, basada en una cartera de servicios específicos, le ayudará a obtener rápidamente información de todos sus datos para todos sus usuarios y le permitirá construir para el futuro, de modo que pueda añadir fácilmente nuevos enfoques y tecnologías analíticas a medida que estén disponibles.

En esta publicación, describimos varios servicios de AWS creados específicamente que puede utilizar para componer las cinco capas de una arquitectura Lake House. Hemos presentado varias opciones para demostrar la flexibilidad y las amplias capacidades que ofrece el servicio de AWS adecuado para cada tarea.
## Tratamiento de datos con Step Functions

El procesamiento de datos implica pasos discretos para la ingesta, el procesamiento, el almacenamiento de los datos transformados y el post-procesamiento, como la visualización o el análisis de los datos transformados. Puede utilizar funciones por pasos para organizar estos pasos y crear canales de procesamiento de datos escalables como parte de una aplicación empresarial más amplia.

Algunos ejemplos de Step Functions en el procesamiento de datos son:
* Orquestar rastreadores de AWS Glue en un bucket de Amazon S3 y ejecutar consultas de Amazon Athena en el conjunto de datos.
* Analizar rápidamente gigabytes de datos en Amazon S3 utilizando miles de flujos de trabajo concurrentes con el estado de mapa distribuido de Step Functions.
* Procese datos de streaming de Amazon Kinesis en tiempo real mediante flujos de trabajo Step Functions Express.

### Paralelización a gran escala con Mapa distribuido

En este módulo, el flujo de trabajo de Step Functions utiliza un estado de mapa en modo distribuido para procesar una lista de objetos de S3 en un bucket de S3. Step Functions itera sobre la lista de objetos y, a continuación, lanza miles de flujos de trabajo paralelos, que se ejecutan simultáneamente, para procesar los elementos.

El conjunto de datos utilizado en este módulo es un pequeño subconjunto de los más de 37 GB de NOAA Global Surface Summary of Day. El código de la aplicación en este ejemplo encuentra la estación meteorológica que tiene la temperatura media más alta del planeta cada mes. Este conjunto de datos es interesante por varias razones:

* Los datos están organizados por estación y día. Cada estación meteorológica tendrá un único registro con los promedios por día.

* Este ejemplo de flujo de trabajo Step Function encontrará la temperatura media más alta en todas las estaciones por mes. Es decir, responde a la pregunta "¿Qué lugar del planeta registró la temperatura media diaria más alta en un mes determinado?".

* Hay más de 558.000 archivos CSV en el conjunto de datos con más de 37 GB. El tamaño medio de los archivos CSV es de 66,5 KB. Para este módulo del taller examinaremos un pequeño subconjunto de datos.

* Los archivos CSV son relativamente fáciles de entender y analizar.

### Exploremos el conjunto de datos

Navega al bucket de S3 que comienza con el nombre SFW-Module-13-distributedmapworkshopdataset para ver un subconjunto de los datos fuente originales de la NOAA.

Los archivos CSV que copiamos en el bucket de S3 contienen datos meteorológicos diarios entre 1929 y 1937 para cada ciudad. El siguiente extracto muestra las columnas que nos interesan.

Archivo CSV para Lerwick, Reino Unido, en octubre de 1929:

<table><thead><tr><th>Station</th><th>Date</th><th>Name</th><th>Temp</th></tr></thead><tbody><tr><td><strong>3005099999</strong></td><td>1929-10-02</td><td>LERWICK, UK</td><td>49.5</td></tr><tr><td><strong>3005099999</strong></td><td>1929-10-03</td><td>LERWICK, UK</td><td>49.0</td></tr><tr><td><strong>3005099999</strong></td><td>1929-10-04</td><td>LERWICK, UK</td><td>45.7</td></tr></tbody></table>

Archivo CSV de Dyce, Reino Unido, en octubre de 1929:

<table><thead><tr><th>Station</th><th>Date</th><th>Name</th><th>Temp</th></tr></thead><tbody><tr><td><strong>3091099999</strong></td><td>1929-10-02</td><td>DYCE, UK</td><td>50.5</td></tr><tr><td><strong>3091099999</strong></td><td>1929-10-03</td><td>DYCE, UK</td><td>48.0</td></tr><tr><td><strong>3091099999</strong></td><td>1929-10-04</td><td>DYCE, UK</td><td>43.8</td></tr></tbody></table>

Si quisiéramos saber cuál es la ciudad con la temperatura media más alta durante octubre de 1929, recorreríamos cada línea de los archivos CSV de cada ciudad y compararíamos las medias de ese mes. Calcular las medias de grandes conjuntos de datos con gigabytes de datos de temperatura de muchas localidades llevaría horas en un proceso de un solo hilo. El nuevo estado de mapa distribuido puede lanzar hasta diez mil flujos de trabajo paralelos para iterar sobre millones de objetos como los archivos CSV de este módulo, registros o imágenes almacenadas en Amazon S3.

En el siguiente paso, construirá un flujo de trabajo con un estado de mapa distribuido para analizar el conjunto de datos.

### Creación del flujo de trabajo de análisis de datos

Ejecutar el comando `bash deploy.sh` en una terminal para crear el flujo de trabajo de Step Functions.

Hemos proporcionado código de procesamiento de datos en las siguientes funciones Lambda:

* **TemperaturesFunction**: Esta función Lambda es ejecutada por cada ejecución de flujo de trabajo hijo del estado Mapa Distribuido y calcula las temperaturas medias más altas por ubicación y ciudad para un subconjunto de los datos.

* **ReducerFunction**: Esta función Lambda comparará los resultados de cada ejecución de TemperaturesFunction. Por ejemplo, la ejecución de flujo de trabajo hijo 1 puede encontrar que Los Ángeles, California, EE.UU. tuvo la temperatura más alta en "1931-07" (julio de 1931) mientras que la ejecución de flujo de trabajo hijo 2 encuentra que El Cairo, Egipto tuvo la temperatura más alta en "1931-07". La función reductora realizará una última pasada por las salidas de todos los flujos de trabajo secundarios para encontrar la temperatura más alta correcta para todo el conjunto de datos.

### Creating the Workflow

1. Navigate to Step Functions  in your AWS console. Make sure you are in the correct region.

2. If you are not on the State machines page, click on State machines on the left side menu and click Create state machine

3. For Choose authoring method select Design your workflow visually, select state machine Type as Standard and click on Next.

4. Click on the patterns tab and drag Process S3 objects onto the Workflow Studio canvas.

5. Configure the Distributed Map state with the following values:


<table><thead><tr><th>Setting</th><th>Value</th><th>Notes</th></tr></thead><tbody><tr><td><strong>Processing mode</strong></td><td>Distributed</td><td>Map State in distributed mode runs child workflow executions for each map iteration to achieve up to 10K concurrent workflows</td></tr><tr><td><strong>Item source</strong></td><td>Amazon S3</td><td></td></tr><tr><td><strong>S3 item source</strong></td><td>S3 object list</td><td>Since we have multiple CSV files we want to analyze, we'll use this item source as it uses S3 ListObjects to get a list a paginated list of objects in the bucket.</td></tr><tr><td><strong>S3 bucket</strong></td><td>Use the <em>distributedmapworkshopdataset</em> bucket.</td><td>You can find the S3 bucket name in the CloudFormation stack resources tab for this module or use the <em>Browse S3 or enter S3 URI option</em> and look for <em>distributedmapworkshopdataset</em> with the Browse S3 button.</td></tr><tr><td><strong>Enable batching</strong></td><td>Check this box</td><td></td></tr><tr><td><strong>Max items per batch</strong></td><td>500</td><td>Define the number of items to be processed by each child workflow execution</td></tr><tr><td><strong>Set concurrency limit</strong></td><td>500</td><td>The Lambda burst concurrency limit> varies by region. You can modify this concurrency setting based on the capacity of your downstream systems.</td></tr><tr><td><strong>Child execution type</strong></td><td>Express</td><td>Given each of these child workflow executions only take a few seconds to run, we can use Express workflows.</td></tr><tr><td><strong>Set a tolerated failure threshold</strong></td><td>Expand <strong>Additional configuration</strong> to see this setting. Check this box</td><td></td></tr><tr><td><strong>Tolerated failure threshold</strong></td><td>5%</td><td>Use this setting to consider a job <em>failed</em> if a minimum threshold of child workflow executions failed. This is useful if you have inconsistencies in your dataset.</td></tr><tr><td><strong>Use state name as label in Map Run ARN</strong></td><td>Check this box</td><td></td></tr><tr><td><strong>Export Map state results to Amazon S3</strong></td><td>Check this box</td><td></td></tr><tr><td><strong>S3 Bucket</strong></td><td>Use the <em>distributedmapresultsbucket</em> bucket.</td><td>Use <em>Browse S3 or enter S3 URI option</em>. You can find the S3 bucket name in the CloudFormation stack resources tab for this module or look for the <em>distributedmapresults</em> bucket with the Browse S3 button.</td></tr><tr><td><strong>Prefix</strong></td><td>results</td><td>Append the "results" prefix at the end of the S3 URI i.e. s3://<em>distributedmapresults</em> bucket/results</td></tr></tbody></table>

6.  Select the Lambda Invoke state within the Distributed Map state.
    * Function name: TemperaturesFunction
    * Payload: Use state input as payload

7. Drag another AWS Lambda Invoke task state onto the canvas below the Distributed Map state.

8. Configure the Lambda Invoke state with the following values:
    * Function name: ReducerFunction
    * Payload: Use state input as payload

9. For the Execution role, choose an existing role: TemperatureStateMachineRole
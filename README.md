# Mi primer proyecto

Soy Ana y estoy aprendiendo a usar GitHub.

## Mi objetivo

Quiero organizar mis trabajos de Big Data con github.

## Mi primer avance

Hoy creé un repositorio y guardé mi primer commit.


Consigna:

## (1) Tres observaciones sobre CSV/JSON, Parquet y Delta

1. **CSV y JSON no definen los tipos de datos de la misma manera que Parquet.** En este caso, al leer los archivos CSV sin inferencia, las columnas se interpretan como `string`; por ejemplo, `amount` queda como texto. Incluso usando `inferSchema=true`, `amount` sigue siendo `string` porque contiene valores como `N/A`, que impiden interpretarlo completamente como número. En cambio, Parquet conserva el esquema físico y en `products` se observa que `price` es `decimal(12,2)` y `product_id` es `long`.

2. **Inferir el esquema implica trabajo adicional y puede producir resultados dependientes de los datos.** Al utilizar `inferSchema=true`, Spark debe inspeccionar los datos para determinar los tipos. En este caso pudo inferir `transaction_id`, `customer_id` y `product_id` como `integer`, `event_ts` como `timestamp` e `is_fraud` como `integer`, pero `amount` continuó siendo `string` debido a la presencia de valores no numéricos. Por eso, la inferencia no reemplaza la validación de los datos.

3. **Delta agrega capacidades de gestión sobre el almacenamiento Parquet.** Las tablas Bronze se materializan como tablas Delta y permiten consultar metadatos, historial de operaciones y el plan de ejecución. En `DESCRIBE HISTORY` se observa la operación realizada sobre la tabla y en `EXPLAIN FORMATTED` se observa que la consulta utiliza archivos Parquet. Delta agrega una capa de administración y trazabilidad sobre esos archivos, facilitando el manejo de las tablas.

## (2) Volumen, velocidad, variedad, veracidad y valor

- **Volumen:** se observa en la cantidad de registros que deben procesarse. Las cuatro fuentes contienen 5.000 clientes, 500 productos, 50.011 transacciones y 200.000 eventos, superando en conjunto los 255.000 registros.

- **Velocidad:** representa la rapidez con la que los datos son generados, recibidos y procesados. En esta práctica los datos son generados y luego ingeridos, por lo que no se está trabajando con un flujo en tiempo real. Sin embargo, el proceso permite observar la necesidad de ingerir y procesar datos de distintas fuentes de forma eficiente.

- **Variedad:** aparece en los diferentes formatos utilizados: CSV, JSON y Parquet. También se observa variedad en las estructuras, ya que por ejemplo `events` contiene el campo anidado `context`, mientras que `products` utiliza tipos como `long` y `decimal(12,2)`.

- **Veracidad:** se evidencia en los problemas de calidad encontrados en los datos. Hay 50.011 filas de transacciones pero solo 50.000 `transaction_id` distintos, lo que indica que existen identificadores duplicados. Además, se detectaron 52 importes que no pueden convertirse a `DECIMAL(12,2)`, debido a valores como `N/A`. Estos problemas se identifican en Bronze, pero no se corrigen todavía porque la limpieza corresponde a la capa Silver.

- **Valor:** aparece en la posibilidad de transformar los datos provenientes de distintas fuentes en información útil para el análisis. La arquitectura permite conservar los datos originales en Bronze, registrar su procedencia y detectar problemas de calidad antes de corregirlos en Silver. De esta forma, los datos pueden convertirse posteriormente en información confiable para el análisis.


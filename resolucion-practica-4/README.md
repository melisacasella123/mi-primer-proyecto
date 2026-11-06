Entrega práctica 4 — Streaming

    Nombre: Melisa Casella
    student_id: melisa_casella
    Escala: small

Respondé cada pregunta en una a tres oraciones. Cuando se pide un dato, copiá el valor que te dio el notebook.
Log y offsets

1. Después de leer tres mensajes, quedaron 2 mensajes en la cola (pago_4 y pago_5). En cambio, el log conservó los 5 mensajes, aunque ya se habían leído tres. La diferencia es que una cola tradicional elimina los mensajes al consumirlos, mientras que un log conserva los mensajes y permite que distintos consumidores los lean independientemente.

2. Después de la llegada 2, el consumidor antifraude había leído 180 mensajes en total, mientras que el consumidor de reportes todavía no había leído ninguno. El atraso de reportes no afectó a antifraude porque cada consumidor tiene su propio offset y avanza de manera independiente.

3. Un offset es la posición que indica hasta qué mensaje leyó un consumidor dentro del log. En esta práctica, cada consumidor guarda su offset en su propio checkpoint, lo que permite continuar desde donde quedó sin volver a procesar los mensajes anteriores.

4. El replay leyó 280 mensajes, que corresponden a todos los mensajes almacenados en el topic. La arquitectura Kappa propone reprocesar los datos históricos utilizando el mismo flujo de procesamiento de streaming, desde el inicio del log. En cambio, Lambda utiliza dos caminos diferentes: uno para procesamiento batch y otro para streaming.
Ingesta y enriquecimiento

5. Bronze procesó 60 filas en stream_001, 120 en stream_002, 40 en stream_003, 40 en stream_004 y 20 en stream_005. Al reejecutar sin archivos nuevos procesó 0 filas. Auto Loader utiliza su checkpoint para registrar los archivos procesados y evitar leerlos nuevamente.

6. En la llegada stream_002 aparecieron dos motivos de rechazo: INVALID_AMOUNT, con 20 registros, y UNKNOWN_CUSTOMER, también con 20 registros. Bronze conserva los datos originales para no perder información y permitir auditorías, correcciones y reprocesamientos posteriores.

7. El enriquecimiento permite incorporar información de clientes y productos, como el país del cliente y la categoría del producto. Según la teoría, es un join stream-tabla porque se combinan eventos que llegan en streaming con tablas Delta existentes (silver_customers y silver_products).
Tiempo y ventanas

8. El event time es el momento en que ocurrió el evento, mientras que el processing time es el momento en que el sistema lo recibe y procesa. Por ejemplo, late_ok ocurrió a las 12:03, pero llegó en stream_002, cuando el sistema ya estaba procesando eventos posteriores.

9. El watermark se calcula restando 10 minutos al máximo event time observado hasta ese momento.

stream_001: 11:54.

stream_002: 11:58.

stream_003: 12:16.

stream_004: 12:17.

stream_005: 12:35.

10. Las primeras ventanas tumbling aparecieron en la llegada 3, cuando el watermark avanzó hasta las 12:16 y permitió cerrar ventanas anteriores. No aparecieron antes porque el sistema todavía esperaba posibles eventos tardíos que pertenecieran a esas ventanas.

11. late_ok, con event time 12:03, fue aceptado porque llegó cuando el watermark todavía era 11:58. En cambio, late_bad, con event time 12:02, llegó cuando el watermark ya estaba en 12:16, por lo que era demasiado antiguo y fue descartado. En la llegada 4 se registraron 20 eventos más viejos que el watermark.

12. Tumbling: son ventanas fijas que no se superponen. Ejemplo: calcular las ventas cada cinco minutos.

Hopping: son ventanas de duración fija que se superponen porque avanzan mediante saltos más pequeños. Ejemplo: analizar las ventas de los últimos diez minutos, actualizando el resultado cada cinco minutos.

Session: agrupan eventos de un mismo usuario mientras no exista una pausa superior al tiempo establecido. Ejemplo: agrupar las compras de un cliente durante una sesión de navegación.

13. En modo update se emitió dos veces: primero con 40 compras y un monto de 6.000, y después con 60 compras y un monto de 8.400. En modo append se emitió una sola vez, con 60 compras y un monto de 8.400, cuando la ventana quedó cerrada.

Update permite consultar resultados parciales más rápidamente, pero puede emitir varias actualizaciones de una misma ventana. Append evita esas actualizaciones y entrega resultados definitivos, aunque hay que esperar a que cierre la ventana.

14. Con un watermark de un minuto se ganarían resultados más rápidos y menor tiempo de espera para cerrar las ventanas. Sin embargo, se perdería tolerancia a eventos tardíos, por lo que aumentarían las posibilidades de descartar eventos que llegan con retraso.
Garantías y fallas

15. Sin deduplicar quedaron 220 filas, mientras que al deduplicar por event_id quedaron 200 filas únicas. El productor puede enviar el mismo evento más de una vez por reintentos ante errores de conexión, falta de confirmación o problemas durante la entrega.

16. Al reiniciar utilizando el mismo checkpoint, el destino continuó teniendo 200 filas, sin generar duplicados, porque el sistema recordó qué datos ya había procesado. En cambio, al perder el checkpoint y volver a utilizar append, el destino llegó a 400 filas porque se procesaron nuevamente los eventos. Con el mismo checkpoint se observa un comportamiento de procesamiento exactly-once en esta práctica, mientras que al perderlo y usar append pueden aparecer duplicados, comportamiento asociado a at-least-once.

17. Con MERGE el resultado se mantuvo en 200 filas incluso después de perder el checkpoint, porque se utilizó event_id para identificar los registros existentes y evitar insertarlos nuevamente. Una escritura es idempotente cuando ejecutarla varias veces produce el mismo resultado que ejecutarla una sola vez.
CDC

18. El log generó 13 eventos: 6 INSERT, 3 UPDATE_PREIMAGE, 3 UPDATE_POSTIMAGE y 1 DELETE. Un UPDATE genera dos eventos porque registra tanto el estado anterior del registro (preimage) como el nuevo estado (postimage), permitiendo conocer exactamente qué cambió.

19. Sí, se pudo reconstruir la tabla correctamente y el resultado coincidió con la tabla final original. El log conserva el historial de cambios, incluyendo inserciones, modificaciones, eliminaciones, versiones y marcas de tiempo. La tabla actual solamente muestra el estado final, mientras que el log permite conocer cómo se llegó a ese estado.
Cierre

20. Elegiría Spark Structured Streaming para procesar grandes volúmenes de datos e integrarlos con procesos batch y tablas Delta, aprovechando su integración con Databricks. Flink lo elegiría para aplicaciones que necesitan procesamiento en tiempo real con baja latencia y un control avanzado del event time y las ventanas. Kafka Streams lo utilizaría para desarrollar aplicaciones de streaming directamente sobre Kafka, ya que es liviano y se integra fácilmente con ese ecosistema.

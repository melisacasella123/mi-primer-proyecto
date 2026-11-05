Entrega práctica 3 — Bases de datos NoSQL

    Nombre: Melisa Casella
    student_id: melisa_casella
    Escala: small

1. En modo CP, la réplica C respondió ERROR: no disponible al intentar leer y ERROR: sin quórum al intentar escribir. En cambio, en modo AP devolvió el saldo desactualizado de 100 y permitió escribir un nuevo saldo de 50. El modo CP prioriza la consistencia y sacrifica la disponibilidad, mientras que el modo AP prioriza la disponibilidad y sacrifica la consistencia.

2. Después de la reparación, las tres réplicas quedaron con un saldo de 50. Se perdió la escritura anterior de saldo=80 realizada desde A, porque se aplicó la política last-write-wins y prevaleció el valor 50.

3. Con W=1, la p99 es de 9,6 ms, mientras que con W=3 es de 55,6 ms. Al esperar más réplicas se obtiene mayor consistencia y seguridad de que la escritura haya sido replicada, pero aumenta la latencia.

4. El lado ABC pudo seguir escribiendo porque cuenta con 3 de las 5 réplicas y alcanza el quórum de mayoría necesario. En cambio, el lado DE no pudo escribir porque solamente tiene 2 réplicas y no alcanza el quórum requerido.
Clave-valor

5. El GET en memoria tardó 0,0002 ms, mientras que el GET con Spark sobre Delta tardó 495 ms. Por lo tanto, el acceso en memoria fue aproximadamente 2.069.525 veces más rápido. Redis guarda los datos en memoria RAM para permitir accesos muy rápidos y reducir la latencia.

6. Para contar los clientes de AR hubo que leer y parsear los 5.000 valores porque el modelo clave-valor permite buscar directamente por clave, pero no indexa automáticamente los atributos internos de los valores. Se encontraron 992 clientes de AR. Una ventaja es la rapidez de búsqueda por clave y una desventaja es que las consultas por atributos requieren recorrer todos los valores.

7. Al pasar de 4 a 5 nodos, con hash mod N se movió el 79,6 % de las claves, mientras que con hashing consistente y 100 nodos virtuales se movió solamente el 21,2 %. Conviene el hashing consistente porque reduce la cantidad de claves que deben reasignarse cuando se agrega o elimina un nodo, evitando movimientos innecesarios de datos.
Documental

8. La consulta relacional devolvió 11 filas, utilizando 3 tablas y 2 joins. En cambio, la consulta documental devolvió 1 solo documento, sin necesidad de joins. Dentro del documento quedaron embebidos los datos del perfil del cliente, sus estadísticas y sus 11 transacciones, incluyendo información de los productos asociados a cada compra.

9. Spark unificó los distintos esquemas y asignó valores null a los campos que faltaban en algunos documentos. Se dice que el modelo documental tiene esquema flexible porque permite almacenar documentos con diferentes estructuras y campos, sin exigir que todos tengan exactamente los mismos atributos.

10. El documento más grande pesa 5,2 KB, aproximadamente 225 bytes por transacción. Si un documento crece sin límite, puede volverse demasiado grande y costoso de leer y actualizar. Según la estimación del notebook, alcanzaría los 16 MB con aproximadamente 74.599 transacciones.

11. El modelo documental resuelve bien las consultas centradas en un cliente, porque permite recuperar su perfil, estadísticas y transacciones en un solo documento, sin realizar joins. En cambio, las consultas que necesitan analizar o agrupar información de muchos documentos, como calcular montos por categoría, son más costosas porque requieren utilizar explode para separar los elementos de los arrays y luego realizar agregaciones.
Grafos

12. El grafo tiene 5.000 nodos Customer, 2.361 nodos Device y aproximadamente 5.300 aristas USES (calculado a partir de las distribuciones de clientes-por-dispositivo y dispositivos-por-cliente que muestra el notebook).

13. SQL necesitó 3 joins para el patrón de 2 saltos y 5 joins para el de 4 saltos. Neo4j es más eficiente porque almacena las relaciones de forma nativa (index-free adjacency / punteros directos entre nodos). No tiene que hacer joins de tablas en cada salto; simplemente sigue los enlaces. En una base relacional cada salto exige un join adicional, lo que se vuelve muy costoso a medida que crece el patrón.

14. La propagación de etiquetas convergió en 14 iteraciones (en la iteración 14 ya no cambió ningún nodo). El componente más grande tiene 23 nodos (y 22 aristas).

15. Al repartir con hash(id) mod 4 se cortaron el 74,4 % de las aristas (quedaron entre máquinas distintas). Con el particionamiento por componente el corte fue 0 %. Es difícil distribuir un grafo porque las conexiones son irregulares y densas localmente. Cualquier partición por hash simple corta muchísimas aristas, lo que genera mucho tráfico de red en cada recorrido. Encontrar una buena partición (mínimo corte) es un problema NP-difícil y, además, los componentes de distinto tamaño hacen que la carga entre máquinas quede desbalanceada.
Vectorial

16. Cada vector de 10 dimensiones representa el comportamiento de compra del cliente: proporciones de gasto en categorías (electronics, home, books, sports, fashion), canales de pago (card, wallet, transfer), monto promedio (avg_amount) y proporción de tickets altos (high_ticket_share). La similitud coseno mide cuán parecidos son dos vectores (ángulo entre ellos); valores cercanos a 1 indican clientes con patrones de comportamiento muy similares.

17. Entre los 10 vecinos más parecidos de clientes marcados hay un 31,6 % de marcados, mientras que la tasa base es del 14,8 % (y solo 13,2 % entre vecinos de no marcados). Buscar vecinos parecidos sirve para detectar clientes de riesgo o con comportamiento anómalo de forma no supervisada: si alguien se parece mucho a clientes ya marcados, es más probable que también lo sea (útil para fraude, churn, etc.).

18. En la curva del índice IVF, ¿qué recall y qué porcentaje de vectores escaneados se obtienen con nprobe=4? ¿Qué se gana y qué se pierde con la búsqueda aproximada (ANN)? Con nprobe=4 se obtiene un recall@10 de 0,872 (87,2 %) escaneando solo el ≈6 % de los vectores (5,985 %). Con la búsqueda aproximada (ANN / IVF) se gana mucho en velocidad y escala (se comparan muchos menos vectores), pero se pierde un poco de exactitud (puede no recuperar exactamente los mismos 10 vecinos más cercanos que la búsqueda exacta).
Columnar

19. Los 503.490 registros ocupan: CSV: 50,0 MB
JSON: 121,1 MB
Parquet: 5,3 MB

(Parquet es ~9,4× más pequeño que CSV y ~22,8× más pequeño que JSON). Para la consulta avg(amount) WHERE amount > 1900 sobre Parquet, Spark solo leyó la columna amount (ReadSchema: structamount:decimal(12,2)). Con los datos ordenados por amount se pueden saltear 7 de 8 archivos (data skipping gracias a los estadísticas min/max de cada archivo).

20. Es excelente para analítica porque: solo se leen las columnas necesarias (column pruning),
los valores similares se comprimen mucho mejor,
se pueden saltar archivos enteros con las estadísticas (data skipping).

Es poco conveniente para modificar una sola fila porque los datos de cada columna están agrupados en bloques/archivos; actualizar una fila obliga a reescribir grandes trozos de varias columnas en lugar de cambiar solo unos pocos bytes.


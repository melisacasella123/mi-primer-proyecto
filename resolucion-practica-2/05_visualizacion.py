# Databricks notebook source
# MAGIC %md
# MAGIC # 5 — Visualización orientada a preguntas
# MAGIC
# MAGIC Un gráfico no es el objetivo: es evidencia para responder una pregunta. En cada ejercicio primero escribí qué querés averiguar, luego construí la agregación y finalmente redactá una conclusión de dos o tres oraciones.
# MAGIC
# MAGIC Este notebook se ejecuta manualmente **después** de que el Job termina correctamente; no forma parte del pipeline.

# COMMAND ----------

dbutils.widgets.text("student_id", "melisa_casella", "01 - Identificador")
dbutils.widgets.dropdown("scale", "small", ["test", "small", "demo"], "02 - Escala")

# COMMAND ----------

# MAGIC %run ../common/config

# COMMAND ----------

from pyspark.sql import functions as F
import matplotlib.pyplot as plt

catalog = spark.sql("SELECT current_catalog()").first()[0]
config = CourseConfig(catalog, dbutils.widgets.get("student_id"), dbutils.widgets.get("scale"))
daily = qualified_table(config, "gold_daily_sales")
risk = qualified_table(config, "gold_customer_risk")
batch = qualified_table(config, "gold_batch_summary")
for table in [daily, risk, batch]:
    assert spark.catalog.tableExists(table), f"Falta {table}. Ejecutá primero el Job completo."

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ejemplo resuelto
# MAGIC
# MAGIC **Pregunta:** ¿Qué categoría concentra el mayor monto vendido?
# MAGIC
# MAGIC La agregación se hace con Spark. Sólo el resultado pequeño se convierte a Pandas para dibujarlo. Un gráfico de barras ordenado permite comparar categorías; un gráfico de torta haría más difícil comparar valores cercanos.

# COMMAND ----------

category_sales = (spark.table(daily)
    .groupBy("category")
    .agg(F.sum("total_amount").alias("total_amount"))
    .orderBy(F.desc("total_amount")))

plot_data = category_sales.toPandas().sort_values("total_amount")
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.barh(plot_data["category"], plot_data["total_amount"], color="#2563eb")
ax.set_title("Monto vendido por categoría")
ax.set_xlabel("Monto total")
ax.set_ylabel("Categoría")
ax.grid(axis="x", alpha=0.25)
fig.tight_layout()
plt.show()

leader = category_sales.first()
print(f"Respuesta: {leader.category} es la categoría con mayor monto vendido ({leader.total_amount:,.2f}).")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consigna 1 — Evolución temporal
# MAGIC
# MAGIC **Pregunta:** ¿Qué día tuvo el mayor monto vendido y ese día también fue el de mayor cantidad de transacciones?
# MAGIC
# MAGIC Construí una visualización temporal que permita comparar ambas métricas sin ocultar sus unidades. Explicá si los dos máximos coinciden y qué implica que coincidan —o no— sobre el ticket promedio. Fuente sugerida: `gold_daily_sales`.
# MAGIC
# MAGIC Respuesta: El 1 de marzo de 2026 se registraron tanto el mayor monto vendido, de 7.310.840,77 unidades monetarias, como la mayor cantidad de transacciones, con 7.236 operaciones. Por lo tanto, ambos máximos coinciden y el ticket promedio de ese día fue de 1.010,34 unidades monetarias por transacción. Esto indica que ese día lideró tanto en facturación como en volumen de operaciones, aunque la coincidencia de los máximos no implica necesariamente que haya tenido el ticket promedio más alto de todo el período.

# COMMAND ----------

from pyspark.sql import functions as F
import matplotlib.pyplot as plt
import pandas as pd

# Agregar los datos por fecha usando Spark
daily_totals = (
    spark.table(daily)
    .groupBy("sale_date")
    .agg(
        F.sum("total_amount").alias("total_amount"),
        F.sum("transaction_count").alias("transactions")
    )
    .orderBy("sale_date")
)

# Convertir sólo el resultado agregado a Pandas
pdf = daily_totals.toPandas()
pdf["sale_date"] = pd.to_datetime(pdf["sale_date"])
pdf = pdf.sort_values("sale_date")

# Identificar los días con los valores máximos
max_amount = pdf.loc[pdf["total_amount"].idxmax()]
max_transactions = pdf.loc[pdf["transactions"].idxmax()]

# Crear gráfico temporal con dos ejes para respetar las unidades
fig, ax1 = plt.subplots(figsize=(12, 5))

ax1.plot(
    pdf["sale_date"],
    pdf["total_amount"],
    color="blue",
    marker="o",
    markersize=3,
    label="Monto vendido"
)
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Monto vendido (unidades monetarias)", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")
ax1.grid(axis="y", alpha=0.25)

ax2 = ax1.twinx()
ax2.plot(
    pdf["sale_date"],
    pdf["transactions"],
    color="darkorange",
    marker="s",
    markersize=3,
    label="Cantidad de transacciones"
)
ax2.set_ylabel("Cantidad de transacciones", color="darkorange")
ax2.tick_params(axis="y", labelcolor="darkorange")

ax1.set_title("Evolución diaria del monto vendido y las transacciones")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

fig.autofmt_xdate()
fig.tight_layout()
plt.show()

# Calcular los tickets promedio de ambos días
ticket_max_amount = (
    max_amount["total_amount"] / max_amount["transactions"]
)
ticket_max_transactions = (
    max_transactions["total_amount"] / max_transactions["transactions"]
)

same_day = max_amount["sale_date"] == max_transactions["sale_date"]

print("Día con mayor monto vendido:",
      max_amount["sale_date"].strftime("%Y-%m-%d"))
print(f"Monto máximo: {max_amount['total_amount']:,.2f}")

print("Día con mayor cantidad de transacciones:",
      max_transactions["sale_date"].strftime("%Y-%m-%d"))
print(f"Transacciones máximas: {int(max_transactions['transactions'])}")

print("¿Coinciden ambos máximos?:", same_day)
print(f"Ticket promedio del día de mayor monto: {ticket_max_amount:,.2f}")
print(
    "Ticket promedio del día de más transacciones: "
    f"{ticket_max_transactions:,.2f}"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consigna 2 — Canal y fraude
# MAGIC
# MAGIC **Pregunta:** ¿Qué canal de pago presenta la mayor tasa de fraude? ¿La conclusión se sostiene al considerar el número de transacciones de cada canal?
# MAGIC
# MAGIC Mostrá tasa y volumen de manera legible. No compares sólo cantidades de fraude: calculá el denominador correcto. Fuente sugerida: `gold_daily_sales`.
# MAGIC
# MAGIC Respuesta:
# MAGIC El canal de pago transfer presenta la mayor tasa de fraude, con un 13,92 % (2.318 fraudes sobre 16.657 transacciones), seguido de wallet con un 12,97 % y card con un 12,53 %. Al considerar el volumen, transfer también registra más fraudes que los otros canales, mientras que card tiene una cantidad ligeramente mayor de transacciones. Por lo tanto, transfer presenta tanto la mayor proporción como la mayor cantidad absoluta de fraudes.
# MAGIC
# MAGIC

# COMMAND ----------

channel_data = (
    spark.table(daily)
    .groupBy("payment_channel")
    .agg(
        F.sum("fraud_transactions").alias("frauds"),
        F.sum("transaction_count").alias("transactions")
    )
    .withColumn(
        "fraud_rate",
        F.col("frauds") / F.col("transactions") * 100
    )
    .orderBy(F.desc("fraud_rate"))
)

plot_data = channel_data.toPandas()

fig, ax1 = plt.subplots(figsize=(9, 4))

ax1.bar(
    plot_data["payment_channel"],
    plot_data["fraud_rate"],
    color="orange",
    label="Tasa de fraude"
)
ax1.set_xlabel("Canal de pago")
ax1.set_ylabel("Tasa de fraude (%)", color="orange")
ax1.tick_params(axis="y", labelcolor="orange")

ax2 = ax1.twinx()
ax2.plot(
    plot_data["payment_channel"],
    plot_data["transactions"],
    color="blue",
    marker="o",
    label="Transacciones"
)
ax2.set_ylabel("Cantidad de transacciones", color="blue")
ax2.tick_params(axis="y", labelcolor="blue")

ax1.set_title("Tasa de fraude y volumen por canal de pago")
fig.tight_layout()
plt.show()

print("Resultados por canal:")
display(channel_data)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consigna 3 — Concentración geográfica y de producto
# MAGIC
# MAGIC **Pregunta:** ¿Qué combinación de país y categoría genera el mayor monto? ¿Existe una categoría dominante en todos los países o cambia según el mercado?
# MAGIC
# MAGIC Elegí una visualización que permita comparar simultáneamente países y categorías. Justificá brevemente por qué ese tipo de gráfico es adecuado. Fuente sugerida: `gold_daily_sales`.
# MAGIC
# MAGIC Respuesta:
# MAGIC La combinación de país y categoría que generó el mayor monto vendido fue BR (Brasil) en la categoría home, con 2.354.763,25 unidades monetarias. La categoría dominante cambia según el mercado: books lidera en AR y MX, mientras que home lidera en BR, CL y UY. Elegí un mapa de calor porque permite comparar visualmente los montos de cada combinación de país y categoría e identificar fácilmente dónde se concentran las mayores ventas.
# MAGIC
# MAGIC

# COMMAND ----------

country_category = (
    spark.table(daily)
    .groupBy("country", "category")
    .agg(
        F.sum("total_amount").alias("total_amount")
    )
    .orderBy(F.desc("total_amount"))
)

plot_data = country_category.toPandas()

# Asegurar que los montos sean numéricos
plot_data["total_amount"] = pd.to_numeric(
    plot_data["total_amount"], errors="coerce"
)

plot_data = plot_data.dropna(subset=["total_amount"])

# Preparar los datos para el mapa de calor
heatmap_data = plot_data.pivot(
    index="country",
    columns="category",
    values="total_amount"
).fillna(0)

# Convertir la matriz a números
heatmap_data = heatmap_data.astype(float)

# Encontrar la combinación con mayor monto
top_combo = plot_data.loc[plot_data["total_amount"].idxmax()]

# Encontrar la categoría líder de cada país
leaders = plot_data.loc[
    plot_data.groupby("country")["total_amount"].idxmax()
].sort_values("country")

# Crear el mapa de calor
fig, ax = plt.subplots(figsize=(9, 4))

im = ax.imshow(
    heatmap_data.to_numpy(),
    cmap="Blues",
    aspect="auto"
)

for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        value = heatmap_data.iloc[i, j]

        ax.text(
            j, i,
            f"{value:,.0f}",
            ha="center",
            va="center",
            color="black" if value < heatmap_data.to_numpy().max() * 0.65 else "white",
            fontsize=8
        )

ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels(heatmap_data.columns, rotation=30, ha="right")

ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index)

ax.set_xlabel("Categoría")
ax.set_ylabel("País")
ax.set_title("Monto vendido por país y categoría")

fig.colorbar(im, ax=ax, label="Monto total vendido")
fig.tight_layout()
plt.show()

print(
    f"Mayor monto: país {top_combo['country']}, "
    f"categoría {top_combo['category']}, "
    f"total {top_combo['total_amount']:,.2f}"
)

print("Categoría con mayor monto en cada país:")
display(leaders)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consigna 4 — Calidad del pipeline
# MAGIC
# MAGIC **Pregunta:** ¿Qué proporción de cada lote fue aceptada y rechazada? ¿El lote nuevo presenta una calidad diferente del lote inicial?
# MAGIC
# MAGIC Compará lotes usando proporciones además de cantidades absolutas. Señalá cualquier limitación de comparar lotes de tamaños distintos. Fuente sugerida: `gold_batch_summary`.
# MAGIC
# MAGIC El lote initial tuvo un 99,90 % de transacciones aceptadas y un 0,10 % rechazadas, mientras que batch_002 presentó un 99,01 % de aceptadas y un 0,99 % de rechazadas. Por lo tanto, el lote batch_002 tuvo una mayor proporción de rechazos que el lote inicial. Como los lotes tienen tamaños muy diferentes, es más adecuado comparar los porcentajes que las cantidades absolutas para evaluar la calidad de los datos.
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

batch_quality = (
    spark.table(batch)
    .withColumn(
        "total",
        F.col("accepted_transactions") + F.col("rejected_transactions")
    )
    .withColumn(
        "accepted_pct",
        F.col("accepted_transactions") / F.col("total") * 100
    )
    .withColumn(
        "rejected_pct",
        F.col("rejected_transactions") / F.col("total") * 100
    )
    .orderBy("source_batch_id")
)

plot_data = batch_quality.toPandas()

# Gráfico de barras apiladas al 100%
plt.figure(figsize=(9, 4))

plt.bar(
    plot_data["source_batch_id"],
    plot_data["accepted_pct"],
    color="steelblue",
    label="Aceptadas"
)

plt.bar(
    plot_data["source_batch_id"],
    plot_data["rejected_pct"],
    bottom=plot_data["accepted_pct"],
    color="orange",
    label="Rechazadas"
)

plt.xlabel("Lote")
plt.ylabel("Porcentaje de transacciones (%)")
plt.title("Porcentaje de transacciones aceptadas y rechazadas por lote")
plt.ylim(0, 100)
plt.legend()
plt.tight_layout()
plt.show()

# Mostrar cantidades y porcentajes
display(
    batch_quality.select(
        "source_batch_id",
        "accepted_transactions",
        "rejected_transactions",
        "total",
        "accepted_pct",
        "rejected_pct"
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Criterios de entrega
# MAGIC
# MAGIC Para cada consigna entregá: (1) la transformación de datos, (2) un gráfico, y (3) una conclusión de dos o tres oraciones que responda explícitamente la pregunta.
# MAGIC
# MAGIC Cada gráfico debe tener título informativo, ejes y unidades legibles, categorías ordenadas cuando corresponda y una elección de color que no sea la única forma de comunicar el significado. No conviertas una tabla Silver completa a Pandas: agregá primero con Spark y convertí sólo el resultado pequeño.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     current_catalog() AS catalogo,
# MAGIC     current_schema() AS esquema;
# MAGIC     
# MAGIC SELECT
# MAGIC     source_batch_id,
# MAGIC     COUNT(*) AS filas_fisicas
# MAGIC FROM bigdata_melisa_casella.bronze_transactions_incremental
# MAGIC GROUP BY source_batch_id
# MAGIC ORDER BY source_batch_id;
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 1: La tabla bronze_transactions_incremental recibió 204 filas físicas correspondientes a batch_002 y otras 204 correspondientes a batch_003, con un total de 408 registros. Esto demuestra que ambos lotes fueron incorporados a Bronze mediante el proceso de ingesta incremental.
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     source_batch_id,
# MAGIC     accepted_transactions,
# MAGIC     rejected_transactions,
# MAGIC     accepted_transactions + rejected_transactions AS total_transactions
# MAGIC FROM bigdata_melisa_casella.gold_batch_summary
# MAGIC ORDER BY source_batch_id;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 2: La tabla gold_batch_summary muestra que batch_002 tuvo 200 transacciones aceptadas y 2 rechazadas, mientras que batch_003 tuvo 201 aceptadas y 2 rechazadas. El lote initial registró 49.948 aceptadas y 51 rechazadas. Las transacciones rechazadas deben coincidir con los registros almacenados en silver_transactions_quarantine, mientras que las aceptadas corresponden a los registros que superaron las reglas de calidad y quedaron en Silver.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     source_batch_id,
# MAGIC     quality_reason,
# MAGIC     COUNT(*) AS cantidad
# MAGIC FROM bigdata_melisa_casella.silver_transactions_quarantine
# MAGIC GROUP BY source_batch_id, quality_reason
# MAGIC ORDER BY source_batch_id, cantidad DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 3: En la cuarentena aparecen dos motivos de rechazo para los lotes incrementales: INVALID_AMOUNT, correspondiente a importes inválidos, y UNKNOWN_CUSTOMER, correspondiente a clientes que no se encuentran registrados. En batch_002 y batch_003 se registró un rechazo por cada motivo, mientras que en initial hubo 51 registros rechazados por INVALID_AMOUNT. Los resultados coinciden con los casos inválidos introducidos por el generador y con las cantidades de rechazos informadas en gold_batch_summary.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM bigdata_melisa_casella.bronze_transactions_all
# MAGIC WHERE transaction_id = 42
# MAGIC ORDER BY updated_at;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM bigdata_melisa_casella.silver_transactions
# MAGIC WHERE transaction_id = 42;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 4: En Bronze existen tres versiones de la transacción 42: la original del lote initial y dos correcciones correspondientes a batch_002 y batch_003. En Silver quedó vigente la versión de batch_003, porque presenta el updated_at más reciente (11 de marzo de 2026 a las 02:00). Esto demuestra que el proceso de deduplicación y actualización mediante MERGE conserva la versión más reciente de la transacción.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     transaction_id,
# MAGIC     COUNT(*) AS cantidad
# MAGIC FROM bigdata_melisa_casella.silver_transactions
# MAGIC GROUP BY transaction_id
# MAGIC HAVING COUNT(*) > 1;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 5: La consulta no devuelve registros, lo que demuestra que cada transaction_id aparece una sola vez en silver_transactions. Esto confirma que el proceso de deduplicación funcionó correctamente. Si la consulta devolviera alguna fila, significaría que existen transacciones duplicadas y que la deduplicación falló.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     source_batch_id,
# MAGIC     accepted_transactions,
# MAGIC     rejected_transactions,
# MAGIC     ROUND(
# MAGIC         rejected_transactions * 100.0 /
# MAGIC         (accepted_transactions + rejected_transactions),
# MAGIC         2
# MAGIC     ) AS rejection_rate_pct
# MAGIC FROM bigdata_melisa_casella.gold_batch_summary
# MAGIC ORDER BY source_batch_id;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 6: El lote initial presentó una tasa de rechazo del 0,10 %, mientras que batch_002 y batch_003 registraron una tasa del 0,99 % cada uno. Por lo tanto, los dos lotes incrementales tuvieron una proporción de rechazos mayor que el lote inicial. No es correcto comparar solamente las cantidades absolutas cuando los lotes tienen tamaños diferentes, porque los porcentajes permiten evaluar la calidad independientemente del volumen de registros recibidos.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     sale_date,
# MAGIC     SUM(total_amount) AS monto_total,
# MAGIC     SUM(transaction_count) AS cantidad_transacciones
# MAGIC FROM bigdata_melisa_casella.gold_daily_sales
# MAGIC GROUP BY sale_date
# MAGIC ORDER BY monto_total DESC
# MAGIC LIMIT 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     sale_date,
# MAGIC     SUM(total_amount) AS monto_total,
# MAGIC     SUM(transaction_count) AS cantidad_transacciones
# MAGIC FROM bigdata_melisa_casella.gold_daily_sales
# MAGIC GROUP BY sale_date
# MAGIC ORDER BY cantidad_transacciones DESC
# MAGIC LIMIT 1;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 7: El 1 de marzo de 2026 presentó tanto el mayor monto total vendido, de 7.310.840,77 unidades monetarias, como la mayor cantidad de transacciones, con 7.236 operaciones. Por lo tanto, ambos máximos coinciden, lo que indica que ese día lideró tanto en facturación como en volumen de operaciones.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     payment_channel,
# MAGIC     SUM(fraud_transactions) AS total_fraudes,
# MAGIC     SUM(transaction_count) AS total_transacciones,
# MAGIC     ROUND(
# MAGIC         SUM(fraud_transactions) * 100.0 /
# MAGIC         SUM(transaction_count),
# MAGIC         2
# MAGIC     ) AS fraud_rate_pct
# MAGIC FROM bigdata_melisa_casella.gold_daily_sales
# MAGIC GROUP BY payment_channel
# MAGIC ORDER BY fraud_rate_pct DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 8: El canal de pago transfer presenta la mayor tasa global de fraude, con un 13,91 %, correspondiente a 2.327 transacciones fraudulentas sobre 16.723 operaciones. Le siguen wallet, con 12,97 %, y card, con 12,54 %. No corresponde promediar directamente fraud_rate porque cada grupo puede tener diferente cantidad de transacciones; por eso, la tasa global debe calcularse dividiendo la suma de fraudes por la suma de transacciones.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     country,
# MAGIC     category,
# MAGIC     SUM(total_amount) AS monto_total
# MAGIC FROM bigdata_melisa_casella.gold_daily_sales
# MAGIC GROUP BY country, category
# MAGIC ORDER BY monto_total DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH ranking AS (
# MAGIC     SELECT
# MAGIC         country,
# MAGIC         category,
# MAGIC         SUM(total_amount) AS monto_total,
# MAGIC         ROW_NUMBER() OVER (
# MAGIC             PARTITION BY country
# MAGIC             ORDER BY SUM(total_amount) DESC
# MAGIC         ) AS posicion
# MAGIC     FROM bigdata_melisa_casella.gold_daily_sales
# MAGIC     GROUP BY country, category
# MAGIC )
# MAGIC SELECT
# MAGIC     country,
# MAGIC     category,
# MAGIC     monto_total
# MAGIC FROM ranking
# MAGIC WHERE posicion = 1
# MAGIC ORDER BY country;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 9: La combinación de país y categoría que concentra el mayor monto vendido es Brasil (BR) en la categoría home, con 2.361.959,97 unidades monetarias. La categoría dominante cambia según el mercado: books lidera en Argentina y México, mientras que home lidera en Brasil, Chile y Uruguay. Esto demuestra que las preferencias de compra y la distribución de ventas varían entre los países.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE bigdata_melisa_casella.pipeline_run_audit;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM bigdata_melisa_casella.pipeline_run_audit;

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 10: Al comparar las dos primeras ejecuciones de batch_002 se observa que las métricas permanecieron iguales: 50.149 filas en Silver, 53 en cuarentena, 598 filas en Gold y un monto total de 50.286.183,33. La columna idempotence_compared, cuyo valor es true en ambas ejecuciones, demuestra que se realizó la comparación de idempotencia. Esto confirma que volver a ejecutar el pipeline sin generar nuevos archivos no modificó las métricas de negocio.
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 11: 
# MAGIC
# MAGIC Notebook: 01_ingest_bronze_incremental.ipynb
# MAGIC Sección: Creación de la tabla incremental e ingesta mediante COPY INTO.
# MAGIC
# MAGIC Respuesta:
# MAGIC
# MAGIC COPY INTO permite incorporar archivos nuevos desde el almacenamiento hacia una tabla Delta de manera incremental. Evita volver a cargar archivos físicos que ya fueron procesados, utilizando el registro de archivos previamente cargados y su información de identificación y ubicación. De esta manera, si se ejecuta nuevamente el proceso, no vuelve a incorporar el mismo archivo físico, evitando duplicaciones durante la ingesta.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 12: 
# MAGIC Notebook: 01_ingest_bronze_incremental.ipynb.
# MAGIC
# MAGIC Sección: Construcción de la vista unificada bronze_transactions_all.
# MAGIC
# MAGIC Respuesta: La vista bronze_transactions_all utiliza UNION ALL porque permite combinar los registros de Bronze sin eliminar duplicados automáticamente. Esto es importante porque Bronze conserva los datos originales recibidos, incluyendo distintas versiones de una misma transacción. Los duplicados de negocio se resuelven posteriormente en Silver, donde se aplican reglas de deduplicación y se determina cuál es la versión vigente de cada transacción.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 13: 
# MAGIC Notebook: 01_ingest_bronze_incremental.ipynb.
# MAGIC
# MAGIC Sección: Construcción de la vista unificada bronze_transactions_all, asignación de source_batch_id y updated_at.
# MAGIC
# MAGIC Las transacciones iniciales reciben source_batch_id = 'initial' para identificar que pertenecen a la carga original y diferenciarlas de los lotes incrementales posteriores. Se utiliza event_ts como updated_at porque permite establecer una referencia temporal para comparar las distintas versiones de una transacción. En el caso de la transacción 42, Bronze conserva tres versiones: la original y dos correcciones correspondientes a batch_002 y batch_003. Silver termina conservando la versión de batch_003, porque tiene el updated_at más reciente, correspondiente al 11 de marzo de 2026 a las 02:00.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 14:
# MAGIC
# MAGIC Archivo: common/quality_rules.py.
# MAGIC
# MAGIC Sección: Función add_transaction_types().
# MAGIC
# MAGIC Respuesta:
# MAGIC
# MAGIC La función try_cast permite convertir un valor al tipo de dato esperado sin interrumpir la ejecución cuando encuentra un dato inválido. Por ejemplo, si el importe contiene el texto N/A, try_cast devuelve NULL en lugar de generar un error que detenga el procesamiento. Luego, las reglas de calidad identifican ese valor nulo y asignan el motivo de rechazo INVALID_AMOUNT. De esta manera, el pipeline puede continuar procesando los demás registros y enviar los datos incorrectos a cuarentena.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 15: 
# MAGIC
# MAGIC Archivo: common/quality_rules.py.
# MAGIC
# MAGIC Sección: Función add_quality_reason().
# MAGIC
# MAGIC Respuesta:
# MAGIC
# MAGIC Las reglas de calidad asignan una única causa principal de rechazo mediante una secuencia de condiciones F.when(). Si un registro incumple más de una regla, se asigna únicamente el primer motivo cuya condición se cumple, ya que las condiciones posteriores no determinan el resultado de esa columna. Por eso, el orden es importante: primero se verifican los identificadores, luego la fecha, el importe, el canal de pago, la marca de fraude, la fecha de actualización y finalmente la existencia del cliente y del producto. Los incumplimientos posteriores no quedan registrados como motivos adicionales.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 16: 
# MAGIC
# MAGIC Notebook: 02_build_silver.ipynb.
# MAGIC
# MAGIC Sección: Construcción de clave de identificación y selección de la última versión.
# MAGIC
# MAGIC Respuesta:
# MAGIC
# MAGIC La columna _record_key se construye mediante F.coalesce(): primero intenta utilizar transaction_id_typed convertido a texto y, si este valor es nulo, genera un hash SHA-256 a partir de las columnas originales del registro (raw_columns), concatenadas con el separador ||. Para evitar ambigüedades, los valores nulos se reemplazan por el texto <NULL> antes de generar el hash.
# MAGIC
# MAGIC Luego, row_number() asigna un número de orden a los registros que comparten la misma _record_key, priorizando el updated_at_typed más reciente y, en caso de empate, el source_batch_id en orden descendente. Finalmente, se conserva únicamente el registro con _rn = 1. El hash permite identificar los registros cuando transaction_id no puede convertirse a un número, evitando que queden sin una clave de identificación.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 17: 
# MAGIC
# MAGIC Notebook: 02_build_silver.ipynb.
# MAGIC
# MAGIC Sección: Actualización incremental de silver_transactions.
# MAGIC
# MAGIC Respuesta:
# MAGIC
# MAGIC El proceso utiliza MERGE INTO para comparar las transacciones válidas nuevas con las que ya existen en silver_transactions, utilizando transaction_id como clave de coincidencia.
# MAGIC
# MAGIC La cláusula WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET * actualiza una transacción existente únicamente cuando la nueva versión tiene una fecha de actualización más reciente que la almacenada. Por otro lado, WHEN NOT MATCHED THEN INSERT * inserta las transacciones que todavía no existen en Silver. De esta manera, se incorporan nuevas transacciones y se actualizan las correcciones sin duplicar identificadores.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 18: 
# MAGIC
# MAGIC Notebooks: 02_build_silver.ipynb y 03_build_gold.ipynb.
# MAGIC
# MAGIC Sección: Actualización incremental de Silver y construcción de tablas Gold.
# MAGIC
# MAGIC Respuesta:
# MAGIC
# MAGIC Las tablas Gold se reconstruyen completamente mediante CREATE OR REPLACE TABLE ... AS SELECT, porque contienen agregaciones y métricas analíticas que deben reflejar el estado actualizado de Silver. Una ventaja de esta estrategia es que los indicadores se recalculan desde los datos confiables y se evita acumular errores en las agregaciones. Su limitación es que puede consumir más tiempo y recursos cuando aumenta el volumen de datos.
# MAGIC
# MAGIC En cambio, Silver utiliza MERGE porque necesita conservar los registros existentes e incorporar nuevas transacciones o correcciones. Su ventaja es que permite actualizar los registros correspondientes sin reconstruir toda la tabla, mientras que su limitación es que requiere definir correctamente las claves y condiciones de actualización para evitar inconsistencias.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 19: 
# MAGIC
# MAGIC Notebooks: 01_ingest_bronze_incremental.ipynb y 04_validate_pipeline.ipynb.
# MAGIC
# MAGIC Secciones:
# MAGIC
# MAGIC 01_ingest_bronze_incremental.ipynb: Ingesta incremental mediante COPY INTO y comprobación del lote esperado.
# MAGIC
# MAGIC 04_validate_pipeline.ipynb: Validación de parámetros, comparación de métricas e idempotencia.
# MAGIC
# MAGIC Respuesta:
# MAGIC
# MAGIC El parámetro expected_batch_id no participa en la detección de archivos nuevos porque su función es indicar qué lote se espera procesar y validar, no determinar qué archivos deben incorporarse. La detección de archivos nuevos la realiza COPY INTO en 01_ingest_bronze_incremental.ipynb, identificando los archivos que todavía no fueron cargados. En ese notebook, expected_batch_id también se utiliza para comprobar que existan registros del lote esperado en Bronze.
# MAGIC
# MAGIC Posteriormente, 04_validate_pipeline.ipynb utiliza el parámetro para verificar su formato, comparar las métricas de la ejecución actual con las de una ejecución anterior del mismo lote y comprobar la idempotencia. Por eso, batch_003 puede descubrirse automáticamente sin modificar el código del pipeline, cambiando únicamente el parámetro expected_batch_id al ejecutar el Job.

# COMMAND ----------

# MAGIC %md
# MAGIC Pregunta 20: 
# MAGIC
# MAGIC Documento: GUIA_CREAR_JOB.md.
# MAGIC
# MAGIC Sección: 3. Tareas y dependencias.
# MAGIC
# MAGIC Respuesta:
# MAGIC
# MAGIC Si la tarea build_silver falla, las tareas build_gold y validate quedan omitidas y no se ejecutan. Esto sucede porque el Job tiene dependencias secuenciales: ingest_bronze debe finalizar correctamente para ejecutar build_silver, luego build_gold depende de build_silver y finalmente validate depende de build_gold. De esta manera, el DAG evita construir tablas Gold con datos Silver incompletos y evita validar resultados que no fueron generados correctamente.
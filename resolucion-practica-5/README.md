# Entrega práctica 5 — MLOps con MLflow

- **Nombre:** Melisa Casella
- **student_id:** melisa_casella
- **Escala:** small

Respondé cada pregunta en una a tres oraciones. Cuando se pide un dato, copiá el valor que te dieron tus notebooks.

## Mis runs

Pegá acá la tabla que imprime `03_comparar_y_elegir` (sección 5) e indicá cuál quedó registrado como `champion`.

| run | modelo | features | class_weight | umbral | hiperparametros | train_pr_auc | pr_auc | accuracy | precision | recall | f1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exp_boosting | gradient_boosting | completas | ninguno | 0.5 | learning_rate=0.1, max_depth=8 | 0.66 | 0.581 | 0.917 | 0.696 | 0.362 | 0.476 |
| exp_boosting | gradient_boosting | completas | ninguno | 0.5 | learning_rate=0.1, max_depth=8 | 0.66 | 0.581 | 0.917 | 0.696 | 0.362 | 0.476 |
| exp_bosque | gradient_boosting | completas | ninguno | 0.5 | learning_rate=0.1, max_depth=8 | 0.66 | 0.581 | 0.917 | 0.696 | 0.362 | 0.476 |
| max_depth=8 | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| random_forest-completas-u0.5 | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| random_forest-completas-u0.5 | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| random_forest-completas-u0.5 | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| exp_umbral_02 | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| exp_umbral_02 | random_forest | completas | ninguno | 0.2 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.874 | 0.432 | 0.68 | 0.528 |
| exp_bosque | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| exp_bosque | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| exp_completas | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| exp_umbral_02 | logistic_regression | completas | ninguno | 0.2 | C=1.0 | 0.531 | 0.545 | 0.863 | 0.402 | 0.647 | 0.496 |
| exp_umbral_02 | logistic_regression | completas | ninguno | 0.2 | C=1.0 | 0.531 | 0.545 | 0.863 | 0.402 | 0.647 | 0.496 |
| exp_regla | logistic_regression | completas | ninguno | 0.5 | C=1.0 | 0.531 | 0.545 | 0.917 | 0.758 | 0.288 | 0.417 |


**Run registrado:** exp_boosting, modelo gradient_boosting, con features completas, umbral 0.5 y PR-AUC de test de 0.581. Se registró como versión 1 en Unity Catalog con el alias champion.

## Datos y tracking

**1.** El split train tiene 35.654 filas y un 11,05 % de contracargos; test tiene 7.129 filas y un 10,38 %; y nuevas tiene 7.165 filas y un 11,05 %. Se separa por fecha para simular una situación real, entrenando con datos del pasado y evaluando con transacciones futuras, evitando utilizar información del futuro durante el entrenamiento.

**2.** El modelo que siempre predice que no hay contracargo obtiene un accuracy del 89,6 %. Sin embargo, no detecta ningún fraude. Por eso se utiliza PR-AUC, que permite evaluar mejor la capacidad de identificar la clase minoritaria, considerando precision y recall.

**3.** Se registraron los parámetros C=1.0, class_weight=ninguno, feature_set=basicas, model_type=logistic_regression y threshold=0.5, además de la tabla y versión de datos. Las métricas fueron PR-AUC test=0.339, accuracy=0.896, precision=0.493, recall=0.045, F1=0.082 y ROC-AUC=0.794, entre otras. Como artefacto se guardó matriz_confusion.png. Un experimento agrupa distintos entrenamientos y un run representa una ejecución individual.

**4.** Autolog registró 46 parámetros y 7 métricas: accuracy, F1, log loss, precision, recall, ROC-AUC y training_score, todas correspondientes al entrenamiento. También guardó artefactos como gráficos de matrices de confusión y curvas. A diferencia del registro manual, autolog no registra específicamente nuestras métricas de test ni el PR-AUC de test que necesitamos para comparar los modelos según el problema.

**5.** Sí, ambos runs dieron exactamente las mismas métricas: PR-AUC test=0.5099, accuracy=0.9094, precision=0.7217 y recall=0.2068, entre otras. Para reproducir un experimento hay que fijar los datos, el código, la semilla aleatoria y el entorno de ejecución.

**6.** Al llamar al modelo sin la columna amount se produjo un error porque faltaba una variable obligatoria que el modelo esperaba recibir. La firma (signature) define las columnas, los tipos de datos de entrada y las salidas esperadas, permitiendo validar que los datos tengan el formato correcto antes de realizar predicciones.

## Tus experimentos

**7.** La mejor configuración según test_pr_auc fue gradient_boosting + features completas + umbral 0.5, con un PR-AUC de test de 0.581. Superó tanto a la regresión logística (0.545) como al random forest (0.568) con el mismo set de features.

**8.** Las features aportaron de forma progresiva y clara: solo_regla (PR-AUC 0.170) → basicas (0.339) → cliente (0.448) → completas (0.545). El salto más importante se produjo al pasar de basicas a cliente y luego a completas, mostrando que las variables adicionales aportan información útil para detectar contracargos.

**9.** Con features completas, Gradient Boosting obtuvo el mejor PR-AUC (0.581) y el mayor recall (0.362). Random Forest quedó segundo (0.568) con mayor precision (0.799), mientras que la regresión logística logró 0.545. Gradient Boosting ofreció el mejor equilibrio general para este problema.

**10.** Al usar class_weight = balanced en la regresión logística con features completas, el recall subió fuertemente de 0.288 a 0.799, pero la precision cayó de 0.758 a 0.296 y las alertas pasaron de 281 a 1999. El PR-AUC se mantuvo casi igual (0.540 vs 0.545), mostrando que el cambio afecta el punto de operación más que la capacidad de ranking del modelo.

**11.** Al bajar el umbral de 0.5 a 0.2 en la regresión logística con features completas, el recall aumentó de 0.288 a 0.647 y las alertas subieron de 281 a 1193, mientras que la precision bajó de 0.758 a 0.402. El PR-AUC no cambió (siguió en 0.545), confirmando que el umbral solo mueve el punto de decisión sobre la misma curva.

**12.** En el barrido de max_depth del Random Forest, el mejor valor de test fue max_depth = 8 (PR-AUC 0.568). Cuando se dejó sin límite, el train_pr_auc llegó a 1.0 mientras el de test bajó a 0.537, evidenciando un claro sobreajuste: el modelo memorizó los datos de entrenamiento y perdió capacidad de generalización.

## Comparar y elegir

**13.** Sí, coincidieron. El mejor run tanto por PR-AUC como por accuracy fue exp_boosting (gradient_boosting + features completas + umbral 0.5), con PR-AUC = 0.581 y accuracy = 0.917. Pueden no coincidir porque la accuracy se ve muy influida por el desbalance de clases (casi el 90 % son “sin contracargo”), mientras que el PR-AUC mide mejor la capacidad de detectar la clase minoritaria.

**14.** El run que queda más lejos de la diagonal es max_depth=sin_limite (train_pr_auc = 1.0 y test_pr_auc = 0.537). Eso indica sobreajuste: el modelo memorizó casi perfectamente los datos de entrenamiento y perdió capacidad de generalización en test.

**15.** La ventaja de mlflow.search_runs es que permite filtrar, ordenar y analizar muchos runs de forma programática y reproducible, sin tener que revisarlos manualmente uno por uno en la interfaz.
El filter_string pedido sería:

filter_string = "params.model_type = 'random_forest' AND metrics.test_pr_auc > 0.55"

**16.** En fraude suele costar más un contracargo no detectado (pérdida económica directa) que una alerta falsa (costo operativo de revisión). Si el equipo de riesgo tiene capacidad limitada de revisión diaria, se ajusta el umbral para generar aproximadamente esa cantidad de alertas (subiendo o bajando el umbral según se necesite más o menos volumen), priorizando las transacciones de mayor score de riesgo.

## Registro, uso y monitoreo

**17.** Sí se pudo registrar. El modelo quedó como workspace.bigdata_melisa_casella.fraud_model versión 1 con alias champion.
La ventaja de cargar models:/...@champion es que el código de inferencia siempre usa el modelo actual marcado como productivo, sin tener que cambiar el run_id cuando se registra una nueva versión mejor.

**18.** Se puntuaron 7.165 transacciones nuevas y se generaron 382 alertas (5,3 %).
Las columnas que permiten auditar cada decisión son: model_name, model_version, run_id, threshold y scored_at.
El umbral se guarda fuera del modelo porque es una decisión de negocio que puede cambiarse sin necesidad de reentrenar ni registrar una nueva versión del modelo.

**19.** El rendimiento del modelo sobre las transacciones nuevas se mantuvo bastante parecido al de test: el PR-AUC pasó de 0,581 a 0,563 y el ROC-AUC de 0,887 a 0,886. El drift es un cambio en la distribución de los datos de entrada o de los scores, y puede detectarse antes de recibir las etiquetas reales observando cambios en variables como importes, medios de pago y la distribución de probabilidades. En la campaña simulada, el cambio en los datos puede modificar los scores y aumentar la cantidad de alertas, por lo que sería necesario revisar el umbral o evaluar un reentrenamiento.


## Cierre

**20.** En esta práctica se recorrieron las principales etapas del ciclo de vida de MLOps: preparación de datos, entrenamiento, seguimiento con MLflow, comparación y selección de modelos, registro en Model Registry con alias champion, inferencia batch y monitoreo. Para llevar este sistema a producción real faltarían procesos automatizados de despliegue y reentrenamiento, monitoreo continuo con alertas ante drift o degradación de métricas, y mecanismos de validación antes de reemplazar el modelo champion.

## Resumen:
En este análisis se utilizaron datos del Banco Central de Chile usando la API 'bcchapi'. Se usaron datos del PIB anual de las 16 regiones y el recaudado por 
sus diferentes servicios (Pesca, Mineria, Construccion, etc..) con una coleccion que abarca desde el 2013 al 2024, se obtuvo información relevante de ellos,
usando programacion en python (pandas) y estadistica, se pudo identificar:
- Una prediccion de los posible servicios dominantes en el futuro.
- Analisis COVID
- Generacion de electricidad por region y su correlacion con el PIB.

Este proyecto continua con un informe en power BI, donde se visualiza este informacion, conteniendo las siguientes secciones (por ahora):
- PIB por regiones
- Servicios

## Power BI
Con el fin de visualizar este proyecto se confecciono un informe con las siguientes secciones:
- PIB por Región: Enfoque en el PIB generado por region en cada año (no en su servicio).
<figure>
   <img src="Power BI/page_1.png" alt="drawing" width="400"/>
  <figcaption>Mapa de Chile con region coloreada segun su PIB, graficos de lineas mostrando la region metropolitana y las 5 regiones que mas contribuyen, tarjetas de crecimiento con su año anterior y grafico de barra de las regiones.</figcaption>
</figure>


- PIB por Servicio: Responder visualmente ¿cual es el servicio que mas produce PIB?, ¿cuales estan a punto de se remplazados? y el de mayor crecimiento.

## Analisis Detallado:

### Principales Regiones
En el año 2024 las regiones que mas contribuyeron fueron:
| Región | PIB |
|:--- | :--- |
|Region Metropolitana de Santiago|118.637,69 MM$|
|Antofagasta|33.249,73 MM$|
|Valparaíso|22539.73 MM$|

Además tambien fueron las regiones que mas han contribuido en el periodo 2013 - 2024.

### Principales Servicios por Región
Pregunta: ¿Que servicios son la principal fuente de PIB de cada región?

En esta seccion, me enfoque mas en averiguar los tres servicios que mas generan PIB del 2024 en cada region, queda pendiente un analisis historico de las regiones.
El resultado fue una notoria dominancia de los servicios personales	y  servicios financieros y empresariales, si bien esto responde la pregunta, queda la intriga si ¿Estos servicios entregan la mayor cantidad de PIB? si no ¿Cuanto se diferencia con el principal servicio del pais?
Para la vista mas detallada se puede consultar la [tabla.1](Tablas/Serv_x_region.md).

Respuesta:

Los servicios que entregaron la mayor cantidad de PIB historicamente (y que tambien son los principales servicios del 2024) son:
| Servicio | PIB historico |
|:--- | :--- |
|Servicios financieros y empresariales|330.876,37 MM$|
|Servicios personales|296.890,25 MM$|
|Minería|261.564,25 MM$|

Seguidos por la industria manufacturera y el comercio.

### Crecimiento de Regiones
pregunta: ¿Que regiones han crecido más en el periodo 2013-2024?

Si bien las principales regiones que contribuyen al PIB son la región Metropolitana de Santiago, Antofagasta y Valparaíso, lo realmente interesante aqui es saber que region crecio mas en este periodo, para esta seccion se calculo el crecimiento acumulado.

|Región|Porcentaje|
|:---|:---|
|Tarapacá|187.96%|
|Antofagasta|167.13%|
|O'Higgins|157.74%|


### Estudio de Tendencias
Pregunta: ¿Cuales servicios principales pueden ser reemplazados en el futuro?

Se buscaba predecir en un tiempo no mayor a 30 años, cuales regiones estan pasando por un proceso de cambio economico, ...
Se utilizaron tres criterios en cada servicio para esta prediccion, el ratio de los pib no debe ser menor a 0.2, la pendiente debe ser mayor y su crecimiento acumulado debe ser mayor.

- Se encontro que las regiones de Magallanes y la Antártica chilena y Los lagos en un plazo de 3 años (2027) la industria manufacturera reemplacen a los 
serivios personales y administracion publica, esto posiblemente debido al alza de la venta de los salmones.
- La region del Maule tiene como PIB principa historicamente a la industria manufacturera, pero puede ser remplazada por Vivienda.
- Los Rios a diferencia de Los Lagos, su industria manufacturera en un plazo de 2 a 3 años puede ser remplazado por servicios personales.

### Analisis COVID.
preguntas: ¿En que afecto la pandemia a los servicios de las regiones? y ¿El PIB post-pandemia recupero lo proyectado del PIB pre-pandemia?

Para esto se dividieron los datos, pre y post, sin considerar el 2020, se estudio el cambio de la tendencia, la volatilidad y el crecimiento acumulado compuesto (CAGR), para ello se tuvieron que normalizar los datos, ya que pre pandemia se consideran 7 años y post 4 años.

- El cambio de la tendencia en la regiones provoco un rebote gigante, teniendo una pendiente muy positiva, causada por el efecto rebote de la pandemia.
- La volatilidad tuvo efecto distinto en cada region, algunos post pandemia la redujo haciendo un efecto de estabilizador, mientras que otras sufrieron una mayor inestabilidad, aunque puede ser atribuido al efecto rebote.
- El CAGR Tambien sufre aquel efecto rebote de la pandemia, por lo que no es un buen estadistico para concluir como esta el pais post pandemia.

Se espera que a futuro se pueda responder la segunda pregunta.

### Relacion del PIB con la Generacion de Electricidad

Preguntas: ¿El aumento de generacion de electrcidad implica aumento en el PIB o viceversa? y ¿Este aumento puede atribuirse al crecimiento del año anterior?

Del mismo banco central es posible descargar datos mensuales de la generacion y distribucion de electrcidad (Mwh) de algunas regiones, para poder relacionarlo con el PIB se calculo el promedio de cada año. 
Lo interesante se encuentra en el norte (Antofagasta y Atacama ) donde un el PIB tiene un mayor impacto cuando crece la generacion de electricidad del año anterior en la region, esto posiblemente debido al rubro minero. Mientras que algunas regiones (Los lagos, Ñuble y Arica y parinacota) con principal rubro los Servicios personales (Actividades deportivas, artisticas, de entretencion, peluquerias,etc...) arrastran la demanda energetica.Los demas presentan datos no significativos, lo que puede deberse a ajustes anuales y no presentan una tendencia alcista o bajista.

El dato interesante es Valparaíso, genera electricidad que no se traduce en crecimiento económico local, posiblemente, el cierre progresivo de las plantas a carbon. Su economía crece por servicios, comercio y turismo, no por industria electrointensiva.
Para mayor detalle acerca de la [Tabla.2](Tablas/Elec_x_PIB.md)

### Series de Tiempo

pregunta: ¿Es posible predecir el PIB regional usando la generación eléctrica como variable anticipadora?

Se entrenaron modelos ARIMA y SARIMA sobre los datos mensuales de electricidad para proyectar el PIB mediante regresión lineal. El error relativo del sistema de dos etapas fue del 20–30%, insuficiente para uso predictivo práctico. Queda pendiente explorar modelos con lag explícito y variables exógenas adicionales como empleo y desocupación.

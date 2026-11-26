# Ambición: la mejor variante, no la más sencilla

## El sesgo que hay que corregir

El agente tiende a elegir la variante que **él** implementa antes: menos código, menos pasos y menos riesgo de que algo
falle delante del usuario. Después la presenta como si fuera una decisión técnica. Eso es un **sesgo por el coste de
implementación**, no una razón medida, y es lo que impide llegar al estado del arte. Casos reales:
- **Sonda del profesor:** se preparó una sonda lineal sobre la última capa cuando el artículo daba por mejor MLP sobre
  capas intermedias.
- **Receta heredada:** se reutilizó la receta de otro alumno, con 1 época, para un brazo que tenía la quinta parte de los
  pasos.
- **Revisión tardía:** el estado del arte de la destilación solo se revisó cuando el usuario lo pidió.

**Regla:** lo que cuesta implementar al agente **no es un criterio**. Solo cuentan tres cosas:
1. la calidad para el usuario;
2. el coste en el dispositivo: tamaño, latencia, memoria y batería;
3. el tiempo de máquina, y solo cuando es prohibitivo y se dice con su número (horas, días).

## Antes de montar una cola, un entrenamiento o un experimento

Cada etapa, cada vez, sin esperar a que el usuario lo pida.

1. **Barrido de frontera con fecha.**
   - **Qué se busca:** métodos, modelos y bancos de los últimos 12 meses, más los clásicos que dominan la etapa.
   - **Búsquedas:** como mínimo tres distintas, una por eje: método u objetivo, modelo o arquitectura, y datos y su
     selección.
   - **Fuentes:**
     - arXiv (cs.CL, cs.LG, cs.IR);
     - actas del año (ICLR, NeurIPS, ICML, ACL, EMNLP);
     - tendencias y fichas de modelo de Hugging Face;
     - blogs de los laboratorios;
     - machinelearning.apple.com;
     - clasificaciones públicas.
   - **Si un resumen no basta:** se lee el artículo, no el resumen de un tercero.
2. **Tabla de palancas.**
   - **Qué tiene cada fila:** la variante actual, la mejor publicada, su evidencia y su coste.
   - **La evidencia:** dominio, tamaño del efecto y si hay réplica independiente.
   - **El coste:** en máquina y en dispositivo.
   - **Palancas de un modelo propio:**
     - datos y su volumen;
     - señal del profesor;
     - objetivo o pérdida;
     - arquitectura del alumno;
     - calendario e hiperparámetros;
     - selección de datos;
     - compresión.
   - **Lo que no se adopta:** se dice por qué, con su número.
3. **La variante que el artículo da por mejor, primero.** Al adoptar un método se implementa la configuración con la que
   el artículo saca su mejor resultado: capas, cabeza, pérdida e hiperparámetros. Lo más simple entra solo como
   **ablación medida** al lado, nunca en su lugar. «Si sobra margen, después» no vale como excusa.
4. **Espacio de variantes declarado y elección anidada.** Las variantes, sus rangos y la métrica se escriben en el
   prerregistro. Se eligen dentro de los pliegues de entrenamiento, con validación anidada o un dev aparte. El conjunto de
   prueba no elige nunca.
5. **Auditoría de la receta heredada.** Una receta adoptada en otra configuración, con otros datos, otro tamaño, otro
   profesor u otras clases, no se reutiliza sin comprobar sus supuestos:
   - **Pasos efectivos:** filas × épocas ÷ lote. Al comparar brazos, que tengan señal comparable.
   - **Datos:** tamaño y reparto de las etiquetas.
   - **Contaminación:** cruce entre train, dev, prueba y oro, por id y por texto, también de traducciones.
   - **Vistas:** que profesor y alumno vean la misma entrada, o que la diferencia sea intencionada.
   - **Coste:** que los límites en el dispositivo sigan cumpliéndose.
6. **Ataca la premisa compartida.** Si dos variantes con la misma premisa fallan, se escribe la premisa y se mide.
7. **Pregunta de cierre, por escrito, antes de dar un plan por bueno.** Hay que responder dos preguntas: «¿qué haría un
   equipo de investigación de primer nivel con estos recursos?» y «¿qué estoy dejando fuera porque me da más trabajo?».
   Cada respuesta se lista y se decide con números.

## Prohibido

- Elegir por facilidad de implementación sin decirlo, o disfrazarlo de decisión técnica.
- Reutilizar una receta o un hiperparámetro de otra configuración sin la auditoría del punto 5.
- Dejar la variante buena para «si sobra margen» cuando el artículo ya dice que es la buena.
- Esperar a que el usuario pida la revisión del estado del arte.
- Descartar una idea por un intento barato que falló.
- Ordenar el plan por lo barato. Lo barato va delante solo como criba explícita, seguida de la variante completa.

## Cuándo sí es legítimo simplificar

- **Coste prohibitivo:** el de máquina o dispositivo lo es, y se dice con su número.
- **Medición previa:** en esta misma configuración, una medición ya mostró que la variante compleja no gana.
- **Criba:** es una criba barata declarada como tal en el prerregistro, y la variante completa corre después sobre lo que
  pase.

## Lista para destilar un modelo propio (estado de nov-2026; vuelve a barrer)

- **Profesor:**
  - Se mide contra oro humano antes de etiquetar. Si hay varios candidatos, se elige el mejor y se mira si combinarlos
    gana.
  - Combinación explícita, con Dawid-Skene, distribuciones blandas o filtro de confianza.
- **Señal del profesor:**
  - Distribución completa, no top-k truncado; si se quita una clase, se renormaliza.
  - Medir **sondas sobre sus estados internos** (PROBE-KD, ICLR 2026: MLP sobre capas intermedias, entrenada con oro)
    frente a su salida.
  - Temperatura elegida en oro, con NLL y ECE.
- **Objetivo:** mezcla de etiqueta dura (oro) y blanda (profesor) con α elegido en validación. Bridge-Garden (2026)
  encuentra que la mezcla gana a lo blando solo.
- **Conjunto de transferencia:**
  - **Tamaño:** grande; medir la curva de datos (½ frente a todo) antes de decidir si etiquetar más.
  - **Selección:** si hay que etiquetar más, por incertidumbre y diversidad, con muestreo activo (M-RARU, 2025), no al
    azar.
- **Calendario:**
  - Largo, con parada por validación («a good teacher is patient and consistent», 2022).
  - Los brazos se comparan con pasos efectivos comparables.
- **Consistencia:** el profesor y el alumno ven la misma vista del texto, o la diferencia es intencionada y se dice.
- **Alumno:**
  - Bake-off de los codificadores recientes con licencia libre: lo de los últimos 12 meses frente al actual.
  - Su coste en el dispositivo, medido: INT8, vocabulario podado, p95 y memoria.
- **Compresión:** un alumno de alumno, más pequeño, destilado del ganador con muchos datos sin etiquetar, si baja tamaño
  o latencia sin perder acierto significativo.
- **Higiene:**
  - Cruce de ids y textos entre train, dev, prueba y oro.
  - Tres semillas o más, con media y desviación.
  - Hiperparámetros solo en validación.
  - Confirmación final en un banco reservado y consultado una sola vez.

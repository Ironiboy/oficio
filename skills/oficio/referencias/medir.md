# Medir para decidir

## Protocolo

0. **Nada se da por hecho.** Antes de medir, investiga: qué publica hoy el estado del arte para esta etapa, qué
   bancos con anotación humana existen y qué jueces los resuelven mejor. El plan sale de esos datos, no de la
   costumbre ni de lo que ya se usaba.
1. **Prerregistro:** antes de mirar, escribe en `DECISIONES.md` qué se mide, con qué juez y qué regla decide, y el
   tamaño de muestra que hace falta para ver la diferencia buscada (con la varianza de las diferencias pareadas
   ya medidas, no a ojo). Nunca se cambia la regla después de ver los números.
2. **Línea base:** reproduce la cifra de producción en el mismo banco y la misma máquina.
3. **Candidatos:** variantes y barridos; cada umbral elegido queda comentado con su cifra.
4. **Intervalos:** bootstrap pareado por unidad (frase, artículo); macro por subgrupo (lengua, plataforma).
5. **Regla de adopción:** límite inferior del Δ por encima de 0, ningún subgrupo cae más de 2 pp, cero casos
   buenos rotos, coste igual o menor.
6. **Ficha** de cada versión adoptada (datos, fuentes, cifras, fecha de la última revisión del estado del arte).

## Jueces

**Un juez sin validar no decide nada.** Un modelo usado como juez (fidelidad, cobertura, preferencia) es un
instrumento y se mide como tal, por tarea, antes de usarlo:

- **Contra anotación humana pública** del mismo tipo de tarea y dominio (p. ej. LLM-AggreFact, MSumBench, RoSE,
  SummEval), por lengua y por dominio. Exactitud equilibrada y AUC; el umbral se calibra en una parte y se mide en
  otra. Un juez bueno en la media puede ir al azar en tu dominio: mira el subgrupo que te toca.
- **Bake-off de jueces** como de cualquier etapa: los del momento, especialistas recientes con licencia libre y
  paneles de familias distintas (media de probabilidades, voto). Puede ganar uno distinto para cada tarea.
- **Estabilidad:** en comparaciones por pares, el veredicto solo cuenta si se mantiene al invertir el orden; si
  el juez se contradice a menudo, esa métrica no decide.
- **Sin anotación humana en tu lengua**, se construye un oro (consenso validado o un anotador fuerte medido antes
  en los bancos públicos) y se declara cómo se hizo.
- Se revisan con fecha, como cualquier etapa: un juez nuevo entra al bake-off.


- **Desarrollo:** para elegir hiperparámetros. Se declara su sesgo (p. ej. consenso de maestros).
- **Fresco de un solo uso:** datos nuevos con la regla escrita antes de mirar; se consulta una vez, con todos los
  candidatos juntos. Las pasadas de descarga son diarias y se fusionan con reglas fijas; si una pasada se olvida,
  se declara.
- **Humano:** anotación pública (p. ej. SIB-200). Comprueba que no se coló en el entrenamiento, **tampoco
  traducido**, y si el entrenamiento trae otras frases del mismo banco, que ya no es un juez del todo ajeno.
- **Producto:** estabilidad, latencia, pico de memoria y coste en el Mac y en el dispositivo.

## Bancos

- **El banco principal es público, variado y grande:** varias fuentes, géneros y lenguas, con licencia libre. Los
  datos del usuario son una segunda prueba (el ruido real del producto), nunca la única base de una decisión.
- Una parte reservada solo para la confirmación final; no se itera sobre ella.

## Entrenamientos

- Los profesores (jueces que etiquetan) se miden primero contra oro humano; sus etiquetas se combinan con un
  método explícito (Dawid-Skene, probabilidades blandas, filtro de confianza).
- Siempre 3 semillas o más, con media y desviación; hiperparámetros solo en validación; el oro no se toca.

## Antes de decidir, comprueba

1. ¿Investigado el estado del arte de esta etapa, con fecha?
2. ¿El juez está validado contra humanos para esta tarea, lengua y dominio?
3. ¿Banco público principal y, además, los datos reales?
4. ¿Prerregistro con regla y tamaño de muestra suficiente?
5. ¿Intervalo, subgrupos y coste según la regla de adopción?

Si alguna respuesta es no, todavía no se decide: se mide o se investiga.

**Ataca la premisa.** Si dos variantes o arreglos que comparten una premisa fallan la misma puerta, se escribe esa
premisa en una frase y se mide la premisa antes de probar otra variante. Siete variantes de un resumen que daban por
hecho que «8 frases bastan» perdieron todas; medir cuántos hechos clave caben en 8 frases lo habría dicho a la segunda.

## Trampas de medida

- Un juez que nadie ha validado convierte cualquier diferencia en opinión: valídalo antes de leer sus cifras.

- La validación contra metadatos ruidosos premia el ruido.
- Elegir el maestro y juzgar al alumno con el mismo banco infla el resultado; dilo.
- La máquina ocupada (entrenando, compilando) invalida las latencias; anota la condición y repite.
- Un filtro de tests que no casa con nada «pasa»: exige que corra al menos un test.
- Un fallo de «extracción» puede ser de descarga: separa las etapas reproduciendo con el mismo cliente.
- Datos reales a escala sacan lo que los bancos no ven (2.000 descargas reales frente a HTML guardado).
- Un resultado demasiado bueno: busca el artefacto antes de celebrarlo.

## Sin etiquetado manual

Las referencias salen de bancos públicos clasificados, de metadatos (secciones de medios) y de consensos de
modelos. Nunca se pide al usuario que revise a mano.

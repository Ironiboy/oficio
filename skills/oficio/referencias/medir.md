# Medir para decidir

## Protocolo

1. **Prerregistro:** antes de mirar, escribe en `DECISIONES.md` qué se mide, con qué juez y qué regla decide.
   Nunca se cambia la regla después de ver los números.
2. **Línea base:** reproduce la cifra de producción en el mismo banco y la misma máquina.
3. **Candidatos:** variantes y barridos; cada umbral elegido queda comentado con su cifra.
4. **Intervalos:** bootstrap pareado por unidad (frase, artículo); macro por subgrupo (lengua, plataforma).
5. **Regla de adopción:** límite inferior del Δ por encima de 0, ningún subgrupo cae más de 2 pp, cero casos
   buenos rotos, coste igual o menor.
6. **Ficha** de cada versión adoptada (datos, fuentes, cifras, fecha de la última revisión del estado del arte).

## Jueces

- **Desarrollo:** para elegir hiperparámetros. Se declara su sesgo (p. ej. consenso de maestros).
- **Fresco de un solo uso:** datos nuevos con la regla escrita antes de mirar; se consulta una vez, con todos los
  candidatos juntos. Las pasadas de descarga son diarias y se fusionan con reglas fijas; si una pasada se olvida,
  se declara.
- **Humano:** anotación pública (p. ej. SIB-200). Comprueba que no se coló en el entrenamiento, **tampoco
  traducido**, y si el entrenamiento trae otras frases del mismo banco, que ya no es un juez del todo ajeno.
- **Producto:** estabilidad, latencia, pico de memoria y coste en el Mac y en el dispositivo.

## Trampas de medida

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

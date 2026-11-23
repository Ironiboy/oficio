# Contexto y tokens: gastar poco sin perder calidad

El contexto es el presupuesto del trabajo. Lo que entra se queda y pesa en cada turno siguiente, y al compactar
se pierde detalle. Se ahorra en lo que no aporta, **nunca en verificar**: rehacer un trabajo mal cerrado cuesta
más que cualquier lectura.

## Lo que no se recorta nunca

- Leer el código que vas a cambiar y el que lo llama.
- Ejecutar los tests y las puertas, y mirar su salida (filtrada, pero mirada).
- La evidencia antes de decir «hecho».
- Las medidas que deciden algo.

## Leer

- **Busca antes de leer:** `grep -n` o `rg` para localizar, y luego lees solo ese rango (`offset`/`limit`,
  `sed -n 'a,bp'`). Un fichero entero solo si lo vas a reescribir.
- **No releas** lo que ya está en contexto; tras editar, la herramienta ya confirma el cambio.
- **Las salidas, filtradas:** `tail`, `grep -E "error|warning:|✘|passed|failed"`, `head`, `cut -c1-160`. Un
  log entero nunca. Los JSON y los logs grandes se resumen con un script que imprime las cifras.
- **Lo generado va a disco**, no al contexto: predicciones, tablas, listados. En el contexto, la ruta y el
  resumen.
- **Llamadas independientes en paralelo**, en la misma respuesta.

## Esperar

- **Procesos largos en segundo plano**, con aviso al terminar. Nada de `sleep` en bucle ni de mirar el log cada
  minuto. Si hay que esperar una condición, un bucle `until` que imprima una sola línea.
- **Sin agente vigilando un entrenamiento:** se lanza, se termina el turno y se recoge al avisar.

## Agentes

- **Por defecto, ninguno.** Cada uno arranca en frío y paga otra vez el contexto, y sus conclusiones llegan sin
  la evidencia. Una puerta mide; un revisor opina.
- **Cuándo sí:** el usuario lo pide, o una lectura masiva (decenas de ficheros o páginas web) de la que solo
  quieres la conclusión. El prompt es corto, apunta a ficheros en vez de copiar contexto, pide el formato exacto
  de vuelta y usa el modelo más pequeño que valga.

## Sesiones

- **`/clear` tras cada commit verde**, con `TRASPASO.md` escrito (≤ 40 líneas: plan y paso, último commit, lo que
  queda a medias, siguiente acción, comandos exactos, trampas). Lo propone el agente; lo ejecuta el usuario.
  Nunca con una puerta a medias ni con procesos corriendo que haya que recoger.
- **`/compact` con instrucciones de foco** antes de un cambio grande de tema, si no se puede limpiar.
- **La sesión nueva empieza por `TRASPASO.md` y el plan**, no explorando el repo.
- **Worktrees:** al acabar, se borra el que nada usa (ni proceso ni cola) y su compilación; lo que tenga cambios sin
  commit espera a que se decida o se conserva en otro sitio antes. Sin limpiar, cuatro copias con su `.build` se comen
  el disco de 16 GB.
- **Memoria:** un hecho por fichero, con su porqué; el índice, una línea por entrada. Nada que ya esté en el
  repo o en el historial.
- **Skills e instrucciones cortas:** lo que se carga siempre (CLAUDE.md, SKILL.md, hooks), al mínimo; el
  detalle, en referencias que se leen al necesitarlas.

## Responder

- Primero el resultado, luego lo imprescindible. Sin recapitular lo que el usuario ya sabe ni narrar cada paso.
- Tablas para comparar cifras; nada de párrafos para lo que cabe en una fila.

## Secuenciar

- Antes de una tarea cara, mira si otra en curso puede volverla innecesaria, y espera a su resultado.
- Barato antes que caro: un sondeo de 20 casos antes de una pasada de 20.000; una ablación de fuentes antes de
  etiquetar con todas.

## Máquina (16 GB)

- **Un proceso pesado a la vez:** un LLM, un entrenamiento o una tanda de mutantes. Juntos llenan la memoria y
  el sistema mata procesos de fondo. Encadénalos en serie.
- **El usuario también usa la máquina:** baja el lote (con acumulación de gradiente la receta no cambia) o
  pausa. Puntos de control cada N pasos para retomar sin perder nada.
- **Disco:** compruébalo antes de convertir, descargar o entrenar; los puntos de control y las conversiones
  temporales ocupan varios GB. Borra lo descartado con número y lo regenerable, nunca lo que no entiendes.
- **Mutantes** en una copia aparte del repo (worktree), sin tocarla mientras corren, con tiempo límite y
  matando los ayudantes de test huérfanos.
- No compiles ni midas dos cosas a la vez mientras se mide tiempo.

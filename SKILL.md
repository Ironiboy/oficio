---
name: oficio
description: >-
  Forma definitiva de desarrollar apps para el ecosistema Apple (iOS, iPadOS, macOS, watchOS, visionOS) con
  Swift/SwiftUI: el guantelete de Uncle Bob (tests de aceptación primero, CRAP ≤ 8, cero mutantes vivos, forma,
  cero warnings), decisiones con números, estado del arte siempre, IA en el dispositivo con degradación, diseño
  nativo, trampas verificadas de SwiftData/SwiftUI/concurrencia/plataforma y economía de tokens y de máquina.
  Usar al empezar o retomar cualquier proyecto Apple, en cada ciclo de código, y antes de decidir un framework,
  un modelo, un formato o una receta.
---

# Oficio: desarrollar para Apple con el método de Uncle Bob

La exigencia vive en **herramientas que dicen sí o no** y en **números medidos**, no en instrucciones largas ni
en opiniones. Este fichero es corto a propósito; el detalle está en `referencias/`. Lee solo la que toque.

| Cuando vayas a… | Lee |
|---|---|
| escribir o cerrar código (cada ciclo) | §1 y `puertas-swift/README.md` |
| decidir algo (framework, modelo, umbral, receta) | §2, §3 y `referencias/medir.md` |
| tocar SwiftData, CloudKit o el esquema | `referencias/swiftdata.md` |
| tocar concurrencia, actores, `Sendable` | `referencias/concurrencia.md` |
| diseñar o tocar vistas SwiftUI | `referencias/diseno.md` y `referencias/swiftui.md` |
| extensiones, widgets, segundo plano, firma, Info.plist | `referencias/plataforma.md` |
| IA (Foundation Models, Core ML, Core AI, modelos propios) | `referencias/ia.md` |
| descargar de la web (bancos, scraping, red de la app) | `referencias/red.md` |
| trabajos largos, varios agentes o contexto grande | `referencias/economia.md` |

## 1. El guantelete, en cada cambio

Un solo agente recorre la cadena y repite cada puerta hasta que pasa. Las puertas miden **solo lo tocado**
frente a una base (`HEAD` o la rama principal), así que se exigen al máximo desde el primer día.

1. **Specifier:** criterios de aceptación como tests, **antes** del código. Tienen que fallar, y por la razón
   esperada.
2. **Coder:** el diff más corto que funcione. Borrar antes que añadir. Sin abstracciones que nadie pidió.
   Plataforma y stdlib primero; una dependencia externa solo tras medir la alternativa nativa.
3. **Cleaner:** CRAP ≤ 8 por función tocada (`CRAP = c² · (1 − cobertura)³ + c`).
4. **Hardener:** cero mutantes vivos en las líneas tocadas. Un superviviente se mata con un test. Si es
   equivalente o no testeable, se declara con su motivo y su posición exacta (`fichero:línea:col:mutación`),
   y se recoloca si el código se mueve. Un mutante que cuelga y está declarado cuenta como detectado.
5. **QA:** build y suite entera **en todas las plataformas**, sin warnings. Un «0 warnings» incremental no
   vale: `touch` a los ficheros tocados antes de compilar. Un procedimiento manual se convierte en test.
6. **Forma (trinquete):** ficheros ≤ 400 líneas, funciones ≤ 40, comentarios ≤ 15 % y solo el porqué, sin
   ciclos, sin duplicación, sin tipos sin uso (un tipo entra en el commit de su primer uso real).

Las reglas de las puertas no se aflojan para pasar. Un falso positivo se arregla en la puerta, con su test, en
un commit aparte. Scripts de referencia (Python 3 + toolchain de Xcode) en `puertas-swift/`.

**Commits:** un commit, un tipo de cambio; cada uno pasa todas las puertas; el mensaje cuenta el porqué y las
cifras (antes → después, en qué banco). El esquema va en su propio commit con la reversión escrita. Toda ruta de
inferencia lleva su degradación en el mismo commit.

## 2. Decisiones con números

Ninguna decisión sin una cifra medida. Si no hay número, se mide antes de recomendar.

- **Banco antes de tocar:** público y con licencia libre o construido sin etiquetado manual. Reproduce la cifra
  de hoy antes de cambiar nada.
- **Regla de adopción:** gana con el límite inferior del intervalo (bootstrap pareado) por encima de 0, ningún
  subgrupo (lengua, plataforma, tipo de caso) cae más de 2 pp, cero casos buenos rotos y coste igual o menor.
- **Tres jueces cuando hay riesgo de sesgo:** el de desarrollo, uno fresco de un solo uso con la regla escrita
  antes de mirar, y uno humano si existe. Se informa de los tres.
- **Comprueba tus conclusiones:** contaminación (también traducciones en corpus paralelos), que la referencia
  no esté sustituida por una predicción, artefactos de medida, y la máquina ocupada mientras mides.
- Las medidas no son tests: van tras un interruptor y fuera de la suite normal. Lo medido se guarda con su
  `ESTADO.md` (método, cifras, decisión) fuera del repo del producto.

## 3. Estado del arte, siempre

Lo último y lo mejor, demostrado con números, **sin que haya que pedirlo**. Antes de decidir un framework, un
modelo, un formato o una receta:

- **SDK instalado:** diff de `$(xcrun --sdk macosx --show-sdk-path)/System/Library/Frameworks` frente a la lista
  guardada en el repo. Un framework nuevo que toque la tarea se lee en la documentación (Xcode
  DocumentationSearch o `.swiftinterface`) y se mide. Ejemplo real: Core AI (iOS 27) apareció en el SDK y casi
  se ignora.
- **Modelos y métodos:** búsqueda de lo publicado en los últimos meses, con licencia libre y que quepa en la
  máquina y en el dispositivo. Lo nuevo entra al bake-off con el protocolo fijo.
- **Verifica la API contra el SDK instalado**, no contra la memoria ni la web (`grep` en el `.swiftinterface`).
  Las notas de este skill tienen fecha: vuelve a comprobarlas en un SDK nuevo.
- Nunca se da una etapa por cerrada. Si algo nuevo se descarta, se dice por qué con su número.

## 4. Principios de producto

- **La función principal es el producto.** La IA es invisible: sin badges, sin «generado por IA», sin
  parámetros del modelo expuestos.
- **Si la IA falla, la app no falla; la app es completa sin IA.** Cada ruta inferida tiene su degradación
  determinista y probada: el usuario ve un resultado más modesto, nunca un error ni un reintento visible.
- **En el dispositivo y privado:** sin cuenta obligatoria ni analítica remota. Nunca se envían datos del
  usuario (tampoco su email) a servicios ajenos.
- **Nada caro en segundo plano sin pedirlo:** no se pregenera lo que el usuario quizá no abra. La latencia se
  baja dentro de la llamada.
- **Respeta a terceros:** robots.txt, ritmo por host, UA neutro, sin saltar muros de pago de servidor
  (`referencias/red.md`).

## 5. Trabajo con el usuario

- **Responde en su idioma**, también en avisos cortos y resúmenes de informes en otro idioma.
- **Delegado no es silencioso:** decide piezas y commits tú, pero lleva al usuario lo visible, lo irreversible
  y lo que cambia el producto. Lo que hay que borrar se entiende antes de borrarlo.
- **Nunca pidas etiquetado ni revisión manual** como fuente de verdad: bancos públicos, secciones, consensos.
- **Propón tú:** investiga y trae mejoras del pipeline con números; el usuario no debería tener que sugerirlas.
- **Corte de sesión:** tras cada commit verde, reescribe `TRASPASO.md` fuera del repo (plan y paso, último
  commit, lo que queda a medias, siguiente acción, comandos exactos, trampas vistas; ≤ 40 líneas). Una sesión
  nueva empieza leyéndolo, no explorando el repo.

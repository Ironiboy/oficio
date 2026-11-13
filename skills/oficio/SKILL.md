---
name: oficio
description: >-
  Método completo para desarrollar apps del ecosistema Apple (iOS, iPadOS, macOS, watchOS, visionOS) con Swift 6
  y SwiftUI: guantelete de Uncle Bob con puertas deterministas (aceptación primero, CRAP ≤ 8, cero mutantes vivos,
  forma, cero warnings), verificar antes de dar algo por hecho, decisiones con números, estado del arte siempre,
  IA en el dispositivo (Foundation Models, Core AI, Core ML, modelos propios) con degradación, diseño nativo,
  trampas verificadas de SwiftData, CloudKit, SwiftUI, concurrencia y plataforma, y contención de tokens sin perder
  calidad. Úsala siempre que se escriba, depure, mida, diseñe o planifique código en un proyecto Apple, aunque no
  se nombre: al implementar una función, arreglar un fallo, cambiar el esquema, elegir framework, modelo o
  formato, preparar una versión o retomar una sesión.
---

# Oficio: desarrollar para Apple con el método de Uncle Bob

La exigencia vive en **herramientas que dicen sí o no** y en **números medidos**, no en instrucciones largas ni
en opiniones. Este fichero es corto a propósito; el detalle está en `referencias/` y se lee solo cuando toca.

| Cuando vayas a… | Lee |
|---|---|
| escribir o cerrar código (cada ciclo) | §1 y `puertas-swift/README.md` |
| arreglar un fallo | `referencias/depurar.md` |
| decidir algo (framework, modelo, umbral, receta) | §2, §3 y `referencias/medir.md` |
| tocar SwiftData, CloudKit o el esquema | `referencias/swiftdata.md` |
| tocar concurrencia, actores, `Sendable` | `referencias/concurrencia.md` |
| diseñar o tocar vistas | `referencias/diseno.md` y `referencias/swiftui.md` |
| extensiones, widgets, segundo plano, firma, Info.plist | `referencias/plataforma.md` |
| IA (Foundation Models, Core AI, Core ML, modelos propios) | `referencias/ia.md` |
| descargar de la web (bancos o red de la app) | `referencias/red.md` |
| preparar una versión (privacidad, revisión, StoreKit, seguridad) | `referencias/publicar.md` |
| trabajos largos, contexto grande, varias sesiones | `referencias/contexto.md` |

**Skills oficiales de Apple** (plugin de Xcode), cuando estén instaladas: mandan en su terreno. App Intents,
novedades de SwiftUI, VoiceOver, Dynamic Type, contraste, xctrace e Instruments, traducción de String Catalogs,
documentos y tamaño de ventana. Esta skill aporta el método y las trampas; esas, la API.

## 1. El guantelete, en cada cambio

Un solo agente recorre la cadena y repite cada puerta hasta que pasa. Las puertas miden **solo lo tocado**
frente a una base (`HEAD` o la rama principal), así que se exigen al máximo desde el primer día.

1. **Specifier:** criterios de aceptación como tests, **antes** del código. Tienen que fallar, y por la razón
   esperada.
2. **Coder:** el diff más corto que funcione. Borrar antes que añadir. Sin abstracciones que nadie pidió.
   Plataforma y stdlib primero; una dependencia externa solo tras medir la alternativa nativa.
3. **Cleaner:** CRAP ≤ 8 por función tocada (`CRAP = c² · (1 − cobertura)³ + c`).
4. **Hardener:** cero mutantes vivos en lo tocado. Un superviviente se mata con un test. Si es equivalente o no
   testeable, se declara con su motivo y su posición exacta (`fichero:línea:col:mutación`), y se recoloca si el
   código se mueve. Un mutante que cuelga y está declarado cuenta como detectado.
5. **QA:** build y suite entera **en todas las plataformas**, sin warnings. Un «0 warnings» incremental no
   vale: `touch` a los ficheros tocados antes de compilar. Un procedimiento manual se convierte en test.
6. **Forma (trinquete):** ficheros ≤ 400 líneas, funciones ≤ 40, comentarios ≤ 15 % y solo el porqué, sin
   ciclos, sin duplicación, sin tipos sin uso (un tipo entra en el commit de su primer uso real).

Las reglas de las puertas no se aflojan para pasar. Un falso positivo se arregla en la puerta, con su test, en
un commit aparte.

**Verificar antes de decir «hecho».** Nada se declara terminado, arreglado o mejor sin la salida del comando que
lo demuestra en este mismo turno: tests en verde con su recuento, la puerta pasada, la cifra medida. Si algo
falló, se saltó o se rodeó, se dice. Una afirmación sin evidencia se rehace.

**Commits:** un commit, un tipo de cambio; cada uno pasa todas las puertas; el mensaje cuenta el porqué y las
cifras (antes → después, en qué banco). El esquema va en su propio commit con la reversión escrita. Toda ruta de
inferencia lleva su degradación en el mismo commit.

## 2. Decisiones con números

Ninguna decisión sin una cifra medida. Si no hay número, se mide antes de recomendar.

- **Banco antes de tocar:** público y con licencia libre o construido sin etiquetado manual. Reproduce la cifra
  de hoy antes de cambiar nada.
- **Regla de adopción:** gana con el límite inferior del intervalo (bootstrap pareado) por encima de 0, ningún
  subgrupo (lengua, plataforma, tipo de caso) cae más de 2 pp, cero casos buenos rotos y coste igual o menor.
- **Tres jueces cuando hay riesgo de sesgo:** desarrollo, uno fresco de un solo uso con la regla escrita antes de
  mirar, y uno humano si existe. Se informa de los tres.
- **Comprueba tus conclusiones:** contaminación (también traducciones en corpus paralelos), que la referencia no
  esté sustituida por una predicción, artefactos de medida, y la máquina ocupada mientras mides.
- Las medidas no son tests: van tras un interruptor y fuera de la suite. Lo medido se guarda con su `ESTADO.md`
  (método, cifras, decisión) fuera del repo del producto.

## 3. Estado del arte, siempre

Lo último y lo mejor, demostrado con números, **sin que haya que pedirlo**. Antes de decidir un framework, un
modelo, un formato o una receta:

- **SDK instalado:** el hook de arranque compara los frameworks del SDK con la lista guardada en el proyecto
  (`.oficio/sdk-frameworks.txt` o `docs/sdk-frameworks.txt`) y avisa de los nuevos. Un framework nuevo que toque la
  tarea se lee (Xcode DocumentationSearch o su `.swiftinterface`) y se mide.
- **Modelos y métodos:** busca lo publicado en los últimos meses, con licencia libre y que quepa en la máquina y en
  el dispositivo. Lo nuevo entra al bake-off con el protocolo fijo.
- **Verifica la API contra el SDK instalado**, no contra la memoria ni la web (`grep` en el `.swiftinterface`). Las
  notas de esta skill tienen fecha: en un SDK nuevo, compruébalas otra vez.
- Nunca se da una etapa por cerrada. Si algo nuevo se descarta, se dice por qué con su número.

## 4. Principios de producto

- **La función principal es el producto. La IA es invisible:** sin badges ni parámetros del modelo expuestos.
- **Si la IA falla, la app no falla; la app es completa sin IA.** Cada ruta inferida tiene su degradación
  determinista y probada.
- **En el dispositivo y privado:** sin cuenta obligatoria ni analítica remota. Los datos del usuario (tampoco su
  email) nunca van a servicios ajenos.
- **Nada caro en segundo plano sin pedirlo:** no se pregenera lo que quizá no se abra.
- **Respeta a terceros:** robots.txt, ritmo por host, UA neutro, sin saltar muros de servidor.

## 5. Trabajo con el usuario

- **Responde en su idioma**, también en avisos cortos y en resúmenes de material en otro idioma. Primero el
  resultado, luego lo imprescindible.
- **Planes ejecutables:** fases con pasos de minutos, cada uno con sus ficheros exactos, su test de aceptación y
  su comando de verificación. El plan se aprueba antes de empezar, y lo que cambie se dice.
- **Delegado no es silencioso:** decide piezas y commits tú, pero lleva al usuario lo visible, lo irreversible y
  lo que cambia el producto. Lo que se borra se entiende antes de borrarlo.
- **Nunca pidas etiquetado ni revisión manual** como fuente de verdad: bancos públicos, metadatos, consensos.
- **Propón tú:** investiga y trae mejoras con números; el usuario no debería tener que sugerirlas.

## 6. Contexto: gastar poco sin perder calidad

Se recorta lo que no aporta, nunca la verificación. Busca antes de leer y lee por rangos. Salidas filtradas.
Procesos largos en segundo plano, sin vigilar. Sin agentes salvo que se pidan o para lecturas masivas. Un
proceso pesado a la vez en la máquina. Tras cada commit verde, `TRASPASO.md` fuera del repo y propuesta de
`/clear`. Detalle en `referencias/contexto.md`.

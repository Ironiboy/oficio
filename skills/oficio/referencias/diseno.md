# Diseño: nativo, sobrio y medible

## Sistema

- **Tipografía del sistema con Dynamic Type completo** en la interfaz. La de lectura o contenido, aparte y
  configurable.
- **Color semántico**, derivado del tema. Ningún color literal en las vistas (tampoco `.white` en la pantalla de
  bloqueo o en las Live Activities).
- **Espaciado en una escala** (4 pt) con tokens; los márgenes de contenido son un token propio.
- **Movimiento:** toda transición respeta `accessibilityReduceMotion`. Duraciones cortas (~0,25 s).
- **Liquid Glass solo en la navegación**, nunca en el contenido ni en las tarjetas.

## Principios

- **El contenido manda; el cromo se retira.** Si una barra ocupa la franja que el contenido necesita, sobra. Un
  dato repetido y truncado arriba (el título en la barra) también.
- **Los controles van en las esquinas, no en barras**, y solo los que se usan *durante* la tarea están a mano.
  El resto va en un menú.
- **Lo que el usuario necesita antes de decidir va dentro de la página**, no en una hoja que se invoca, y llega
  preparado («que ya estuviera ahí» decide si se usa). Aun así, nunca se pregenera en segundo plano lo que quizá
  no abra.
- **La IA no se ve:** sin badges ni avisos de generación. Si falla, la vista se pliega o muestra la versión
  determinista sin decir nada.
- **Menos es más en el texto generado:** pocas claves, la más importante primero, todas a la vista. Si un
  formato «más rico» se mide peor, no entra.
- **Referentes antes de diseñar:** estudia la mejor app de la categoría (Reeder, GoodLinks, Fotos…) y mide
  antes de diseñar lo que depende de datos. Una portada de historias no se diseña sin saber cuántas salen.
- **Nombres comerciales fuera de la app** (web, App Store); dentro, la función se explica sola.

## Accesibilidad (puertas, no deseos)

- VoiceOver: toda acción con etiqueta legible, rasgos correctos, imágenes decorativas ocultas.
- Dynamic Type hasta los tamaños de accesibilidad, con el layout adaptado y no recortado.
- Contraste WCAG 2.1 AA en claro y oscuro.
- Usa las skills de auditoría de accesibilidad de Xcode cuando existan, y convierte cada hallazgo en un test o
  en un caso de QA ejecutable.

## Primer arranque

- Pantallas breves que enseñan el uso real, no promesas.
- Si hacen falta recursos que no vienen instalados (modelos de NER por idioma, modelos propios), una pantalla de
  carga con progreso honesto; la app funciona mientras tanto.

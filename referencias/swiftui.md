# SwiftUI: trampas verificadas (SDK 27)

- **`navigationDestination(item:)` usa la clausura de la última evaluación del `body`.** Si el destino necesita
  dos datos y solo uno viaja en el `item`, el otro llega viejo («funciona a la segunda»). Mete todo lo que el
  destino necesita en el propio `item`, un struct `Hashable`.
- **Identidad en listas:** nada de `id: \.self` sobre valores que cambian, ni índices, ni filtros u ordenaciones
  dentro del `ForEach`; la colección llega ya preparada. Una fila es una vista, no `AnyView`.
- **`@Observable` e invalidación:** lee en el `body` solo lo que pinta. Un valor que cambia muy a menudo
  (progreso, scroll) vive en una vista hoja, no en la raíz.
- **Liquid Glass (iOS 26–27):** el cristal es solo para la capa de navegación (tab bar, toolbar, botones
  flotantes), nunca sobre el contenido. Es automático al compilar contra el SDK. Antes de usar un modificador de
  cristal, compruébalo en el `.swiftinterface`: en el SDK 27 no había `.glassEffect()` sobre vistas propias.
- **`Tab(role: .search)` sí separa la lupa en iPhone.** Si la búsqueda es una pantalla propia, añade
  `.tabViewSearchActivation(.searchTabSelection)`.
- **`.textSelection` puede tapar menús contextuales** de bloques en macOS; pruébalo en las dos plataformas.
- **Localización:** usa `LocalizedStringResource` en las API y el bundle correcto en los paquetes (`.module`);
  los menús en inglés en una app en castellano son un bundle mal pasado.
- **Restaura la posición por identificador de bloque, no por offset:** el offset se invalida con Dynamic Type
  o al girar.
- **Mide fps en el dispositivo**, no en el simulador (un lector a 24–36 fps pasó a 84 fps y cero tirones con
  renderizado perezoso por bloque).

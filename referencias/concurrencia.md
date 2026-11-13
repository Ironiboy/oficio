# Swift 6: concurrencia estricta

- **Concurrencia estricta activada desde el primer commit**, y cada commit compila sin warnings.
- **`@unchecked Sendable` solo con justificación pegada:** un doc-comment sobre el tipo que diga por qué tiene
  que cruzar, y dentro un comentario que acote por qué es seguro (candado, inmutable tras `init`…).
- **Aislamiento explícito por `ModelContext`:** un contexto por actor (`@ModelActor`). Entre actores viajan
  `PersistentIdentifier` y valores, nunca modelos.
- **MainActor por defecto (`SWIFT_DEFAULT_ACTOR_ISOLATION`):** un tipo sin anotar vive en el hilo principal.
  Un parser de 2 MB bloqueaba la UI 0,9 s. El trabajo pesado va en tipos `nonisolated` con puntos de entrada
  `@concurrent`. Con la concurrencia accesible, un `async` `nonisolated` hereda el ejecutor del llamante; solo
  `@concurrent` garantiza salir del principal.
- **Las conformidades heredan el aislamiento:** un `struct` sin anotar que conforma `ActivityAttributes` (u otro
  protocolo `nonisolated`) queda aislado al MainActor y no se puede usar desde tareas concurrentes. Márcalo
  `nonisolated`. Lo mismo con las implementaciones por defecto en extensiones de protocolo.
- Un SDK nuevo suele aflorar errores de aislamiento latentes. Compila contra el SDK real antes de dar nada por
  terminado.
- **Cancelación:** mírala en los bucles largos con una cadencia fija (cada N iteraciones o cada M unidades de
  trabajo) y pruébala con una tarea que se cancela a sí misma antes de empezar
  (`withUnsafeCurrentTask { $0?.cancel() }`), no con carreras de tiempo.
- **Tests y paralelismo:** Swift Testing paraleliza dentro del proceso. `.serialized` no se propaga a suites
  anidadas por `extension`, y `parallelizable: false` del test plan solo afecta a XCTest. Lo que comparte
  estado global (CoreData, singletons) se aísla de verdad o va a un proceso aparte.
- Un test frágil bajo carga es un bug del test: no exijas tiempos ni tamaños de lote exactos cuando el código
  vacía por tiempo.
- `precondition` se prueba con exit tests: `#expect(processExitsWith: .failure) { … }`.

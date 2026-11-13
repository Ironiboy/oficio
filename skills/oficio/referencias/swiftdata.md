# SwiftData y CloudKit: trampas verificadas

Verificado en el SDK 27 (jul–nov 2026). Muchas **no fallan: matan el proceso** con una excepción de Objective-C
que `try` no captura. En los tests se ven como «0 tests… TEST FAILED», con el host de tests muerto. La pista
está en el log («Restarting after unexpected exit») y en el `.ips` de `~/Library/Logs/DiagnosticReports`.

## Esquema

- **`#Index` sobre un enum aborta** al construir el `ModelContainer` («composite property»). Persiste el bruto
  (`stateRaw: String`), indexa ese, y deja el enum como propiedad calculada. Centraliza los `#Predicate` sobre el
  bruto en un solo tipo de consultas.
- **`#Predicate` sobre un enum a través de una relación** (`$0.classification?.topic == x`) aborta con «keypath
  … not found». Filtra en memoria, dentro de un `@ModelActor`, y pasa a la vista solo `PersistentIdentifier` y
  cifras.
- **Codable + RawRepresentable en el mismo tipo** (para `@AppStorage`) se recursa hasta desbordar la pila: el
  `encode(to:)` de la stdlib vía `rawValue` gana a la síntesis. Usa un tipo envoltorio o codifica a mano.
- Toda migración lleva su reversión documentada **antes** de escribir código. `deleteRule: .cascade` para lo
  que depende del padre.

## CloudKit

- **Basta con tener el entitlement de iCloud** para que SwiftData valide el esquema para CloudKit, aunque la
  configuración sea local. Exige: todas las relaciones a-muchos opcionales (`[X]?`), nada de muchos-a-muchos,
  nada de `#Unique`. Diseña así desde el primer día; los accesores `allX` absorben el `nil`.
- **`ModelConfiguration` trae `cloudKitDatabase: .automatic` por defecto, también en memoria.** En tests y
  previews pasa `.none` explícito, o el primer `save()` aborta sin cuenta de iCloud.
- Un registro llega antes que aquello con lo que se relaciona: **no cuentes filas de hijos**, cuenta padres que
  tienen hijo.
- Hace falta `UIBackgroundModes: remote-notification` en un `Info.plist` real (Xcode no lo genera desde
  `INFOPLIST_KEY_`), o lo de otro dispositivo no baja hasta abrir la app.

## Concurrencia de contextos

- **Varios `ModelContainer` en memoria creados a la vez corrompen CoreData** (SIGSEGV o igualdades falsas en
  tipos ajenos). Un contenedor como en producción; en el paquete, uno en disco aislado por test. Instanciar
  `@Model` en paralelo también corre contra la resolución de conformidades.
- **Hijo a-uno borrado por otro contexto:** la primera lectura de su propiedad aborta. `isDeleted` y
  `modelContext` no avisan. La cura es un `fetch` del padre por `persistentModelID`. Un escritor de fondo
  **actualiza el hijo en su sitio**, nunca lo borra y lo recrea.
- `FetchDescriptor.includePendingChanges` (por defecto `true`) es incompatible con `fetch(_:batchSize:)`. Con un
  `try?` delante, la lista sale vacía en silencio.

## Rendimiento

- **Mide el coste por guardado del store en el hilo principal**, no solo el trabajo del lote. Un `@Query` sin
  predicado ni tope con el filtro en el `body` costaba 200 ms por guardado con 5.000 filas; por lotes, 6 ms.
  Multiplicado por 11 guardados por elemento, congela la app. Reprodúcelo con datos sembrados **y** la ingesta
  simulada a la vez.
- Agrupa los guardados: uno por unidad de trabajo, no uno por imagen o subpaso.
- El guardado no espera al enriquecimiento (IA, imágenes): primero se guarda, luego se enriquece.

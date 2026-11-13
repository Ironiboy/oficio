# Plataforma: build, firma, extensiones y segundo plano

## Dónde vive el código

- **Nunca en iCloud Drive** (`~/Library/Mobile Documents`). El file provider cuelga `xcodebuild` antes de la
  primera línea (`NSFileCoordinator`), rompe la firma con `.build` dentro y revierte borrados horas después. Ni
  `.nosync` ni matar `bird` lo arreglan. Usa `~/Developer/<Proyecto>`.
- Las medidas, los bancos y los modelos van fuera del repo del producto (`~/Developer/<Proyecto>-bench`).

## Build y estilo

- Comandos exactos de build y test en una skill del proyecto (`build-and-test`): esquemas, destinos,
  `-derivedDataPath`, filtros.
- **Un formateador sin configuración reformatea el fichero entero** (swift-format usa 2 espacios). O se pone su
  configuración con el estilo del proyecto y un commit de formato aparte, o se indenta a mano como el fichero de
  al lado.
- `CODE_SIGNING_ALLOWED=NO` no embebe entitlements: los App Groups fallan («client is not entitled»). Las
  pruebas de extremo a extremo se hacen con un build firmado.

## Extensiones y widgets

- Comprueba que la fase «Embed Foundation Extensions» contiene las `.appex` tras tocar frameworks del target; una
  vez se vació sola y desaparecieron widgets, Live Activity y hoja de compartir.
- Cada extensión necesita su `CODE_SIGN_ENTITLEMENTS` apuntando al fichero; tener el `.entitlements` no basta.
- Las Live Activities necesitan actualizarse en cada fase y terminar al final del trabajo, no antes.

## Segundo plano (BGTaskScheduler)

- **Encolar sin manejador registrado mata la app** (solo en el dispositivo, no en el simulador). Encola solo si
  `register` devolvió `true`.
- Fallos silenciosos: el identificador no coincide con `BGTaskSchedulerPermittedIdentifiers`, falta `processing`
  en `UIBackgroundModes`, o se registra pero nunca se encola. Compruébalo en el dispositivo con
  `pendingTaskRequests()`.
- `requiresExternalPower = true` desactiva el CPU Monitor. Con batería, el sistema puede no programarla nunca.
- **Térmica:** en `.serious` los modelos del sistema no devuelven peores resultados, no devuelven ninguno. El
  trabajo de IA se aborta antes, y las medidas esperan a que el dispositivo se enfríe.

## Simulador frente a dispositivo

- El simulador no trae los modelos del dispositivo: `NLTagger` sin NER, Foundation Models sin inferencia. Los
  tests toleran el vacío allí y comprueban lo sustantivo donde el modelo existe (macOS o dispositivo).
- Rendimiento, térmica, segundo plano y fps se miden en el dispositivo.

## API con disponibilidad cambiante

- Una API nueva (p. ej. iOS 27) con un objetivo mínimo menor (iOS 26) va con `#available` y la ruta antigua
  envuelta en una función `@available(iOS, deprecated: 27.0)`, para que no genere warning.

# Puertas del guantelete

Dos puertas deterministas sobre lo que cambia en `<Paquete>/Sources` respecto a un commit base
(diff contra el árbol de trabajo, más los `.swift` sin trackear). Solo `python3` del sistema y el
toolchain de Xcode; ponen `DEVELOPER_DIR` ellas mismas. La base es obligatoria, y las dos salen
con ≠0 si no hay nada tocado o si `swift test` no ejecutó ningún test (un `--filter` que no casa
sale con 0 en SwiftPM: «No matching test cases were run»).

**Montaje en un proyecto:** copia esta carpeta a `scripts/gates/` del repo y define el paquete:
`export OFICIO_PKG=MiAppKit` (por defecto `.`, el repo es el paquete). `forma` mide además las carpetas de
`OFICIO_FUENTES` (separadas por comas; por defecto `<Paquete>/Sources`). Guarda la base de forma con
`scripts/gates/forma --update` y comprueba con `--check`.

```bash
scripts/gates/crap HEAD~1 --filter MiModuloTests                  # --max 8 por defecto
scripts/gates/mutants HEAD~1 --filter MiModuloTests
python3 -m unittest scripts/gates/test_gates.py                    # la lógica de las puertas
```

**`crap`** — corre `swift test --enable-code-coverage` (con `--filter` si se da), exporta la
cobertura con `xcrun llvm-cov export` de todos los `.xctest`, y para cada función que solapa una
línea cambiada calcula CRAP = c² × (1 − cob)³ + c. Sale con 1 si alguna pasa de `--max`, si los
tests fallan, o si un fichero tiene líneas tocadas sin ninguna función medida (típico: un
`#if os(iOS)`, que en macOS no se compila; o un cambio solo en declaraciones). Ese caso se revisa
y, si procede, se acepta con `--allow-uncovered <Paquete>/Sources/…/X.swift` (repetible).

**`mutants`** — sobre las líneas añadidas o cambiadas genera mutantes uno a uno (`==`↔`!=`,
`<`↔`>=`, `>`↔`<=`, y de frontera `>=`↔`>`, `<=`↔`<`, `&&`↔`||`, `true`↔`false`, `+`↔`-`, condición de `if`/`guard` negada, borrado
de una llamada sin valor), solo en los ficheros bajo `--only <ruta>` si se da (repetible). Cada uno: `swift build --build-tests` y `swift test --filter`. Si no
compila cuenta aparte como muerto por compilación; si pasa del tiempo límite (10× la pasada base +
60 s) queda **sin veredicto** y la puerta falla. El fichero se escribe y se restaura con temporal +
`os.replace`, siempre (también con Ctrl-C o SIGTERM), y al final se comprueba que `git status`/
`git diff` siguen iguales. Si el proceso muere sin restaurar (SIGKILL), el original queda en
`.build/gates-mutant.orig`: el siguiente arranque lo restaura y se para avisando.

Sale con 1 si sobrevive alguno que no esté en `equivalent-mutants.txt` (la columna es la que
imprime la puerta; el motivo es obligatorio). Un mutante que **cuelga** los tests (una espera que
nunca se reanuda) también se declara ahí, con un motivo que diga que cuelga: no terminar es
detectarlo, pero la puerta no distingue colgar de tardar.

```
MiAppKit/Sources/Core/X.swift:42:17:==->!=  # motivo obligatorio
```

**No lo ejecutes en paralelo ni edites ficheros del paquete mientras corre `mutants`**: escribe
sobre los fuentes de verdad, y al restaurar pisaría lo que hayas editado.

## Límites conocidos

- **Solo el paquete.** El target de app (`xcodebuild`, sus tests) queda fuera.
- **Complejidad léxica, no sintáctica.** Cuenta palabras clave y operadores tras quitar
  comentarios y cadenas; no entiende interpolaciones con comillas dentro ni cadenas raw con `#`.
  Un `case` de un `enum` anidado en la función cuenta como decisión, y un ternario sin espacios
  (`a?b:c`) no cuenta.
  Una función que contiene closures cuenta también sus decisiones (y las closures salen aparte).
- **Mutantes de una línea.** Condiciones partidas en varias líneas no se niegan; `if let`/`case`
  no se niegan; borrar la expresión de un `return` implícito sale como muerto por compilación.
- **«Sin medir» es por fichero.** Una línea tocada dentro de un `#if os(iOS)` en un fichero que
  tiene otras funciones tocadas y medidas pasa sin aviso.
- `--filter` decide qué tests cuentan: una función cubierta solo por otro target sale al 0 %.

**`forma`** — la belleza en cifras (ADR 0007): ficheros > 400 líneas, funciones > 40 (por llaves,
sin contar comentarios ni literales; la firma puede ocupar varias líneas), comentario por
módulo > 15 %, tipos cuyo nombre solo aparece en su declaración, ficheros de un módulo que se
usan en círculo y líneas dentro de un bloque de 6 líneas de código repetido. Sin argumentos
informa; `--check` es un
trinquete contra `forma-base.json` (lo que incumple puede mejorar, nunca empeorar; lo que cumple no
puede romperse); `--update` fija la base. Pruebas: `python3 -m unittest scripts/gates/test_forma.py`.

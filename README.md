# oficio

[![tests](https://github.com/Ironiboy/oficio/actions/workflows/tests.yml/badge.svg)](https://github.com/Ironiboy/oficio/actions/workflows/tests.yml)

Una skill de [Claude Code](https://claude.com/claude-code) para desarrollar apps del ecosistema Apple (iOS,
iPadOS, macOS, watchOS, visionOS) con oficio: el guantelete de Uncle Bob con puertas deterministas, decisiones
con números, el estado del arte siempre y la contención de tokens sin perder calidad.

Nace de un proyecto real: una app de lectura con IA en el dispositivo, escrita en Swift 6 y SwiftUI sobre el
SDK 27. Cada regla viene de algo que costó tiempo, y cada trampa está verificada contra el SDK instalado y
fechada.

## Qué trae

| Pieza | Qué hace |
|---|---|
| `skills/oficio/SKILL.md` | El método, corto a propósito: el guantelete (aceptación primero, CRAP ≤ 8, cero mutantes vivos, forma, cero warnings), verificar antes de decir «hecho», decisiones con números, estado del arte, principios de producto y contexto. |
| `skills/oficio/referencias/` | El detalle, que se lee solo cuando toca: depurar, medir, SwiftData y CloudKit, concurrencia, SwiftUI, diseño, plataforma, IA en el dispositivo, red, publicar y contexto. |
| `skills/oficio/puertas-swift/` | Las puertas en Python 3 más el toolchain de Xcode (`crap`, `mutants`, `forma`), con sus tests. |
| `hooks/arranque.sh` | Al empezar, tras `/clear` y al compactar, recuerda lo esencial en cuatro líneas y avisa de los frameworks nuevos del SDK instalado. |
| `evals/` | Tareas con expectativas y consultas de activación, en el formato del skill-creator de Anthropic. |
| `tests/` | La skill se prueba a sí misma: rutas, tamaños, manifiestos, hook y evals. |

## Instalación

Como plugin, que trae la skill y el hook:

```
/plugin marketplace add Ironiboy/oficio
/plugin install oficio@oficio
```

Solo la skill, sin el hook:

```bash
git clone https://github.com/Ironiboy/oficio ~/Developer/oficio
ln -s ~/Developer/oficio/skills/oficio ~/.claude/skills/oficio
```

En cada proyecto:

1. **Lista de frameworks del SDK**, para que el hook avise de los nuevos:
   ```bash
   mkdir -p .oficio && ls "$(xcrun --sdk macosx --show-sdk-path)/System/Library/Frameworks" | sed 's/.framework//' > .oficio/sdk-frameworks.txt
   ```
2. **Puertas:** copia `skills/oficio/puertas-swift/` a `scripts/gates/` y define `OFICIO_PKG`
   (ver su `README.md`).

## Medir la skill

Con el [skill-creator](https://github.com/anthropics/skills) de Anthropic:
- **Tareas:** se ejecuta `evals/evals.json` con la skill y sin ella, y se puntúan las expectativas.
- **Activación:** `scripts.run_loop` sobre `evals/disparo.json` mide si se activa cuando debe y afina la
  descripción.

## Estado

Las notas de API están verificadas en el SDK 27.2 (noviembre de 2026). En un SDK nuevo, vuelve a comprobarlas:
la propia skill lo exige.

## Licencia

MIT.

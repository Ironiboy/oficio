# oficio

Una skill de [Claude Code](https://claude.com/claude-code) para desarrollar apps del ecosistema Apple (iOS,
iPadOS, macOS, watchOS, visionOS) con oficio: el guantelete de Uncle Bob con puertas deterministas, decisiones
con números y el estado del arte siempre.

Nace de un proyecto real (una app de lectura con IA en el dispositivo, Swift 6 y SwiftUI sobre el SDK 27).
Cada regla viene de algo que costó tiempo, y cada trampa está verificada contra el SDK instalado y fechada.

## Qué trae

- **`SKILL.md`**: el método, corto a propósito. Incluye el guantelete (aceptación primero, CRAP ≤ 8, cero
  mutantes vivos, forma, cero warnings), las decisiones con números, el estado del arte, los principios de
  producto y la forma de trabajar.
- **`referencias/`**: el detalle, que se lee solo cuando toca. Cubre SwiftData y CloudKit, concurrencia,
  SwiftUI, diseño y accesibilidad, plataforma (firma, extensiones, segundo plano), IA en el dispositivo
  (Foundation Models, Core AI, Core ML, modelos propios), medida, red y economía de tokens y de máquina.
- **`puertas-swift/`**: las puertas en Python 3 de sistema más el toolchain de Xcode (`crap`, `mutants`,
  `forma`), con sus tests.

## Instalación

```bash
git clone https://github.com/Ironiboy/oficio ~/.claude/skills/oficio
```

Para las puertas en un proyecto, copia `puertas-swift/` a `scripts/gates/` del repo y define
`OFICIO_PKG` (ver `puertas-swift/README.md`).

## Estado

Las notas de API están verificadas en el SDK 27.2 (noviembre de 2026). En un SDK nuevo, vuelve a comprobarlas:
la propia skill lo exige.

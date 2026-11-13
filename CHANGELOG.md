# Cambios

## 1.1.0 — 2026-11-13

- **Plugin de Claude Code** (`.claude-plugin/`), con marketplace propio y licencia MIT.
- **Hook de arranque** (`hooks/arranque.sh`) al empezar, tras `/clear` y al compactar: lo esencial del método en
  cuatro líneas y los frameworks del SDK instalado que no estaban en la lista guardada del proyecto.
- **Verificar antes de decir «hecho»** y **planes ejecutables** en el método.
- Referencias nuevas: `contexto.md` (tokens sin perder calidad; sustituye a `economia.md`), `depurar.md` y
  `publicar.md`. Envío a las skills oficiales de Apple en su terreno.
- **Evals** (`evals/evals.json`, 6 tareas con expectativas; `evals/disparo.json`, 20 consultas de activación) en
  el formato del skill-creator de Anthropic.
- **La skill se prueba a sí misma** (`tests/test_skill.py`): rutas citadas, referencias sin huérfanas y a un
  nivel, tamaño de lo que se carga siempre, manifiestos, hook y evals; CI en GitHub Actions.
- Descripción reescrita para que se active en cualquier trabajo de código Apple, aunque no se nombre.

## 1.0.0 — 2026-11-13

- Primera versión: método (guantelete de Uncle Bob, decisiones con números, estado del arte), 9 referencias y
  puertas Swift configurables (`OFICIO_PKG`, `OFICIO_FUENTES`).

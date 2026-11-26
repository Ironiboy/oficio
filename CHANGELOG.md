# Cambios

## 1.4.0 — 2026-11-26

- **Ambición** (`referencias/ambicion.md`, §3): la facilidad de implementación del agente no es un criterio. Al adoptar
  un método publicado se implementa la variante que el artículo da por mejor; lo simple, solo como ablación al lado.
  Antes de cada cola: barrido con fecha (tres búsquedas, por método, modelo y datos), tabla de palancas, elección
  anidada, auditoría de la receta heredada (pasos efectivos, contaminación por id y texto, vistas, coste) y la pregunta
  «¿qué dejo fuera porque me da más trabajo?». Lista de destilación de modelos propios (nov-2026).
- `medir.md`: cruce de ids y textos entre conjuntos y pasos efectivos comparables antes de entrenar.

## 1.3.0 — 2026-11-24

- **Barrido de frontera** y **¿hay un camino más corto?** en el estado del arte: buscar lo publicado en los últimos
  meses que resuelva la etapa de otra forma, no solo variantes del enfoque actual (los modelos de decisión
  «System 1» salieron tras el corte y solo se ven buscando).
- **Oro roto** en las trampas de medida: triangular con fuentes humanas independientes antes de decidir.

## 1.2.0 — 2026-11-23

Tres principios de [unclebob/ub-mode](https://github.com/unclebob/ub-mode) que el método no tenía:
- **Funciones gemelas** en la puerta `forma`: misma forma con los nombres locales y los números neutralizados,
  parecido ≥ 0,8 (la idea de unclebob/dryer, que no soporta Swift). Con base y trinquete, como el resto.
- **Ataca la premisa** (`referencias/medir.md`) y **tira el test que pasaría vacío** (Specifier).
- **Limpieza de worktrees** (`referencias/contexto.md`).

## 1.1.1 — 2026-11-13

- README en inglés y más cercano; historial sin datos de la máquina (correo anónimo de GitHub).

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

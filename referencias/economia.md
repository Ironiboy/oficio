# Economía de tokens y de máquina

## Tokens

- **Sin agentes salvo que el usuario los pida.** Cada uno arranca en frío y paga otra vez el contexto. Una
  puerta mide; un revisor opina.
- Si hay que delegar: investigación y recuentos a modelos pequeños; prompts cortos que apuntan a ficheros en vez
  de copiar contexto.
- **Salida filtrada** (`grep`, `tail`, `cut`), nunca logs enteros. Ficheros por rangos; no releas lo que ya está
  en contexto.
- **Procesos largos en segundo plano**, sin quedarse mirando: el aviso de fin despierta. Nada de `sleep` en
  bucle.
- **Secuencia lo que puede volverse innecesario:** antes de una tarea cara, mira si otra en curso la invalida.
- **Corte de sesión** tras cada commit verde, con `TRASPASO.md`.

## Máquina (16 GB)

- **Un proceso pesado a la vez:** un LLM, un entrenamiento o una batería de mutantes. Juntos llenan la memoria y
  el sistema mata procesos de fondo. Encadénalos en serie.
- **El usuario también usa la máquina:** si va a ver vídeo o a trabajar, baja el lote (con acumulación de
  gradiente la receta no cambia) o pausa. Guarda puntos de control cada N pasos para retomar sin perder nada.
- **Disco:** compruébalo antes de convertir, descargar o entrenar. Los puntos de control y las conversiones
  temporales ocupan varios GB. Borra lo descartado con número (modelos perdedores, cachés públicas ya usadas),
  nunca lo que no entiendes.
- **Mutantes:** en una copia aparte del repo (worktree) sin tocarla mientras corren, con tiempo límite y matando
  los ayudantes de test huérfanos al cortar un mutante.
- **No compiles ni midas dos cosas a la vez mientras se mide tiempo.**

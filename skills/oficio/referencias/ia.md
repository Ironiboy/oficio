# IA en el dispositivo

## Reglas

- **Toda llamada a un modelo tiene fallback** determinista en el mismo commit (resumen extractivo, «sin
  categoría», reintento único a las 24 h). Sin badge, sin error visible.
- **Prompts versionados:** no se cambia un prompt sin subir su versión (que invalida la caché) y sin evaluación
  comparativa contra la versión anterior.
- **Caché por clave de versión** (modelo, prompt, texto de entrada): un cambio de cualquiera reprocesa solo lo
  afectado.
- **Lenguas:** solo las que soporta el modelo del sistema. Fuera de ellas, la función se omite, no se inventa.
- **Un modelo grande cargado a la vez** en máquinas de 16 GB.

## Elegir dónde corre (verificado SDK 27, nov-2026; vuelve a comprobarlo)

| Opción | Cuándo |
|---|---|
| Foundation Models (sistema) | generación, extracción guiada, razonamiento corto; sin coste de tamaño |
| Natural Language | idioma, tokenización, lemas, NER (con modelos por idioma que pueden no venir instalados) |
| **Core AI** (iOS/macOS 27, `.aimodel` vía `coreai-torch`) | modelos propios con arquitecturas modernas; medido: CPU 9× más rápido que Core ML, paridad mejor |
| Core ML (`.mlmodelc`) | respaldo para objetivos anteriores a 27; Neural Engine muy afinado |
| MLX | entrenar y evaluar en el Mac; en la app es una dependencia externa |

- **Mide cada formato** en el Neural Engine, la GPU y la CPU: latencia por ventana, primera carga (la
  compilación para el ANE tarda 20–25 s y pide unos 650 MB la primera vez; luego queda en caché entre procesos
  hasta que el modelo se recopia), pico de memoria y paridad (coseno y top-1 frente a la referencia). Nunca
  midas con otro trabajo pesado en la máquina.
- **Prepara el modelo pronto** (al pasar la app a activa, con prioridad baja) para que la primera consulta no
  pague la compilación.
- INT8 por pesos y vocabulario recortado a lo que se usa: medido con −50 % de tamaño y la misma paridad de top-1.

## Modelos propios: el motor que evoluciona

Lo que dura no es el modelo, sino el motor que produce etiquetas, el que entrena y el que mide.

1. **Almacén de etiquetas** fuera del repo: una columna por fuente versionada (sección o metadato, cada LLM
   maestro con su `modelo|prompt|plantilla`, clasificadores especializados en su propio espacio de etiquetas) y
   la huella del texto. Una fuente nueva es una columna nueva; no se rehace nada.
2. **Bake-off permanente de maestros:** todo modelo abierto que quepa en la máquina entra cuando sale, con el
   mismo protocolo.
3. **Combinar fuentes con Dawid-Skene** (EM sin oro, matriz de confusión por fuente). En voto blando ganó a la
   mejor fuente sola: +2,3 contra secciones y +6,7 contra anotación humana. Más fuentes no siempre suman: las
   débiles restaron con etiquetas humanas. Valídalo como un maestro más.
4. **El oro humano nunca se sustituye por el maestro.** Haberlo hecho en 1.091 filas costó 4,8 puntos en el juez
   humano.
5. **Alumno único**, con su calibración por lengua, guardando todas las probabilidades y su vector, para aplicar
   umbrales, cabezas nuevas y personalización sin recalcular.
6. **Validación del alumno contra el ruido:** la validación interna contra metadatos ruidosos premia al modelo
   que imita el ruido; el veredicto lo da el juez fresco o el humano.

## Licencias en cadena

Un modelo entrenado con etiquetas de otro hereda preguntas de licencia (CC BY-SA, salidas de modelos
comerciales). Revísalo antes de que llegue a la app, y acredita todo recurso en la pantalla de créditos, con un
test que lo exija.

# Red: descargar con educación

## Para bancos y medidas

- **robots.txt y Crawl-delay**, como mucho 1 petición/s por host, **UA neutro y fijo** (p. ej. `Proyecto/0.1
  (offline evaluation)`), sin reintentos en bucle, una pasada al día como mucho a sitios que limitan.
- **Nunca cambies de User-Agent ni de huella para esquivar un límite.** Un 429 se respeta y se reintenta otro
  día, en una sola pasada.
- Todo fuera del repo, y **nunca para entrenamiento** si la regla del banco dice solo medir.
- Comprueba el disco antes de una descarga grande y para por debajo de un umbral.

## En la app

- **Concurrencia por sitio** (≈ 4, también en HTTP/2): con ráfagas, algunos CDN devuelven 200 con el cuerpo
  «(null)». Un 200 sin `<` es transitorio, no «contenido insuficiente» permanente.
- **Muros de pago:** se muestra el texto que viene en el HTML aunque esté oculto por CSS (como Safari o Pocket);
  **nunca se saltan muros de servidor**.
- **Enlaces muertos:** la copia pública de archive.org, con su ritmo. Los agregadores (Menéame…) se siguen hasta
  el original. Para social y vídeo, se abre la web.
- Separa los errores transitorios de los permanentes, con prueba de cada uno.

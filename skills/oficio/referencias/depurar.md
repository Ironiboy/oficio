# Depurar: de síntoma a causa, con pruebas

Nada de arreglos a ciegas. Cada paso deja evidencia.

1. **Reproduce de forma determinista.** Un test o una sonda que falla siempre. Si solo falla a veces, busca la
   variable (carga en paralelo, tamaño de los datos, orden de los tests, térmica) hasta que falle siempre.
2. **Separa las etapas.** Localiza en qué capa nace el fallo antes de mirar dentro: descarga o extracción, datos o
   vista, modelo o prompt. Reproduce cada etapa con el mismo cliente o los mismos datos que producción.
3. **Lee la señal entera:**
   - «0 tests… TEST FAILED» con la lista vacía es el host de tests muerto, no un test que falla. Busca
     «Restarting after unexpected exit» y el `.ips` en `~/Library/Logs/DiagnosticReports`; la pila dice dónde.
   - Un `catch` que no imprime en un crash: escribe el error a un fichero temporal y léelo del contenedor.
   - Un congelamiento que depende del tamaño de la biblioteca y no del lote es coste por guardado en el hilo
     principal, no el parseo.
4. **Hipótesis con evidencia:** escríbelas, y descarta cada una con una prueba, no con un razonamiento.
   Bisección (`git bisect`, quitar mitades) cuando no hay hipótesis.
5. **Una sonda por escenario y un proceso por escenario** cuando el fallo mata el proceso: así un aborto no se
   lleva por delante al resto.
6. **Arregla la causa, no el síntoma.** Un candado alrededor de algo que corrompe no lo arregla si el trabajo de
   fondo se escapa del candado.
7. **Test de regresión que falla antes del arreglo** y pasa después. Busca las otras instancias del mismo patrón
   en el código.
8. **Anota la trampa** (referencia de la skill o memoria del proyecto) con el síntoma exacto, la causa y la
   cura, fechada y verificada. Lo que costó una hora no debe costar otra.

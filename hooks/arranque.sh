#!/bin/sh
# Arranque de sesión de oficio: lo esencial que no debe perderse tras /clear o al compactar, y los frameworks
# del SDK instalado que no estaban en la lista guardada del proyecto. Pocas líneas: va al contexto cada vez.
cat <<'EOF'
oficio: en cada cambio, el guantelete (aceptación como tests que fallan primero, CRAP <= 8, cero mutantes vivos,
forma sin regresiones, cero warnings en todas las plataformas). Nada es «hecho» sin la salida del comando que lo
demuestra. Toda decisión con un número medido. Lo último y mejor sin que haya que pedirlo. Contexto: leer por
rangos, salidas filtradas, procesos largos en segundo plano, TRASPASO.md tras cada commit verde. Detalle: skill oficio.
EOF
command -v xcrun >/dev/null 2>&1 || exit 0
raiz=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
sdk=$(xcrun --sdk macosx --show-sdk-path 2>/dev/null) || exit 0
lista=""
for f in "$raiz/.oficio/sdk-frameworks.txt" "$raiz/docs/sdk-frameworks.txt"; do [ -f "$f" ] && lista="$f" && break; done
version=$(xcrun --sdk macosx --show-sdk-version 2>/dev/null)
if [ -z "$lista" ]; then
  echo "oficio: SDK macOS $version sin lista guardada; guárdala con: mkdir -p .oficio && ls \"$sdk/System/Library/Frameworks\" | sed 's/.framework//' > .oficio/sdk-frameworks.txt"
  exit 0
fi
nuevos=$(ls "$sdk/System/Library/Frameworks" | sed 's/\.framework$//' | grep -vxF -f "$lista" | tr '\n' ' ')
[ -n "$nuevos" ] && echo "oficio: frameworks nuevos en el SDK $version frente a $(basename "$lista"): ${nuevos}— léelos antes de decidir y actualiza la lista."
exit 0

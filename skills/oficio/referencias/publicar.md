# Publicar: App Store, privacidad, compras y seguridad

Las normas de revisión y las listas de API cambian: **compruébalas en la documentación vigente de Apple** antes
de cada envío. Aquí va el método y lo que más se olvida.

## Privacidad

- **Manifiesto de privacidad** (`PrivacyInfo.xcprivacy`) en la app y en cada extensión: datos recogidos,
  seguimiento y API de «motivo requerido» que se usan (p. ej. `UserDefaults`, fechas de ficheros, espacio en
  disco), con su motivo. Los SDK de terceros traen el suyo.
- Las **etiquetas de privacidad** de App Store Connect tienen que coincidir con lo que hace la app. Sin
  analítica remota, «no se recogen datos» es una ventaja que se puede declarar.
- Las cadenas de permiso (`NS…UsageDescription`) explican para qué, en cada idioma.

## Revisión

- **La app está completa:** nada de pantallas de relleno, enlaces muertos ni funciones «próximamente».
- Si hay cuentas, **borrar la cuenta desde la app**.
- **Cumplimiento de exportación:** declara `ITSAppUsesNonExemptEncryption` en el `Info.plist`.
- Metadatos, capturas y descripción localizados en las mismas lenguas que la app.
- TestFlight antes de cada versión, con los dispositivos más viejos que soportes.

## Compras (StoreKit 2)

- Escucha `Transaction.updates` desde el arranque y termina (`finish()`) cada transacción verificada.
- Prueba con un fichero de configuración de StoreKit en Xcode y con el sandbox; los casos que hay que cubrir son
  reembolso, renovación, caducidad y compra pendiente.
- El estado de los derechos sale de `Transaction.currentEntitlements`, no de una bandera guardada.

## Seguridad

- **Los secretos, en el Llavero**, nunca en `UserDefaults` ni en el bundle.
- ATS activado; sin excepciones globales.
- Los datos sensibles con protección de ficheros adecuada, y fuera de las copias si no deben viajar.

## Créditos y licencias

- Cada recurso de terceros (modelos, fuentes, datos, código) se acredita en una pantalla de créditos, con un test
  que falle si se añade un recurso sin acreditar.
- La licencia de un modelo entrenado incluye la de sus datos y la de sus etiquetas.

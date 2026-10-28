# SelladoMX

Firma tus documentos PDF con tu e.firma del SAT desde tu computadora.

## Qué es

SelladoMX es un programa gratuito para Windows, macOS y Linux que firma PDFs con tu e.firma (tus archivos `.cer` y `.key`) y les agrega un sello de tiempo, que demuestra la fecha y hora en que firmaste.

- La firma es compatible con Adobe Reader y con los validadores oficiales.
- Tus documentos, tu certificado y tu contraseña nunca salen de tu computadora.
- Puedes firmar varios PDFs a la vez. Los firmados se guardan con el sufijo `_firmado.pdf`.
- El sello de tiempo básico es gratuito. El sello profesional (cumple la NOM-151-SCFI-2016 y la norma europea eIDAS) cuesta un crédito por documento; los créditos se compran en [www.selladomx.com](https://www.selladomx.com).

## Descargar e instalar en Windows

Necesitas Windows 10 u 11 de 64 bits. No se necesita ser administrador.

1. Descarga el instalador: [SelladoMX-Windows-Setup.exe](https://github.com/SelladoMX/app/releases/latest/download/SelladoMX-Windows-Setup.exe).
2. Ábrelo. Como SelladoMX todavía no tiene firma de código, Windows puede mostrar **"Windows protegió tu PC"**. Haz clic en **"Más información"** y después en **"Ejecutar de todas formas"**.
3. Sigue los pasos del instalador. Al terminar tendrás SelladoMX en el menú Inicio y, si dejas marcada la casilla, en el escritorio.

Para actualizar, descarga el instalador de la versión nueva y ábrelo; se instala encima de la anterior y tu configuración y tu token se conservan. Si SelladoMX está abierto, el instalador te pedirá cerrarlo.

**Windows 11 y el "Control inteligente de aplicaciones".** Si lo tienes activado, Windows puede bloquear el instalador sin darte la opción "Ejecutar de todas formas", porque SelladoMX todavía no tiene firma de código. La única forma de continuar es desactivarlo en *Seguridad de Windows → Control de aplicaciones y navegador → Configuración de Control inteligente de aplicaciones*. Ten en cuenta que, en algunas versiones de Windows, una vez desactivado ya no se puede volver a activar sin reinstalar Windows. Si prefieres no hacerlo, escríbenos.

**Antivirus.** Algunos antivirus revisan las conexiones seguras (opciones como "protección web", "análisis de HTTPS" o "inspección de tráfico cifrado") y pueden bloquear la conexión con los servidores de sello de tiempo. Si SelladoMX no logra obtener el sello de tiempo, agrega SelladoMX a las excepciones de esa función de tu antivirus.

## Si ya usabas la versión ZIP

Hasta la versión 0.4.2, SelladoMX para Windows se descargaba como ZIP.

1. Instala SelladoMX con el instalador, como se explica arriba.
2. Abre SelladoMX instalado una vez. Tu configuración y tu token siguen ahí, porque se guardan en tu usuario de Windows y no en la carpeta del ZIP.
3. Borra la carpeta donde descomprimiste el ZIP.

Desde ese momento, los enlaces que te enviamos por correo vuelven a abrir SelladoMX.

## macOS y Linux

**macOS:** descarga [SelladoMX-macOS.dmg](https://github.com/SelladoMX/app/releases/latest/download/SelladoMX-macOS.dmg), ábrelo y arrastra SelladoMX a la carpeta Aplicaciones. La primera vez que lo abras, macOS dirá que no puede verificar al desarrollador: haz clic derecho en SelladoMX → **Abrir** y confirma. En versiones recientes de macOS, ve a *Configuración del Sistema → Privacidad y seguridad* y haz clic en **"Abrir de todas formas"**.

**Linux:** descarga el archivo `SelladoMX-<versión>.flatpak` de la [página de descargas](https://github.com/SelladoMX/app/releases/latest) e instálalo:

```bash
flatpak install --user SelladoMX-<versión>.flatpak
flatpak run com.selladomx.SelladoMX
```

## Desinstalar

**Windows:** abre *Configuración → Aplicaciones → Aplicaciones instaladas*, busca SelladoMX y elige **Desinstalar**. Se te preguntará **"¿Eliminar también tu configuración y token?"**:

- **No** (recomendado si vas a volver a instalarlo): se conservan tu configuración y tu token.
- **Sí**: se borran.

En ambos casos se borran los registros de diagnóstico (logs). Tus PDFs y tus archivos `.cer` y `.key` nunca se borran.

**macOS:** arrastra SelladoMX de Aplicaciones a la papelera.

**Linux:** `flatpak uninstall com.selladomx.SelladoMX`

## Ayuda

- Correo: [soporte@selladomx.com](mailto:soporte@selladomx.com)
- Sitio web: [www.selladomx.com](https://www.selladomx.com)

Para reportar un problema de seguridad, consulta [SECURITY.md](SECURITY.md).

## Avanzado

### Verificar la descarga

Cada versión publica un archivo `SHA256SUMS.txt` con la huella de cada descarga, y una constancia de que los archivos se generaron en GitHub Actions a partir de este código.

En Windows (PowerShell), compara el resultado con la línea correspondiente de `SHA256SUMS.txt`:

```powershell
Get-FileHash SelladoMX-Windows-Setup.exe -Algorithm SHA256
```

En macOS o Linux, con `SHA256SUMS.txt` en la misma carpeta que la descarga:

```bash
sha256sum -c SHA256SUMS.txt --ignore-missing   # Linux
shasum -a 256 -c SHA256SUMS.txt --ignore-missing  # macOS
```

Para verificar el origen del archivo (requiere [GitHub CLI](https://cli.github.com)):

```bash
gh attestation verify SelladoMX-Windows-Setup.exe --repo SelladoMX/app
```

### Versión portable (solo 0.4.3)

La versión 0.4.3 también se publica como `SelladoMX-Windows.zip`, que se usa sin instalar. Es la última versión que se publica así.

### Desarrollo

La documentación para desarrolladores está en [docs/developer/](docs/developer/): [desarrollo](docs/developer/development.md), [arquitectura](docs/developer/architecture.md) y [empaquetado](docs/developer/packaging.md). Los enlaces `selladomx://` se describen en [docs/URL_SCHEME_REGISTRATION.md](docs/URL_SCHEME_REGISTRATION.md).

## Licencia

[MIT](LICENSE)

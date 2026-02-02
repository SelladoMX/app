# Troubleshooting

## Problemas de Certificados

### Error: "No se pudo cargar la clave privada"

1. Verifica que estés usando la contraseña correcta
2. Asegúrate de que el archivo .key corresponda al certificado .cer
3. Intenta convertir el formato usando los comandos de conversión
4. Verifica que el archivo no esté corrupto

### Error: "Contraseña incorrecta"

- La contraseña de la clave privada debe ser la que estableciste al obtener tu e.firma
- No es la misma contraseña que usas para el portal del SAT
- Verifica que no haya espacios al inicio o final de la contraseña

### Error: "Certificado expirado"

- Los certificados e.firma del SAT tienen vigencia de 4 años
- Necesitas renovar tu e.firma en el SAT
- Visita: https://www.sat.gob.mx/tramites/operacion/28753/obten-tu-certificado-de-e.firma

## Problemas de Firma

### La firma no se muestra en Adobe Reader

Asegúrate de que:
- El PDF original no estaba corrupto
- El proceso de firma se completó sin errores
- Estás usando una versión reciente de Adobe Reader

### Error: "No se pudo firmar el PDF"

- Verifica que el PDF no esté protegido con contraseña
- Asegúrate de que el PDF no esté dañado
- Verifica que tienes permisos de escritura en la carpeta de destino

## Problemas de TSA

### Error: "No se pudo conectar al TSA"

- Verifica tu conexión a Internet
- El servicio FreeTSA puede estar temporalmente no disponible
- Intenta nuevamente en unos minutos

### Error: "Timeout de TSA"

- Tu conexión a Internet puede ser lenta
- El servicio TSA está experimentando problemas
- Puedes ajustar el timeout en la configuración

## Problemas de Instalación

### macOS: "App is damaged and can't be opened"

Ejecuta en la terminal:

```bash
xattr -cr /Applications/SelladoMX.app
```

### Windows: SmartScreen bloquea la aplicación

1. Clic en "Más información"
2. Clic en "Ejecutar de todas formas"

### Linux: "error while loading shared libraries"

Instala las dependencias de Qt:

```bash
# Ubuntu/Debian
sudo apt-get install -y \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0

# Fedora
sudo dnf install \
    xcb-util-cursor \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    xcb-util-wm
```

## Problemas de Rendimiento

### La aplicación es lenta al iniciar

- Esto es normal en el primer inicio
- PyInstaller extrae archivos temporales
- Los siguientes inicios serán más rápidos

### La firma de múltiples PDFs es lenta

- La validación OCSP/CRL requiere conexión a Internet
- Cada PDF se firma secuencialmente
- El proceso puede tardar dependiendo del tamaño de los archivos

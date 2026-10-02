# Instalación y Uso

## Descarga

Descarga desde [GitHub Releases](https://github.com/SelladoMX/app/releases/latest):

- **macOS**: `SelladoMX-macOS.dmg`
- **Windows**: `SelladoMX-Windows.zip`
- **Linux**: `SelladoMX-<versión>.flatpak`

## Primera Ejecución

Como la aplicación no está firmada, verás advertencias de seguridad la primera vez:

**macOS:**
1. Clic derecho en SelladoMX.app
2. Seleccionar "Abrir"
3. Confirmar en el diálogo

**Windows:**
1. Clic en "Más información"
2. Clic en "Ejecutar de todas formas"

**Linux:**
```bash
flatpak install --user SelladoMX-<versión>.flatpak
flatpak run com.selladomx.SelladoMX
```

Para ejecutar desde el código fuente, consulta [docs/developer/development.md](../developer/development.md).

## Uso de la Aplicación

### Paso 1: Seleccionar PDFs

- Arrastra los PDFs a la ventana o haz clic en "Agregar PDFs..."

### Paso 2: Cargar Certificado

- Selecciona tu archivo `.cer` (certificado e.firma)
- Selecciona tu archivo `.key` (clave privada e.firma)
- Ingresa la contraseña de tu clave privada
- SelladoMX valida tu certificado; al terminar se activa el paso 3

### Paso 3: Firmar

- Opcional: activa "Usar protección mejorada" (TSA profesional, requiere token y créditos)
- Opcional: en "Guardar en:" elige otra carpeta de destino
- Haz clic en "Firmar N PDF(s)" y confirma

Los PDFs firmados se guardan con el sufijo `_firmado`, en la misma carpeta que los originales salvo que elijas otra.

## Verificación de Firmas

### Con Adobe Acrobat Reader

1. Abre el PDF firmado
2. Ve al panel de "Firmas" (menú lateral izquierdo)
3. Deberías ver la firma digital con estado válido

### Con pyhanko (línea de comandos)

```bash
pyhanko sign validate archivo_firmado.pdf
```

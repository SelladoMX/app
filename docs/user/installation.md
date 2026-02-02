# Instalación y Uso

## Descarga del Ejecutable

Para usuarios que solo desean utilizar la aplicación:

- **macOS**: [SelladoMX-macOS.dmg](https://github.com/tu-usuario/selladomx/releases/latest) (Intel y Apple Silicon)
- **Windows**: [SelladoMX-Windows.zip](https://github.com/tu-usuario/selladomx/releases/latest) (Windows 10+)
- **Linux**: [SelladoMX-Linux.tar.gz](https://github.com/tu-usuario/selladomx/releases/latest) (Ubuntu, Fedora, Arch)

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
chmod +x SelladoMX
./SelladoMX
```

## Instalación para Desarrollo

### Requisitos

- Python ≥ 3.11, < 3.14
- Poetry (gestor de dependencias)

### Instalar Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Instalar Dependencias

```bash
cd /ruta/al/proyecto/client
poetry install
```

### Ejecutar desde Código Fuente

```bash
poetry run selladomx
```

O en modo desarrollo:

```bash
poetry shell
python -m selladomx.main
```

## Uso de la Aplicación

SelladoMX te guía a través de un flujo de 3 pasos:

### Paso 1: Seleccionar PDFs

- Haz clic en "Agregar PDFs..."
- Selecciona los archivos a firmar
- Una vez agregados, el paso 1 se marca como completado y se activa el paso 2

### Paso 2: Cargar Certificado

- Selecciona tu archivo `.cer` (certificado e.firma)
- Selecciona tu archivo `.key` (clave privada e.firma)
- Ingresa la contraseña de tu clave privada
- El sistema valida automáticamente tu certificado
- Una vez validado, el paso 2 se marca como completado y se activa el paso 3

### Paso 3: Firmar

- Haz clic en "Firmar PDFs"
- Observa el progreso en tiempo real
- Revisa el log de actividad

Los PDFs firmados se guardarán con el sufijo `_firmado` en la misma carpeta que los originales.

## Verificación de Firmas

### Con pyhanko (línea de comandos)

```bash
poetry run pyhanko sign validate archivo_firmado.pdf
```

### Con Adobe Acrobat Reader

1. Abre el PDF firmado
2. Ve al panel de "Firmas" (menú lateral izquierdo)
3. Deberías ver la firma digital con estado válido

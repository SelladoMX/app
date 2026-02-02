# Guía de Empaquetado

Esta guía explica cómo crear ejecutables de SelladoMX para macOS, Windows y Linux.

## Quick Start

### macOS

```bash
# Compilar
make build
# O también: ./scripts/build.sh

# Crear DMG instalador
make dmg
# O también: ./scripts/create-dmg.sh

# Probar
open dist/SelladoMX.app
```

### Windows

```powershell
# Instalar dependencias
poetry install --with dev

# Compilar
poetry run pyinstaller selladomx.spec

# Probar
.\dist\SelladoMX\SelladoMX.exe
```

### Linux

```bash
# Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt-get install -y \
    python3-dev \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0

# Compilar
make build
# O también: ./scripts/build.sh

# Crear tarball
tar -czf SelladoMX-Linux.tar.gz -C dist SelladoMX

# Probar
./dist/SelladoMX/SelladoMX
```

## GitHub Actions (CI/CD)

La forma más fácil es usar GitHub Actions para compilar automáticamente en las 3 plataformas.

### Trigger con Tag de Versión

```bash
# Crear y publicar un tag
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions compilará automáticamente y creará un Release con:
- `SelladoMX-Linux.tar.gz`
- `SelladoMX-Windows.zip`
- `SelladoMX-macOS.dmg`

### Trigger Manual

1. Ve a tu repositorio en GitHub
2. Actions → Build Executables → Run workflow
3. Espera a que termine (15-20 minutos)
4. Descarga los artifacts

## Build Local Detallado

### Requisitos por Plataforma

**macOS:**
- macOS 10.13+
- Python 3.11-3.13
- Poetry

**Windows:**
- Windows 10+
- Python 3.11-3.13
- Poetry

**Linux:**
- Python 3.11-3.13
- Poetry
- Dependencias de Qt (ver arriba)

### Proceso de Build

El script `scripts/build.sh` (o `make build`) realiza automáticamente:

1. Instalación de dependencias con Poetry
2. Limpieza de builds anteriores
3. Compilación con PyInstaller
4. Creación del bundle para macOS o directorio para Windows/Linux

## Distribución sin Firma

### macOS

Los usuarios verán un mensaje de seguridad la primera vez:

```
"SelladoMX.app" no se puede abrir porque el desarrollador no se puede verificar.
```

Solución para usuarios:
1. Clic derecho en SelladoMX.app
2. Seleccionar "Abrir"
3. Confirmar en el diálogo
4. Las siguientes veces abrirá normalmente

### Windows

Windows SmartScreen mostrará:

```
Windows protegió tu PC
Microsoft Defender SmartScreen impidió el inicio de una aplicación desconocida
```

Solución para usuarios:
1. Clic en "Más información"
2. Clic en "Ejecutar de todas formas"

Con el tiempo, a medida que más usuarios descarguen, SmartScreen dejará de mostrar el mensaje.

## Optimización

### Tamaño de los Ejecutables

Tamaños aproximados:
- **macOS**: 180-220 MB (.app) / 80-100 MB (.dmg comprimido)
- **Windows**: 150-180 MB (carpeta) / 60-80 MB (.zip comprimido)
- **Linux**: 160-200 MB (carpeta) / 70-90 MB (.tar.gz comprimido)

El tamaño es grande debido a:
- Qt6 (PySide6)
- Python runtime
- Bibliotecas de criptografía
- pyhanko y dependencias

### Usar UPX

Para reducir el tamaño del ejecutable:

```bash
# Instalar UPX
# macOS:
brew install upx

# Linux:
sudo apt-get install upx-ucl

# Windows:
# Descargar de https://upx.github.io/
```

UPX ya está habilitado en `selladomx.spec`.

### Excluir Módulos Innecesarios

En `selladomx.spec`, ya excluimos:
- matplotlib
- numpy
- pandas
- scipy

## Firma de Código

### macOS (con Apple Developer Account)

```bash
# 1. Firmar
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Tu Nombre (TEAM_ID)" \
  dist/SelladoMX.app

# 2. Notarizar (enviar a Apple)
xcrun notarytool submit dist/SelladoMX-macOS.dmg \
  --apple-id "tu@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

# 3. Staple (adjuntar ticket de notarización)
xcrun stapler staple dist/SelladoMX.app
```

Costo: $99/año Apple Developer Program

### Windows (con certificado de código)

```powershell
# Usando signtool.exe
signtool sign /f certificado.pfx /p password /t http://timestamp.digicert.com dist\SelladoMX\SelladoMX.exe
```

### Alternativa: Sigstore (gratis)

Ya configurado en `.github/workflows/build.yml` - se firma automáticamente al crear releases.

## Distribución

### GitHub Releases (Recomendado)

```bash
# 1. Crear tag
git tag v0.1.0

# 2. Push tag (trigger automático)
git push origin v0.1.0

# 3. GitHub Actions compila y crea Release
# Los usuarios descargan de: github.com/tu-usuario/selladomx/releases
```

### Sitio Web

Sube los archivos a tu hosting y provee links de descarga:

```
https://tu-sitio.com/downloads/
├── SelladoMX-macOS.dmg
├── SelladoMX-Windows.zip
└── SelladoMX-Linux.tar.gz
```

### Gestores de Paquetes

**Homebrew (macOS):**

```ruby
cask "selladomx" do
  version "0.1.0"
  url "https://github.com/tu-usuario/selladomx/releases/download/v#{version}/SelladoMX-macOS.dmg"
  sha256 "hash-del-dmg"

  app "SelladoMX.app"
end
```

**Chocolatey (Windows):**
```powershell
choco install selladomx
```

## Troubleshooting

### macOS: "App is damaged and can't be opened"

```bash
xattr -cr /Applications/SelladoMX.app
```

### Windows: Antivirus detecta como malware

PyInstaller es común en malware, genera falsos positivos.

Soluciones:
1. Firma el ejecutable (reduce detecciones)
2. Reporta falso positivo a proveedores de antivirus
3. Distribuye también el código fuente

### Linux: "error while loading shared libraries"

```bash
# Ver dependencias faltantes
ldd dist/SelladoMX/SelladoMX

# Instalar dependencias de Qt
sudo apt-get install libxcb-*
```

## Testing Pre-Release

Antes de distribuir, prueba en máquinas limpias:

**macOS:**
- Prueba en Mac sin Xcode/Homebrew
- Prueba en diferentes versiones (10.13+)

**Windows:**
- Prueba en Windows 10 y 11
- Prueba en cuenta sin privilegios de administrador

**Linux:**
- Prueba en Ubuntu, Fedora, Arch
- Prueba con diferentes escritorios (GNOME, KDE, XFCE)

## Checklist de Release

- [ ] Actualizar versión en `pyproject.toml` y `__init__.py`
- [ ] Crear tag con `git tag vX.Y.Z`
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Esperar a que GitHub Actions termine
- [ ] Verificar que el Release se creó en GitHub
- [ ] Descargar y probar cada ejecutable
- [ ] Actualizar README con instrucciones de descarga

## Recursos

- [PyInstaller Docs](https://pyinstaller.org/)
- [create-dmg](https://github.com/create-dmg/create-dmg)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Apple Code Signing](https://developer.apple.com/support/code-signing/)
- [Sigstore (free code signing)](https://www.sigstore.dev/)

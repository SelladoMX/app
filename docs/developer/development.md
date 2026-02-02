# Guía de Desarrollo

## Setup del Entorno

### Requisitos

- Python ≥ 3.11, < 3.14
- Poetry (gestor de dependencias)

### Instalar Dependencias

```bash
cd /ruta/al/proyecto/client
poetry install --with dev
```

## Ejecutar desde Código Fuente

### Modo Normal

```bash
poetry run selladomx
```

### Modo Desarrollo (con shell)

```bash
poetry shell
python -m selladomx.main
```

## Testing

### Ejecutar todos los tests

```bash
poetry run pytest -v
```

### Ejecutar test específico

```bash
poetry run pytest tests/test_certificate_validator.py -v
```


## Formateo de Código

```bash
# Formatear con black
poetry run black src/

# Verificar sin modificar
poetry run black --check src/
```

## Gestión de Dependencias

```bash
# Agregar dependencia
poetry add nombre-paquete

# Agregar dependencia de desarrollo
poetry add --group dev nombre-paquete

# Actualizar dependencias
poetry update

# Ver dependencias instaladas
poetry show
```

## Testing del Onboarding

El onboarding solo aparece en la primera ejecución. Para testearlo:

### Método 1: Script Rápido

```bash
make reset-onboarding
poetry run selladomx
# O también:
poetry run python scripts/reset_onboarding.py
poetry run selladomx
```

### Método 2: Comando Directo

```bash
poetry run python -c "from selladomx.utils.settings_manager import SettingsManager; SettingsManager().reset_onboarding()"
poetry run selladomx
```

### Método 3: Borrar Archivo Manualmente

```bash
# macOS
rm ~/Library/Preferences/mx.sellado.SelladoMX.plist

# Linux
rm ~/.config/SelladoMX/SelladoMX.conf

# Windows
# Usar regedit para eliminar: HKEY_CURRENT_USER\Software\SelladoMX\SelladoMX
```

## Building y Empaquetado

### Build Local

```bash
# Compilar aplicación (limpia automáticamente)
make build
# O también:
./scripts/build.sh
```

Resultado:
- **macOS**: `dist/SelladoMX.app`
- **Windows**: `dist/SelladoMX/SelladoMX.exe`
- **Linux**: `dist/SelladoMX/SelladoMX`

### Crear DMG para macOS

```bash
make dmg
# O también:
./scripts/create-dmg.sh
```

Genera: `dist/SelladoMX-macOS.dmg`

### Limpieza de Cache

Si el build no refleja tus cambios:

```bash
make clean    # Limpia todos los caches
make build    # Construye desde cero
# O también:
./scripts/clean.sh
./scripts/build.sh
```

El script `scripts/clean.sh` elimina:
- Directorios `build/` y `dist/`
- Cache de Python (`__pycache__`, `*.pyc`)
- Cache de PyInstaller (`~/.pyinstaller_cache`)
- Cache de pytest (`.pytest_cache`)

## Configuración

La configuración de la aplicación está en `src/selladomx/config.py`:

```python
# TSA (Time Stamp Authority)
TSA_URL = "https://freetsa.org/tsr"
TSA_TIMEOUT = 30

# Validación de certificados
OCSP_TIMEOUT = 10
CRL_TIMEOUT = 10
ENABLE_CRL_FALLBACK = True

# Firma
SIGNED_SUFFIX = "_firmado"
```

## Estructura de Archivos de Configuración

```
# Python cache
src/selladomx/__pycache__/
tests/__pycache__/

# PyInstaller cache
build/
dist/
~/.pyinstaller_cache/

# Pytest cache
.pytest_cache/

# QSettings (persistencia del app)
~/Library/Preferences/mx.sellado.SelladoMX.plist  # macOS
~/.config/SelladoMX/SelladoMX.conf                # Linux
HKEY_CURRENT_USER\Software\SelladoMX\SelladoMX   # Windows
```

## Comandos Útiles

Usa el Makefile para comandos comunes:

```bash
make help              # Ver todos los comandos disponibles
make install           # Instalar dependencias con Poetry
make run               # Ejecutar la aplicación
make test              # Ejecutar tests con pytest
make clean             # Limpiar builds y cache
make build             # Compilar ejecutable
make dmg               # Crear DMG (solo macOS)
make reset-onboarding  # Resetear estado de onboarding
```

## Scripts Útiles

| Script | Propósito | Comando |
|--------|-----------|---------|
| `scripts/reset_onboarding.py` | Resetear onboarding | `make reset-onboarding` |
| `scripts/clean.sh` | Limpiar caches y builds | `make clean` |
| `scripts/build.sh` | Construir ejecutable | `make build` |
| `scripts/create-dmg.sh` | Crear instalador DMG | `make dmg` |

## Flujo de Desarrollo Recomendado

```bash
# 1. Hacer cambios en el código
vim src/selladomx/ui/...

# 2. Probar en modo desarrollo (hot-reload)
poetry run selladomx

# 3. Ejecutar tests
make test

# 4. Si todo bien, construir
make build

# 5. Probar el build
open dist/SelladoMX.app    # macOS
./dist/SelladoMX/SelladoMX # Linux
dist\SelladoMX\SelladoMX.exe # Windows
```

## Comandos Rápidos

```bash
# Desarrollo rápido
make run

# Test rápido
make test

# Reset onboarding rápido
make reset-onboarding

# Build fresco
make clean && make build

# Todo en uno: limpiar, test, build
make clean && make test && make build
```

## Troubleshooting

### El Build Sigue Mostrando Versión Antigua

```bash
# Limpieza profunda
make clean

# Reinstala dependencias (solo si es necesario)
rm -rf .venv
poetry install

# Build desde cero
make build

# Verifica la fecha del ejecutable
ls -la dist/SelladoMX.app/Contents/MacOS/SelladoMX
```

### Error al Ejecutar el Build en macOS

```bash
# Dar permisos
xattr -cr dist/SelladoMX.app

# O usar clic derecho -> Open
```

### Error: "Cannot find Qt platform plugin"

Asegúrate de que PySide6 esté en hiddenimports en `selladomx.spec`.

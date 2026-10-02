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
```

### Método 2: Borrar Archivo Manualmente

```bash
# macOS
rm ~/Library/Preferences/com.selladomx.SelladoMX.plist

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
```

Resultado:
- **macOS**: `dist/SelladoMX.app`
- **Windows**: `dist/selladomx/selladomx.exe`
- **Linux**: `dist/selladomx/selladomx`

### Crear DMG para macOS

```bash
make dmg
```

Genera: `dist/SelladoMX-macOS.dmg`

### Limpieza de Cache

`make clean` elimina `build/`, `dist/` y los caches de Python, PyInstaller y pytest.

## Configuración

Constantes y variables de entorno: `src/selladomx/config.py`.

`make help` lista todos los comandos.

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
xattr -cr dist/SelladoMX.app

# O usar clic derecho -> Open
```

### Error: "Cannot find Qt platform plugin"

Asegúrate de que PySide6 esté en hiddenimports en `selladomx.spec`.

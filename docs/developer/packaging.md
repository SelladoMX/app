# Guía de Empaquetado

macOS y Windows se empaquetan con PyInstaller (`selladomx.spec`); Linux se distribuye como Flatpak (`com.selladomx.SelladoMX.yml`).

## macOS

```bash
make build        # dist/SelladoMX.app
make dmg          # dist/SelladoMX-macOS.dmg
open dist/SelladoMX.app
```

## Windows

```powershell
poetry install --with dev
poetry run pyinstaller selladomx.spec
.\dist\selladomx\selladomx.exe
```

El exe no se comprime con UPX y lleva un recurso de versión (empresa, producto y versión tomada de `__version__`), porque los antivirus desconfían más de un exe sin firma que además no lo tiene.

### Instalador (Inno Setup 6)

`installer/selladomx.iss` empaqueta `dist/selladomx/` en `dist/SelladoMX-Windows-Setup.exe`. Desde la raíz del repo, después del build de PyInstaller:

```powershell
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" /DAppVersion=0.4.3 installer\selladomx.iss
```

- Instalación por usuario, sin administrador (`PrivilegesRequired=lowest`), en `%LOCALAPPDATA%\Programs\SelladoMX`. x64, Windows 10 o posterior.
- `AppId` es `{4285FAC5-53B6-436F-89B4-A58266D49505}`. No debe cambiar nunca: las actualizaciones y la desinstalación encuentran la instalación por él, y `platform_helpers.py` lee `InstallLocation` de `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{AppId}_is1`.
- Accesos directos en el menú Inicio y en el escritorio (casilla marcada por defecto).
- Registra `selladomx://` en `HKCU\Software\Classes\selladomx` y lo borra al desinstalar.
- Al actualizar borra `{app}\_internal` antes de copiar, para que no queden DLLs ni plugins de Qt de builds anteriores.
- La app crea el mutex `SelladoMXAppMutex` mientras corre; el instalador y el desinstalador lo usan para detectar que está abierta (`AppMutex`), y `CloseApplications=yes` ofrece cerrarla.
- El desinstalador pregunta "¿Eliminar también tu configuración y token?" (por defecto "No"). Con "Sí" borra `HKCU\Software\SelladoMX`, donde vive `QSettings("SelladoMX", "SelladoMX")`. Siempre borra `%LOCALAPPDATA%\SelladoMX\logs` y la caché de QML de Qt, y luego `%LOCALAPPDATA%\SelladoMX` si quedó vacía.

Con la app instalada, la copia instalada siempre toma el handler de `selladomx://`; una copia portable solo lo toma si el exe registrado ya no existe (`should_update_url_handler()` en `platform_helpers.py`).

### Zip portable (solo 0.4.3)

CI copia `assets/README-Windows.txt` como `dist/selladomx/README.txt` y comprime `dist/selladomx/` en `SelladoMX-Windows.zip`. Se publica por última vez en 0.4.3 y se elimina en 0.4.4.

## Linux (Flatpak)

Runtime: `org.kde.Platform//6.11` / `org.kde.Sdk//6.11` (Freedesktop 25.08, Python 3.13). PySide6 no usa el Qt del runtime: el wheel trae su propio Qt. El build es offline: las dependencias y el wheel de la app deben estar en `flatpak-python-deps/`, y `requirements.txt` debe existir en la raíz (ambos se generan a partir de `poetry.lock`, igual que en CI):

```bash
poetry self add "poetry-plugin-export==1.10.1"
poetry export -f requirements.txt --output requirements.txt
mkdir -p flatpak-python-deps
# Con Python 3.13, la versión del runtime; pip elige los wheels para ella
pip download --require-hashes --only-binary=:all: -r requirements.txt -d flatpak-python-deps
poetry build && cp dist/*.whl flatpak-python-deps/

flatpak install -y flathub org.kde.Platform//6.11 org.kde.Sdk//6.11
flatpak-builder --force-clean --repo=repo build-dir com.selladomx.SelladoMX.yml
flatpak build-bundle repo SelladoMX-dev.flatpak com.selladomx.SelladoMX \
  --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo
```

`make build` en Linux genera `dist/selladomx/`, pero ese build no se distribuye.

### Permisos

- `--filesystem=home`: la app guarda `<nombre>_firmado.pdf` junto a cada original, así que necesita escribir en la carpeta del PDF. Con el portal de documentos, un archivo elegido llega sin su carpeta y esa escritura falla. Pasar a un diseño solo con portales obligaría a elegir siempre una carpeta de destino (o un diálogo de guardar por archivo), un cambio de flujo que no se puede probar en CI. Mientras el destino por omisión sea junto al original, se mantiene el acceso a home.
- Un PDF fuera de home (por ejemplo, una USB en `/run/media`) llega por el portal de documentos, en una carpeta que no es la del original, así que la copia firmada no queda junto a él: para esos archivos hay que elegir una carpeta de destino dentro de home.
- Sin `--socket=session-bus`: los diálogos de archivos, abrir enlaces y el tema claro/oscuro usan `org.freedesktop.portal.Desktop`, que el bus filtrado de Flatpak permite. `org.freedesktop.portal.OpenURI` es una interfaz de ese servicio, no un nombre de bus, así que no se declara.

## GitHub Actions

`.github/workflows/build.yml` se ejecuta al publicar un tag `v*` o manualmente (Actions → Build Executables → Run workflow). Corre los tests sin red (`-m "not network"`) en Linux y en Windows; si alguno falla no se genera nada. Después genera:

- `SelladoMX-Windows-Setup.exe` (instalador; ISCC recibe `/DAppVersion` del tag, o de `__version__` en ejecuciones manuales; en tags el job falla si no coinciden)
- `SelladoMX-Windows.zip` (portable, solo 0.4.3)
- `SelladoMX-macOS.dmg`
- `SelladoMX-<versión>.flatpak` (`SelladoMX-dev.flatpak` en ejecuciones manuales)
- `SHA256SUMS.txt`

Cada artefacto lleva una attestation de procedencia (Sigstore). En tags, todo se sube al GitHub Release; una ejecución manual solo deja los artefactos en la ejecución de Actions. Los nombres de Windows y macOS no llevan versión, para que funcionen los enlaces `releases/latest/download/<archivo>` del sitio web.

Los tests que usan TSAs reales (`-m network`) corren en un job aparte (`network-tests`) que no bloquea el build. La versión de Poetry está fijada en `POETRY_VERSION` y las actions de terceros están fijadas por SHA de commit; `requirements.txt` del Flatpak lleva hashes, que `pip` verifica al descargar y al instalar dentro del build.

## Distribución sin Firma

Los ejecutables no están firmados con certificado de código.

**macOS**: "SelladoMX.app no se puede abrir porque el desarrollador no se puede verificar". Clic derecho en SelladoMX.app → "Abrir" → confirmar. Si dice "App is damaged and can't be opened":

```bash
xattr -cr /Applications/SelladoMX.app
```

**Windows**: SmartScreen muestra "Windows protegió tu PC" al abrir el instalador. Clic en "Más información" → "Ejecutar de todas formas". El Control inteligente de aplicaciones de Windows 11 puede bloquearlo sin ofrecer esa opción. Algunos antivirus marcan ejecutables de PyInstaller como falsos positivos.

## Checklist de Release

- [ ] Actualizar versión en `pyproject.toml` y `src/selladomx/__init__.py` (`selladomx.spec` toma de `__init__.py` `CFBundleVersion`/`CFBundleShortVersionString` y el recurso de versión del exe de Windows; CI pasa la versión al instalador)
- [ ] Agregar `<release version="X.Y.Z" date="AAAA-MM-DD">` al inicio de `<releases>` en `com.selladomx.SelladoMX.metainfo.xml`, con una descripción breve en español
- [ ] `poetry run pytest -m "not network"`: `tests/test_version_consistency.py` falla si alguna versión no coincide
- [ ] `git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Verificar el Release en GitHub y probar cada artefacto. En Windows: instalar encima de la versión anterior con la app abierta, abrir un enlace `selladomx://` y desinstalar

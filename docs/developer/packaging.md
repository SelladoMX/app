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

CI copia `assets/README-Windows.txt` como `dist/selladomx/README.txt` y comprime `dist/selladomx/` en `SelladoMX-Windows.zip`.

## Linux (Flatpak)

Runtime: `org.kde.Platform//6.9` / `org.kde.Sdk//6.9`. El build es offline: las dependencias y el wheel de la app deben estar en `flatpak-python-deps/`, y `requirements.txt` debe existir en la raíz (ambos se generan a partir de `poetry.lock`, igual que en CI):

```bash
poetry self add "poetry-plugin-export==1.10.1"
poetry export -f requirements.txt --output requirements.txt
mkdir -p flatpak-python-deps
pip download --require-hashes -r requirements.txt -d flatpak-python-deps
poetry build && cp dist/*.whl flatpak-python-deps/

flatpak install -y flathub org.kde.Platform//6.9 org.kde.Sdk//6.9
flatpak-builder --force-clean --repo=repo build-dir com.selladomx.SelladoMX.yml
flatpak build-bundle repo SelladoMX-dev.flatpak com.selladomx.SelladoMX \
  --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo
```

`make build` en Linux genera `dist/selladomx/`, pero ese build no se distribuye.

## GitHub Actions

`.github/workflows/build.yml` se ejecuta al publicar un tag `v*` o manualmente (Actions → Build Executables → Run workflow). Corre los tests sin red (`-m "not network"`) y después genera:

- `SelladoMX-Windows.zip`
- `SelladoMX-macOS.dmg`
- `SelladoMX-<versión>.flatpak` (`SelladoMX-dev.flatpak` en ejecuciones manuales)
- `SHA256SUMS.txt`

Cada artefacto lleva una attestation de procedencia (Sigstore). En tags, todo se sube al GitHub Release.

Los tests que usan TSAs reales (`-m network`) corren en un job aparte (`network-tests`) que no bloquea el build. La versión de Poetry está fijada en `POETRY_VERSION` y las actions de terceros están fijadas por SHA de commit; `requirements.txt` del Flatpak lleva hashes, que `pip` verifica al descargar y al instalar dentro del build.

## Distribución sin Firma

Los ejecutables no están firmados con certificado de código.

**macOS**: "SelladoMX.app no se puede abrir porque el desarrollador no se puede verificar". Clic derecho en SelladoMX.app → "Abrir" → confirmar. Si dice "App is damaged and can't be opened":

```bash
xattr -cr /Applications/SelladoMX.app
```

**Windows**: SmartScreen muestra "Windows protegió tu PC". Clic en "Más información" → "Ejecutar de todas formas". Algunos antivirus marcan ejecutables de PyInstaller como falsos positivos.

## Checklist de Release

- [ ] Actualizar versión en `pyproject.toml` y `src/selladomx/__init__.py` (`selladomx.spec` toma `CFBundleVersion`/`CFBundleShortVersionString` de `__init__.py`)
- [ ] Agregar `<release version="X.Y.Z" date="AAAA-MM-DD">` al inicio de `<releases>` en `com.selladomx.SelladoMX.metainfo.xml`, con una descripción breve en español
- [ ] `poetry run pytest -m "not network"`: `tests/test_version_consistency.py` falla si alguna versión no coincide
- [ ] `git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Verificar el Release en GitHub y probar cada artefacto
